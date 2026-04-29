from __future__ import annotations

from typing import Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.models import SecurityLog


def queue_security_event(
    db: Session,
    *,
    user_id: Optional[int],
    action: str,
    request: Request | None = None,
    details: str | None = None,
) -> SecurityLog:
    event = SecurityLog(
        user_id=user_id,
        action=action,
        details=details or _default_request_details(request),
        ip_address=request.client.host if request and request.client else None,
    )
    db.add(event)

    return event


def log_and_commit_security_event(
    db: Session,
    *,
    user_id: Optional[int],
    action: str,
    request: Request | None = None,
    details: str | None = None,
) -> SecurityLog:
    event = queue_security_event(
        db,
        user_id=user_id,
        action=action,
        request=request,
        details=details,
    )
    db.commit()
    return event


def describe_activity(subject_type: str, subject_name: str, verb: str, *, extra: str | None = None) -> str:
    subject_label = f"{subject_type.title()} '{subject_name}'"
    if extra:
        return f"{subject_label} {verb}. {extra}"
    return f"{subject_label} {verb}."


def _default_request_details(request: Request | None) -> str | None:
    if not request:
        return None
    return request.headers.get("user-agent")
