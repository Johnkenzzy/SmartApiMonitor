import httpx
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.metric import Metric
from app.tasks.alerts import send_alert

logger = logging.getLogger(__name__)

async def check_single_monitor(db: Session, monitor):
    """
    Perform health check for a single monitor and store result.
    Always writes a Metric, even for failed checks.
    """
    start_time = datetime.utcnow()
    response_time_ms = None
    status_code = None
    is_up = False
    error_message = None

    try:
        async with httpx.AsyncClient(timeout=monitor.frequency_sec) as client:
            response = await client.get(monitor.url)
            response_time_ms = response.elapsed.total_seconds() * 1000
            status_code = response.status_code
            is_up = status_code == 200
            if not is_up:
                error_message = f"Non-200 status: {status_code}"

    except httpx.RequestError as exc:
        error_message = f"Request failed: {exc}"
        logger.warning(f"[Monitor {monitor.id}] {monitor.url} request error: {exc}")

    except Exception as exc:
        error_message = f"Unexpected error: {exc}"
        logger.error(f"[Monitor {monitor.id}] {monitor.url} unexpected error: {exc}")

    # Always insert a metric record
    try:
        metric = Metric(
            monitor_id=monitor.id,
            status_code=status_code,
            is_up=is_up,
            response_ms=response_time_ms,
            error=error_message,
            timestamp=start_time,
        )
        db.add(metric)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error(f"[Monitor {monitor.id}] Failed to save metric: {exc}")
        return  # do not trigger alert if metric persistence failed

    # Trigger alert for downtime or latency violation
    if (not is_up) or (
        monitor.max_latency_ms and response_time_ms and response_time_ms > monitor.max_latency_ms
    ):
        logger.warning(
            f"[Monitor {monitor.id}] Alert triggered (status={status_code}, response={response_time_ms}ms)"
        )
        send_alert.delay(
            {
                "monitor_id": str(monitor.id),
                "status": "up" if is_up else "down",
                "status_code": status_code,
                "response_time_ms": response_time_ms,
                "error": error_message,
            }
        )