from celery import Celery
from app.config import settings

celery_app = Celery(
    "monitoring",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.task_routes = {
    "app.tasks.monitor.check_monitors": {"queue": "monitoring"},
    "app.tasks.alerts.send_alert": {"queue": "alerts"},
}

celery_app.conf.beat_schedule = {
    "check-monitors-every-minute": {
        "task": "app.tasks.monitor.check_monitors",
        "schedule": 60.0,  # run every 60 seconds
    },
}

celery_app.conf.timezone = "UTC"

celery_app.autodiscover_tasks(["app.tasks"])
