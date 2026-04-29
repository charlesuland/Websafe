from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from app.dependencies import get_db, get_current_user, get_s3_client, s3_base_url, upload_image_to_s3
from app.models import (
    Project,
    ProjectPage,
    Vendor, 
    DraftProjectPage,
    MediaObjectMetadata,
    ProjectProduct,
    ProductImage
)
from app.utils import slugify
from fastapi import Depends
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid as UUID
import base64
import mimetypes
import copy
from pathlib import Path
from sqlmodel import select
from sqlalchemy import update
from urllib.parse import quote

projects_router = APIRouter(prefix="/projects", tags=["projects"])
public_router = APIRouter(prefix="/site", tags=["public"])


class DraftPageIn(BaseModel):
    name: str
    layout: list

class DraftSaveRequest(BaseModel):
    pages: List[Dict[str, Any]]
    preview: Optional[str] = None

class ProjectIn(BaseModel):
    name: str

class SlugUpdate(BaseModel):
    slug: str


def build_media_proxy_url(file_key: str) -> str:
    return f"/api/site/_media?file_key={quote(file_key, safe='')}"


def normalize_media_url(url: Any) -> Any:
    if not isinstance(url, str) or not url:
        return url

    if url.startswith("/api/site/_media?file_key="):
        return url

    if url.startswith("/api/projects/media?file_key="):
        file_key = url.split("file_key=", 1)[1]
        return f"/api/site/_media?file_key={file_key}"

    if url.startswith(s3_base_url):
        file_key = url[len(s3_base_url):]
        return build_media_proxy_url(file_key)

    return url


def normalize_layout_media(layout: list[dict]) -> list[dict]:
    normalized = copy.deepcopy(layout)

    for component in normalized:
        props = component.get("props")
        if not isinstance(props, dict):
            continue

        if "src" in props:
            props["src"] = normalize_media_url(props["src"])

        if "imageUrl" in props:
            props["imageUrl"] = normalize_media_url(props["imageUrl"])

    return normalized

@projects_router.get("/")
async def get_projects(db=Depends(get_db), user=Depends(get_current_user)):
    vendors = db.execute(
        select(Vendor).where(Vendor.owner == user.id)
    ).scalars().all()

    if not vendors:
        return []

    vendor_ids = [v.id for v in vendors]

    projects = db.execute(
        select(Project).where(Project.vendor.in_(vendor_ids))
    ).scalars().all()

    projects_data = []
    for p in projects:
        preview_url = None
        if p.preview_image:
            metadata = db.get(MediaObjectMetadata, p.preview_image)
            if metadata:
                preview_url = f"{s3_base_url}{metadata.file_key}"

        projects_data.append({
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "is_live": p.is_live,
            "last_updated": p.updated_at,
            "last_published": p.last_published,
            "preview_image": preview_url
        })

    return projects_data

@projects_router.post("/create")
async def create_project(projectIn: ProjectIn, db=Depends(get_db), user=Depends(get_current_user)):
    project_name = projectIn.name

    vendor = db.execute(
        select(Vendor).where(Vendor.owner == user.id)
    ).scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=400, detail="User has no vendor")

    project = Project(
        name=project_name,
        vendor=vendor.id,
        is_live=False
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    draft_page = DraftProjectPage(project=project.id, name="Home", layout=[])

    db.add(draft_page)
    db.commit()

    return {
        "id": project.id,
        "name": project.name,
        "slug": project.slug,
        "is_live": project.is_live,
        "last_published": project.last_published
    }

@projects_router.delete("/{project_id}/delete")
async def delete_project(project_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(404)
    
    vendor = db.get(Vendor, project.vendor)

    if vendor.owner != user.id:
        raise HTTPException(403)
    

    db.execute(DraftProjectPage.__table__.delete().where(DraftProjectPage.project == project_id))
    db.execute(ProjectPage.__table__.delete().where(ProjectPage.project_id == project_id))
    db.execute(ProjectProduct.__table__.delete().where(ProjectProduct.project_id == project_id))

    db.delete(project)
    db.commit()

    return {"status": "deleted"}

@projects_router.get("/{project_id}")
async def get_project(project_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(404)

    vendor = db.get(Vendor, project.vendor)

    if vendor.owner != user.id:
        raise HTTPException(403)

    return project


@projects_router.get("/{project_id}/pages")
async def get_project_pages(project_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(404)

    vendor = db.get(Vendor, project.vendor)

    if vendor.owner != user.id:
        raise HTTPException(403)

    pages = db.execute(
        select(ProjectPage).where(ProjectPage.project_id == project_id)
    ).scalars().all()

    return [{"name": page.name} for page in pages]


@projects_router.get("/{project_id}/get-draft-pages")
async def get_draft_pages(project_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(404)

    vendor = db.get(Vendor, project.vendor)
    if vendor.owner != user.id:
        raise HTTPException(403)

    pages = db.execute(
        select(DraftProjectPage).where(DraftProjectPage.project == project_id)
    ).scalars().all()

    return [
        {
            "name": p.name,
            "layout": normalize_layout_media(p.layout)
        }
        for p in pages
    ]


@projects_router.post("/{project_id}/publish")
async def publish_project(project_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(404)

    vendor = db.get(Vendor, project.vendor)
    if vendor.owner != user.id:
        raise HTTPException(403)

    # Block publish if no slug has been set yet
    if not project.slug:
        raise HTTPException(
            status_code=400,
            detail="Set a custom URL for your store before publishing"
        )

    db.execute(
        ProjectPage.__table__.delete().where(ProjectPage.project_id == project_id)
    )

    drafts = db.execute(
        select(DraftProjectPage).where(DraftProjectPage.project == project_id)
    ).scalars().all()

    for d in drafts:
        page = ProjectPage(
            project_id=project_id,
            name=d.name,
            layout=normalize_layout_media(d.layout)
        )
        db.add(page)

    db.execute(
        update(ProjectProduct)
        .where(ProjectProduct.project_id == project_id)
        .values(is_published=False)
    )
    db.execute(
        update(ProjectProduct)
        .where(ProjectProduct.project_id == project_id)
        .where(ProjectProduct.is_active == True)
        .values(is_published=True)
    )

    project.is_live = True
    project.last_published = datetime.utcnow()

    db.commit()

    return {"status": "published", "url": f"/site/{project.slug}"}


@projects_router.post("/{project_id}/save-draft")
async def save_draft_pages(
    project_id: int,
    data: DraftSaveRequest,
    db=Depends(get_db),
    user=Depends(get_current_user),
    s3=Depends(get_s3_client)
):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(404)

    vendor = db.get(Vendor, project.vendor)
    if vendor.owner != user.id:
        raise HTTPException(403)

    db.execute(
        DraftProjectPage.__table__.delete().where(
            DraftProjectPage.project == project_id
        )
    )

    for page in data.pages:
        db.add(
            DraftProjectPage(
                project=project_id,
                name=page["name"],
                layout=page["layout"]
            )
        )

    if data.preview:
        try:
            previous_metadata = project.preview

            header, encoded = data.preview.split(",", 1)
            mime_type = header.split(":")[1].split(";")[0]

            if previous_metadata:
                file_key = previous_metadata.file_key

            else:
                ext = mimetypes.guess_extension(mime_type) or ".png"
                file_id = str(UUID.uuid4())
                file_key=f"projects/{project_id}/preview/{file_id}{ext}"

            file_bytes = base64.b64decode(encoded)
            file_size = len(file_bytes)

            new_metadata = MediaObjectMetadata(
                    project_id=project_id,
                    file_key=file_key,
                    file_type=mime_type,
                    file_size_bytes=file_size,
                    alt_text=f"Preview image for project {project_id}"
                )

            db.add(new_metadata)
            db.flush()
            
            project.preview_image = new_metadata.id

            # Upload to S3 using the reusable function
            await upload_image_to_s3(file_bytes, file_key, mime_type, s3)

        except Exception as e:
            raise HTTPException(400, f"Invalid preview image: {str(e)}")
    
    project.last_updated = datetime.utcnow()

    db.commit()

    return {"status": "saved"}


# ---------------------------------------------------------------
# Slug endpoints
# ---------------------------------------------------------------

@projects_router.get("/{project_id}/slug")
async def get_project_slug(project_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    vendor = db.execute(
        select(Vendor).where(Vendor.owner == user.id)
    ).scalar_one_or_none()

    if not vendor or project.vendor != vendor.id:
        raise HTTPException(status_code=403, detail="Not your project")

    return {
        "slug": project.slug,
        "url": f"/site/{project.slug}" if project.slug else None
    }


@projects_router.put("/{project_id}/slug")
async def set_project_slug(project_id: int, body: SlugUpdate, db=Depends(get_db), user=Depends(get_current_user)):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    vendor = db.execute(
        select(Vendor).where(Vendor.owner == user.id)
    ).scalar_one_or_none()

    if not vendor or project.vendor != vendor.id:
        raise HTTPException(status_code=403, detail="Not your project")

    clean_slug = slugify(body.slug)

    if not clean_slug:
        raise HTTPException(status_code=400, detail="Slug is empty after cleaning — use letters, numbers, or hyphens")

    # Check uniqueness against other projects
    existing = db.execute(
        select(Project).where(
            Project.slug == clean_slug,
            Project.id != project_id
        )
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=409, detail="That URL is already taken — try another name")

    project.slug = clean_slug
    db.commit()
    db.refresh(project)

    return {"slug": project.slug, "url": f"/site/{project.slug}"}


# ---------------------------------------------------------------
# Public routes (no auth)
# ---------------------------------------------------------------

@public_router.get("/_media")
async def proxy_project_media(file_key: str, s3=Depends(get_s3_client)):
    try:
        obj = s3.Object("websafe", file_key)
        response = obj.get()
    except Exception:
        raise HTTPException(status_code=404, detail="Media not found")

    content_type = response.get("ContentType") or "application/octet-stream"
    body = response["Body"]

    return StreamingResponse(
        body.iter_chunks(),
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )


@projects_router.post("/{project_id}/upload-image")
async def upload_project_image(
    project_id: int,
    file: UploadFile = File(...),
    alt_text: Optional[str] = Form(None),
    db=Depends(get_db),
    user=Depends(get_current_user),
    s3=Depends(get_s3_client),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    vendor = db.get(Vendor, project.vendor)
    if not vendor or vendor.owner != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    filename = file.filename or "upload"
    ext = Path(filename).suffix or mimetypes.guess_extension(file.content_type or "image/png") or ".png"
    file_bytes = await file.read()
    file_key = f"projects/{project_id}/editor/{UUID.uuid4()}{ext}"

    await upload_image_to_s3(file_bytes, file_key, file.content_type or "application/octet-stream", s3)

    metadata = MediaObjectMetadata(
        project_id=project_id,
        file_key=file_key,
        file_type=file.content_type or "application/octet-stream",
        file_size_bytes=len(file_bytes),
        alt_text=alt_text,
    )
    db.add(metadata)
    db.commit()

    return {"url": build_media_proxy_url(file_key)}


@projects_router.post("/{project_id}/products")
async def assignProducts(project_id: int, data: dict, db=Depends(get_db), user=Depends(get_current_user)):
    project_ids = data.get("project_ids", [])

    for id in project_ids:
        db.add(ProjectProduct(project_id=project_id, product_id=id))

    db.commit()

    return {"status": "assigned"}


@public_router.get("/{project_slug}/{page_name}")
async def get_published_page(project_slug: str, page_name: str, db=Depends(get_db)):
    # Resolve by slug instead of numeric ID
    project = db.execute(
        select(Project).where(
            Project.slug == project_slug,
            Project.is_live == True
        )
    ).scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Store not found or not published")

    page = db.execute(
        select(ProjectPage).where(
            ProjectPage.project_id == project.id,
            ProjectPage.name == page_name
        )
    ).scalar_one_or_none()

    if not page:
        raise HTTPException(status_code=404, detail=f"Page '{page_name}' not found")

    has_products = db.execute(
        select(ProjectProduct).where(
            ProjectProduct.project_id == project.id,
            ProjectProduct.is_published == True,
            ProjectProduct.is_active == True
        ).limit(1)
    ).scalar_one_or_none() is not None

    return {
        "layout": normalize_layout_media(page.layout),
        "has_products": has_products,
        "project_name": project.name,
        "slug": project.slug,
    }


@public_router.get("/{project_slug}/products")
async def get_project_products(project_slug: str, db=Depends(get_db)):
    # Resolve by slug instead of numeric ID
    project = db.execute(
        select(Project).where(
            Project.slug == project_slug,
            Project.is_live == True
        )
    ).scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Store not found or not published")

    products = db.execute(
        select(ProjectProduct).where(
            ProjectProduct.project_id == project.id,
            ProjectProduct.is_published == True,
            ProjectProduct.is_active == True
        )
    ).scalars().all()

    product_data = []
    for product in products:
        image_url = None
        if product.product_image:
            media = db.get(MediaObjectMetadata, product.product_image)
            if media:
                image_url = build_media_proxy_url(media.file_key)

        product_data.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "sale_price": product.sale_price,
            "shipping_price": product.shipping_price,
            "currency": product.currency,
            "stock": product.stock,
            "image_url": image_url,
            "alt_text": product.alt_text
        })

    return {
        "products": product_data,
        "project_name": project.name,
        "slug": project.slug,
    }