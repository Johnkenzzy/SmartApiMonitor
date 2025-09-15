import asyncio
import logging
from datetime import datetime, timedelta, timezone
from celery.result import AsyncResult

from app.core.celery_app import celery_app
from app.db import SessionLocal
from app.models.monitor import Monitor
from app.services.monitor import check_single_monitor

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.monitor.check_single_monitor")
def check_single_monitor_task(monitor_id: str):
    db = SessionLocal()
    try:
        monitor = db.get(Monitor, monitor_id)
        if not monitor:
            logger.warning(f"Monitor {monitor_id} not found — skipping.")
            return

        if not monitor.is_active:
            logger.info(f"Monitor {monitor.url} is inactive — skipping reschedule.")
            return

        # --- Run the monitor check ---
        try:
            asyncio.run(check_single_monitor(db, monitor))
        except RuntimeError:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(check_single_monitor(db, monitor))

        monitor.last_checked_at = datetime.now(timezone.utc)

        # --- Schedule next run safely ---
        # Only revoke if there is a still-pending task
        if monitor.celery_task_id:
            prev_task = AsyncResult(monitor.celery_task_id)
            if prev_task.state in ("PENDING", "RECEIVED", "SCHEDULED"):
                try:
                    prev_task.revoke(terminate=False)
                    logger.debug(
                        f"Revoked pending task {monitor.celery_task_id} for {monitor.url}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to revoke pending task: {e}")

        try:
            next_task = check_single_monitor_task.apply_async(
                args=[monitor_id],
                countdown=monitor.frequency_sec,
            )
            monitor.celery_task_id = next_task.id
        except Exception as e:
            logger.error(f"⚠️ Failed to schedule next task for {monitor.url}: {e}")

        db.commit()
        logger.info(
            f"✅ Monitor {monitor.url} checked in {monitor.frequency_sec}sec - (task={monitor.celery_task_id})."
        )

    except Exception as exc:
        db.rollback()
        logger.exception(f"Error checking monitor {monitor_id}: {exc}")
    finally:
        db.close()
