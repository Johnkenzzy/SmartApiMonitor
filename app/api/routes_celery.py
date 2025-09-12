from fastapi import APIRouter

from app.core.celery_app import celery_app
from app.tasks.monitor import check_monitors

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/trigger-checks")
async def trigger_monitor_checks():
    check_monitors.delay()  # ✅ Runs in Celery worker
    return {"message": "Monitor checks triggered"}

@router.get("/celery-health")
async def celery_health():
    result = celery_app.control.ping()
    return {"workers": result}
