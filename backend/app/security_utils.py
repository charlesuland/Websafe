import uuid
from datetime import datetime

from fastapi.params import Depends
from app.dependencies import get_db
from app.models import SecurityReport

class ProjectSecurityInfo:
    user_id=None,
    project_id=None,
    urgent=False,
    db_actions=None,
    website_actions=None,
    user_logins=None,
    role_modifications=None


def run_security_tests() -> dict:
    # Dummy implementations, replace with real tests
    return {
        "xss_test_passed": True,
        "sqli_test_passed": True,
        "csrf_test_passed": True,
        "notes": "All tests passed."
    }
    

def generate_security_report(project_security_info: ProjectSecurityInfo, db=Depends(get_db)):
    tests = run_security_tests()
    report = SecurityReport(
        report_id=str(uuid.uuid4()),
        generated_at=datetime.utcnow(),
        user_id=project_security_info.user_id,
        project_id=project_security_info.project_id,
        db_actions=project_security_info.db_actions or "",
        website_actions=project_security_info.website_actions or "",
        user_logins=project_security_info.user_logins or "",
        role_modifications=project_security_info.role_modifications or "",
        xss_test_passed=tests["xss_test_passed"],
        sqli_test_passed=tests["sqli_test_passed"],
        csrf_test_passed=tests["csrf_test_passed"],
        urgent=project_security_info.urgent,
        status="pass" if all([tests["xss_test_passed"], tests["sqli_test_passed"], tests["csrf_test_passed"]]) else "fail",
        notes=tests["notes"]
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
