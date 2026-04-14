from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from typing import List

from app.security_utils import generate_security_report

from app.email_utils import maybe_send_urgent_report_email

router = APIRouter(
    prefix="/security",
    tags=["security"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/logs", response_model=List[dict])
def get_security_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(models.SecurityLog).order_by(models.SecurityLog.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "details": log.details,
            "ip_address": log.ip_address,
            "created_at": log.created_at,
        }
        for log in logs
    ]


# Endpoint to generate a security report (for testing/integration)
from fastapi import Body


@router.post("/generate_report", response_model=dict)
def api_generate_security_report(
    user_id: int = Body(None),
    project_id: int = Body(None),
    urgent: bool = Body(False),
    db_actions: str = Body(""),
    website_actions: str = Body(""),
    user_logins: str = Body(""),
    role_modifications: str = Body(""),
    db: Session = Depends(get_db),
):
    report = generate_security_report(
        db=db,
        user_id=user_id,
        project_id=project_id,
        urgent=urgent,
        db_actions=db_actions,
        website_actions=website_actions,
        user_logins=user_logins,
        role_modifications=role_modifications,
    )
    # Send urgent email if needed (replace with real admin email)
    maybe_send_urgent_report_email(db, report, to_email="admin@example.com")
    return {
        "id": report.id,
        "report_id": report.report_id,
        "generated_at": report.generated_at,
        "user_id": report.user_id,
        "project_id": report.project_id,
        "db_actions": report.db_actions,
        "website_actions": report.website_actions,
        "user_logins": report.user_logins,
        "role_modifications": report.role_modifications,
        "xss_test_passed": report.xss_test_passed,
        "sqli_test_passed": report.sqli_test_passed,
        "csrf_test_passed": report.csrf_test_passed,
        "urgent": report.urgent,
        "status": report.status,
        "notes": report.notes,
    }

@router.get("/reports", response_model=List[dict])
def get_security_reports(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    reports = db.query(models.SecurityReport).order_by(models.SecurityReport.generated_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": report.id,
            "report_id": report.report_id,
            "generated_at": report.generated_at,
            "user_id": report.user_id,
            "project_id": report.project_id,
            "db_actions": report.db_actions,
            "website_actions": report.website_actions,
            "user_logins": report.user_logins,
            "role_modifications": report.role_modifications,
            "xss_test_passed": report.xss_test_passed,
            "sqli_test_passed": report.sqli_test_passed,
            "csrf_test_passed": report.csrf_test_passed,
            "urgent": report.urgent,
            "status": report.status,
            "notes": report.notes,
        }
        for report in reports
    ]
