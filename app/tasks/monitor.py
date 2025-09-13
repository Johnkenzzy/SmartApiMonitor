import asyncio
import logging

from app.core.celery_app import celery_app
from app.db import SessionLocal
from app.models.monitor import Monitor
from app.services.monitor import check_single_monitor

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.monitor.check_monitors")
def check_monitors():
    """Fetch all active monitors and check their status."""
    db = SessionLocal()
    try:
        monitors = db.query(Monitor).filter(Monitor.is_active == True).all()

        if not monitors:
            logger.info("No active monitors found.")
            return

        async def run_all():
            tasks = []
            for monitor in monitors:
                # Wrap each monitor check in asyncio.wait_for for safety
                tasks.append(
                    asyncio.wait_for(check_single_monitor(db, monitor),
                    timeout=monitor.frequency_sec)
                )   
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Log any exceptions but continue
            for monitor, result in zip(monitors, results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Monitor check failed for {monitor.url}: {result}")

        asyncio.run(run_all())
        logger.info(f"✅ Completed checks for {len(monitors)} monitors.")
    except Exception as exc:
        logger.exception("Error running monitor checks")
    finally:
        db.close()
