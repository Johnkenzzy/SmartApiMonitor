import logging
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.metric import Metric
from datetime import datetime

logger = logging.getLogger(__name__)

def send_alert_if_needed(db: Session, monitor, metric: Metric):
    """
    Check metric and create alert if needed.
    Called during monitor check logic (synchronous).
    """
    alert_triggered = False
    alert_message = None

    if not metric.is_up:
        alert_triggered = True
        alert_message = f"Monitor DOWN: {monitor.url} (Error: {metric.error})"
    elif monitor.max_latency_ms and metric.response_time_ms > monitor.max_latency_ms:
        alert_triggered = True
        alert_message = (
            f"Latency Alert: {monitor.url} "
            f"({metric.response_time_ms}ms > {monitor.max_latency_ms}ms)"
        )

    if alert_triggered:
        logger.warning(alert_message)
        _store_alert(db, monitor.id, alert_message)
        _send_notifications(monitor.user.email, alert_message)


def send_alert_message(alert_data: dict):
    """
    Celery task handler for sending alert messages asynchronously.
    Accepts a dict with keys: monitor_id, message, email (optional)
    """
    monitor_id = alert_data.get("monitor_id")
    message = alert_data.get("message")
    email = alert_data.get("email")

    logger.warning(f"Async Alert Triggered: {message}")
    # You could store to DB here if monitor_id provided
    if monitor_id and message:
        db = None
        try:
            from app.db import SessionLocal
            db = SessionLocal()
            _store_alert(db, monitor_id, message)
        finally:
            if db:
                db.close()

    if email:
        _send_notifications(email, message)


def _store_alert(db: Session, monitor_id: int, message: str):
    """Helper to create and persist an Alert record."""
    alert = Alert(
        monitor_id=monitor_id,
        triggered_at=datetime.utcnow(),
        message=message,
    )
    db.add(alert)
    db.commit()


def _send_notifications(email: str, message: str):
    """Actual notification sending logic."""
    logger.info(f"Sending email to {email}: {message}")
    # TODO: Replace with real email/SMS/slack integration
