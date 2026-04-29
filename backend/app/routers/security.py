from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.dependencies import get_db, get_current_user
from app import models


router = APIRouter(prefix="/security", tags=["security"])


class SecurityLogOut(BaseModel):
    id: int
    action: str
    details: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/activity", response_model=list[SecurityLogOut])
def get_activity(
    limit: int = 30,
    action: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.SecurityLog)
        .filter(models.SecurityLog.user_id == current_user.id)
        .order_by(models.SecurityLog.created_at.desc())
    )
    if action:
        query = query.filter(models.SecurityLog.action == action)
    return query.limit(limit).all()
    
