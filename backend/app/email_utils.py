import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models import SecurityReport
import os

def send_urgent_security_email(report: SecurityReport, to_email: str):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.example.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER", "user@example.com")
    smtp_password = os.getenv("SMTP_PASSWORD", "password")
    from_email = os.getenv("FROM_EMAIL", smtp_user)

    subject = f"URGENT: Security Report {report.report_id}"
    body = f"""
    Urgent Security Report Generated\n\nReport ID: {report.report_id}\nDate: {report.generated_at}\nStatus: {report.status}\nXSS Test: {report.xss_test_passed}\nSQLi Test: {report.sqli_test_passed}\nCSRF Test: {report.csrf_test_passed}\nNotes: {report.notes}\n\nPlease review immediately.
    """
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())

def maybe_send_urgent_report_email(report: SecurityReport, to_email: str):
    if report.urgent or report.status == "fail":
        send_urgent_security_email(report, to_email)
