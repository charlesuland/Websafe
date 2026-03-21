from fastapi import APIRouter, HTTPException
from app.dependencies import get_db, get_current_user
from app.models import Project, ProjectPage, Vendor, DraftProjectPage
from fastapi import Depends
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
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

    return [
        {
            "id": p.id,
            "name": p.name,
            "is_live": p.is_live,
            "last_updated": p.updated_at,
            "last_published": p.last_published,
            "preview_image": p.preview_image
        }
        for p in projects
    ]

@projects_router.post("/")
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

@projects_router.delete("/{project_id}")
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


@projects_router.get("/{project_id}/draft-pages")
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


@public_router.get("/{project_slug}/{page_name}")
async def get_page(project_slug: str, page_name: str, db=Depends(get_db)):
    project = db.execute(
        select(Project).where(Project.slug == project_slug)
    ).scalar_one_or_none()

    if not project or not project.is_live:
        raise HTTPException(404)

    page = db.execute(
        select(ProjectPage).where(
            ProjectPage.project_id == project.id,
            ProjectPage.name == page_name.capitalize()
        )
    ).scalar_one_or_none()

    if not page:
        raise HTTPException(404)

    return page.layout


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


@projects_router.post("/{project_id}/draft")
async def save_draft_pages(
    project_id: int,
    data: DraftSaveRequest,
    db=Depends(get_db),
    user=Depends(get_current_user)
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
        project.preview_image = data.preview
    project.last_updated = datetime.utcnow()

    db.commit()

    return {"status": "saved"}