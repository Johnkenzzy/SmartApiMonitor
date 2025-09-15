from fastapi import APIRouter

from app.core.celery_app import celery_app
from app.tasks.monitor import check_single_monitor_task

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/trigger-checks")
async def trigger_monitor_checks():
    check_single_monitor_task.delay()  # Runs in Celery worker
    return {"message": "Monitor checks triggered"}

@router.get("/celery-health")
async def celery_health():
    result = celery_app.control.ping()
    return {"workers": result}
