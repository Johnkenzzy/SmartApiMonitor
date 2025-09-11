# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.interval import IntervalTrigger
# from sqlalchemy.orm import Session

# from app.db import SessionLocal
# from app.services.monitor import run_monitor_checks
# import logging

# logger = logging.getLogger(__name__)

# scheduler = BackgroundScheduler()

# def start_scheduler():
#     """Start the APScheduler with monitor check job."""
#     logger.info("Starting APScheduler...")
#     scheduler.add_job(
#         func=monitor_job,
#         trigger=IntervalTrigger(minutes=1),
#         id="monitor_job",
#         name="Monitor API endpoints every minute",
#         replace_existing=True,
#     )
#     scheduler.start()
#     logger.info("APScheduler started ✅")


# def stop_scheduler():
#     """Stop APScheduler on shutdown."""
#     logger.info("Stopping APScheduler...")
#     scheduler.shutdown(wait=False)


# def monitor_job():
#     """Wrapper job that creates a DB session and runs checks."""
#     db: Session = SessionLocal()
#     try:
#         run_monitor_checks(db)
#     except Exception as e:
#         logger.exception(f"Monitor job failed: {e}")
#     finally:
#         db.close()
