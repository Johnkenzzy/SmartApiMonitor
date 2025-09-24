import httpx
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.metric import Metric
from app.tasks.alerts import send_alert
from app.utils.user_monitor_query import get_monitor_with_user

logger = logging.getLogger(__name__)


async def check_single_monitor(db: Session, monitor):
    """
    Perform health check for a single monitor and store result.
    Always writes a Metric, even for failed checks.
    """
    if not hasattr(monitor, "user"):
        monitor = get_monitor_with_user(db, monitor.id)

    start_time = datetime.now(timezone.utc)
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
                error_message = f"Unexpected status code {status_code}"

    except httpx.TimeoutException:
        error_message = f"Request timed out after {monitor.frequency_sec}s"
        logger.warning(f"[Monitor {monitor.id}] Timeout: {monitor.url}")

    except httpx.ConnectError as exc:
        error_message = f"Connection failed: {exc!s}"
        logger.warning(f"[Monitor {monitor.id}] Connection error: {exc}")

    except httpx.RequestError as exc:
        error_message = f"Request failed: {exc.__class__.__name__} - {exc!s}"
        logger.warning(f"[Monitor {monitor.id}] Request error: {exc}")

    except Exception as exc:
        error_message = f"Unexpected error: {exc.__class__.__name__} - {exc!s}"
        logger.error(f"[Monitor {monitor.id}] Unexpected error: {exc}", exc_info=True)

    # Persist metric
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
        logger.info(
            f"[Monitor {monitor.id}] Metric saved | status={status_code}, "
            f"is_up={is_up}, response_time={response_time_ms}ms"
        )
    except Exception as exc:
        db.rollback()
        logger.error(f"[Monitor {monitor.id}] Failed to save metric: {exc}")
        return  # do not trigger alert if metric persistence failed

    # Trigger alert if needed
    if (not is_up) or (
        monitor.max_latency_ms
        and response_time_ms
        and response_time_ms > monitor.max_latency_ms
    ):
        logger.warning(
            f"[Monitor {monitor.id}] Alert triggered (status={status_code}, "
            f"response_time={response_time_ms}ms, error={error_message})"
        )
        send_alert.delay(
            {
                "monitor_id": monitor.id,
                "monitor_name": monitor.name,
                "url": monitor.url,
                "status_code": metric.status_code,
                "response_time": metric.response_ms,
                "is_up": metric.is_up,
                "error": metric.error,
                "timestamp": metric.timestamp.strftime("%b %d, %Y — %I:%M %p %Z"),
                "email": monitor.user.email,
                "subject": "🚨 Monitor DOWN" if not metric.is_up else "⚠️ High Latency",
                "message": (
                    f"Monitor DOWN: {monitor.url} (Error: {metric.error})"
                    if not metric.is_up
                    else f"Latency Alert: {monitor.url} ({metric.response_ms}ms > {monitor.max_latency_ms}ms)"
                ),
            }
        )
