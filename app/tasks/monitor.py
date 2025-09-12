from app.core.celery_app import celery_app
from app.db import SessionLocal
from app.models.monitor import Monitor
from app.services.monitor import check_single_monitor

@celery_app.task(name="app.tasks.monitor.check_monitors")
def check_monitors():
    """Fetch all active monitors and check their status."""
    db = SessionLocal()
    try:
        monitors = db.query(Monitor).filter(Monitor.is_active == True).all()
        for monitor in monitors:
            check_single_monitor(db, monitor)
    finally:
        db.close()
