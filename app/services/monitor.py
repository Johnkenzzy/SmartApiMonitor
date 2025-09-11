import httpx
from datetime import datetime
from app.models.metric import Metric
from app.tasks.alerts import send_alert


def check_single_monitor(db, monitor):
    """Perform health check for a single monitor and store result."""
    try:
        response = httpx.get(monitor.url, timeout=monitor.timeout)
        status = "up" if response.status_code == 200 else "down"
    except Exception:
        status = "down"

    # Save metric
    metric = Metric(
        monitor_id=monitor.id,
        status=status,
        response_time=(response.elapsed.total_seconds() if status == "up" else None),
        timestamp=datetime.utcnow(),
    )
    db.add(metric)
    db.commit()

    # Trigger alert if needed
    if status == "down":
        send_alert.delay({"monitor_id": monitor.id, "status": "down"})
