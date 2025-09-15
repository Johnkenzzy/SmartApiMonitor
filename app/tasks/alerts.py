import logging

from app.core.celery_app import celery_app
from app.services.alerts import send_alert_message

logger = logging.getLogger(__name__)


@celery_app.task(
  name="app.tasks.alerts.send_alert",
  autoretry_for=(Exception,), # Retries for any exception
  retry_backoff=True, # Exponential backoff: 1s, 2s, 4s...
  retry_kwargs={"max_retries": 5},  # Limit retries to avoid infinite loops
  acks_late=True  # Ensure task is requeued if worker crashes mid-task
)
def send_alert(alert_data: dict):
    """Send email/SMS alert asynchronously."""
    try:
        if not isinstance(alert_data, dict):
            raise ValueError("alert_data must be a dictionary")

        logger.info(
          f"[Celery] Processing alert task for monitor_id={alert_data.get('monitor_id')}"
        )
        send_alert_message(alert_data)
        logger.info(
          f"[Celery] ✅ Alert task completed (monitor_id={alert_data.get('monitor_id')})"
        )

    except Exception as exc:
        logger.error(f"[Celery] ❌ Failed to send alert: {exc}", exc_info=True)
        raise  # triggers Celery retry mechanism
