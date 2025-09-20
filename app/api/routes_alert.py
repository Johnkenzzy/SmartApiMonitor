from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from typing import List, Optional
from uuid import UUID

from app.db import get_db
from app.models import Alert, Monitor
from app.schemas import AlertRead
from app.utils.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=List[AlertRead])
def list_alerts(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    monitor_id: Optional[UUID] = Query(None, description="Filter by monitor ID"),
    channel: Optional[str] = Query(None, description="Filter by channel (email, sms)"),
    limit: int = Query(50, ge=1, le=200, description="Max number of alerts to fetch"),
):
    """Get alerts for the current user (optionally filtered by monitor_id/channel)."""
    query = (
        db.query(Alert)
        .join(Monitor, Monitor.id == Alert.monitor_id)
        .filter(Monitor.user_id == current_user.id)
    )

    if monitor_id:
        query = query.filter(Alert.monitor_id == monitor_id)
    if channel:
        query = query.filter(Alert.channel == channel)

    return query.order_by(Alert.triggered_at.desc()).limit(limit).all()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_alerts(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    alert_id: Optional[UUID] = Query(None, description="Delete specific alerts by ID"),
    monitor_id: Optional[UUID] = Query(None, description="Delete all alerts for a monitor"),
    channel: Optional[str] = Query(None, description="Delete all alerts by channel (email, sms)"),
):
    """
    Delete alerts for the current user using a safe subquery filter.
    """
    # Build a subquery of monitor_ids the current user owns
    user_monitors_subq = (
        select(Monitor.id)
        .filter(Monitor.user_id == current_user.id)
        .subquery()
    )

    # Build filter condition
    filters = [Alert.monitor_id.in_(user_monitors_subq)]

    if alert_id:
        filters.append(Alert.id == alert_id)
    if monitor_id:
        filters.append(Alert.monitor_id == monitor_id)
    if channel:
        filters.append(Alert.channel == channel)

    # Perform a DELETE statement explicitly
    stmt = delete(Alert).where(*filters)
    result = db.execute(stmt)
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="No alerts found matching criteria")
    return None