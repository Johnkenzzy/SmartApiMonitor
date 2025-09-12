from app.core.celery_app import celery_app
from app.services.alerts import send_alert_message

@celery_app.task(
  name="app.tasks.alerts.send_alert",
  autoretry_for=(Exception,),
  retry_backoff=True
)
def send_alert(alert_data: dict):
    """Send email/SMS alert asynchronously."""
    send_alert_message(alert_data)
