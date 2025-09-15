import logging
from celery.result import AsyncResult
from sqlalchemy.orm import joinedload

from app.core.celery_app import celery_app
from app.db import SessionLocal
from app.models.monitor import Monitor
from app.tasks.monitor import check_single_monitor_task

logger = logging.getLogger(__name__)


def reschedule_all_monitors():
    """Reschedule tasks for all active monitors on startup."""
    db = SessionLocal()
    try:
        # Load monitors with their user relationship so we have access for alerts if needed
        monitors = (
            db.query(Monitor)
            .options(joinedload(Monitor.user))
            .filter(Monitor.is_active == True)
            .all()
        )

        if not monitors:
            logger.info("No active monitors found to reschedule.")
            return

        for monitor in monitors:
            # Revoke old task if it exists (likely invalid after restart)
            if monitor.celery_task_id:
                try:
                    AsyncResult(monitor.celery_task_id).revoke(terminate=False)
                    logger.debug(f"Revoked old task {monitor.celery_task_id} for {monitor.url}")
                except Exception as e:
                    logger.warning(f"Failed to revoke task {monitor.celery_task_id}: {e}")

            try:
                # Schedule a new task immediately (countdown = 0)
                task = check_single_monitor_task.apply_async(
                    args=[str(monitor.id)], countdown=0
                )
                monitor.celery_task_id = task.id
                logger.info(
                    f"Rescheduled monitor {monitor.url} "
                    f"(new task={task.id}) to run in {monitor.frequency_sec}s"
                )
            except Exception as e:
                logger.error(f"Failed to schedule monitor {monitor.url}: {e}")

        db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to reschedule all monitors: {e}")
    finally:
        db.close()


# def schedule_task_async(monitor):
#     db = SessionLocal()
#     try:
#         task = check_single_monitor_task.apply_async(
#             args=[str(monitor.id)], countdown=monitor.frequency_sec
#         )
#         monitor.celery_task_id = task.id
#         db.commit()
#     except Exception as e:
#         logger.error(f"Failed to schedule task: {e}")