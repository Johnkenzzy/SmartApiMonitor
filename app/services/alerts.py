import logging
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.config import settings

logger = logging.getLogger(__name__)


def send_alert_message(alert_data: dict):
    """
    Celery task handler for sending alert messages asynchronously.
    Called from tasks.alerts.send_alert(alert_data).
    """

    monitor_id = alert_data.get("monitor_id")
    subject = alert_data.get("subject", "🚨 Monitor Alert")
    email = alert_data.get("email")
    message = alert_data.get("message")

    logger.warning(f"📧 Sending Alert: {subject} -> {email}")

    # Store alert in DB
    if monitor_id and message:
        from app.db import SessionLocal
        db: Session = None
        try:
            db = SessionLocal()
            _store_alert(db, monitor_id, message)
        finally:
            if db:
                db.close()

    if email:
        _send_email_notification(email, subject, alert_data)


def _store_alert(db: Session, monitor_id: str, message: str):
    """Persist alert record in database."""
    alert = Alert(
        monitor_id=monitor_id,
        triggered_at=datetime.now(timezone.utc),
        message=message,
    )
    db.add(alert)
    db.commit()
    logger.info(f"✅ Alert stored in DB for monitor {monitor_id}")


def _send_email_notification(email: str, subject: str, alert_data: dict):
    """Send a well-styled HTML + plaintext email."""
    try:
        msg = EmailMessage()
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = email
        msg["Subject"] = subject

        # Build plain-text fallback
        text_content = alert_data.get("message", "An alert was triggered.")
        msg.set_content(text_content)

        # Build HTML content
        status_color = "#dc2626" if not alert_data.get("is_up") else "#f59e0b"
        response_time = alert_data.get("response_time") or "N/A"
        error = alert_data.get("error") or "None"

        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color:#f9fafb; padding:20px;">
            <div style="max-width: 600px; margin: auto; background: white; padding: 20px; 
                        border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
              
              <h2 style="color:{status_color}; margin-top: 0;">{subject}</h2>
              
              <p style="color:#374151; font-size: 15px;">
                <b>Monitor:</b> {alert_data.get("monitor_name")}<br>
                <b>URL:</b> <a href="{alert_data.get("url")}" target="_blank">{alert_data.get("url")}</a><br>
                <b>Status:</b> {"✅ UP" if alert_data.get("is_up") else "❌ DOWN"}<br>
                <b>HTTP Code:</b> {alert_data.get("status_code") or "N/A"}<br>
                <b>Response Time:</b> {response_time} ms<br>
                <b>Checked at:</b> {alert_data.get("timestamp")}<br>
                <b>Error:</b> {error}<br>
              </p>

              <p style="margin-top: 20px; font-size: 14px; color:#6b7280;">
                This is an automated alert from <b>SmartAPI Monitor</b>.
              </p>
            </div>
          </body>
        </html>
        """

        msg.add_alternative(html, subtype="html")

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"✅ Alert email sent to {email}")

    except Exception as e:
        logger.error(f"❌ Failed to send alert email: {e}")
