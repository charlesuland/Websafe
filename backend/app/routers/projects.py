from fastapi import APIRouter, HTTPException
from app.dependencies import get_db, get_current_user, get_s3_client
from app.models import (
    Project,
    ProjectPage,
    Vendor, 
    DraftProjectPage,
    MediaObjectMetadata,
    ProjectProduct,
    ProductImage
)
from fastapi import Depends
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid as UUID
import base64
import mimetypes
from sqlmodel import select

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
                preview_url = f"https://websafe.s3.us-east-2.amazonaws.com/{metadata.file_key}"

        projects_data.append({
            "id": p.id,
            "name": p.name,
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
            "layout": p.layout
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
            layout=d.layout
        )
        db.add(page)

    project.is_live = True
    project.last_published = datetime.utcnow()

    db.commit()

    return {"status": "published"}


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
                    file_size_bytes=file_size
                )

            db.add(new_metadata)
            db.flush()
            
            project.preview_image = new_metadata.id

            obj = s3.Object("websafe", file_key)
            obj.put(Body=file_bytes, ContentType=mime_type)

        except Exception as e:
            raise HTTPException(400, f"Invalid preview image: {str(e)}")
    
    project.last_updated = datetime.utcnow()

    db.commit()

    return {"status": "saved"}


@projects_router.post("/{project_id}/products")
async def assignProducts(project_id: int, data: dict, db=Depends(get_db), user=Depends(get_current_user)):
    project_ids = data.get("project_ids", [])

    for id in project_ids:
        db.add(ProjectProduct(project_id=project_id, product_id=id))

    db.commit()

    return {"status": "assigned"}