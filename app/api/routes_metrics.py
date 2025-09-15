from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.db import get_db
from app.models.metric import Metric
from app.schemas.metric import MetricRead

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/", response_model=List[MetricRead])
def list_metrics(
    db: Session = Depends(get_db),
    monitor_id: Optional[UUID] = Query(None, description="Filter by monitor ID"),
    is_up: Optional[bool] = Query(None, description="Filter by uptime status"),
    since: Optional[datetime] = Query(None, description="Only return metrics after this timestamp"),
    limit: int = Query(100, le=1000, description="Max number of results to return"),
):
    """List metrics with optional filters."""
    query = db.query(Metric)

    if monitor_id:
        query = query.filter(Metric.monitor_id == monitor_id)
    if is_up is not None:
        query = query.filter(Metric.is_up == is_up)
    if since:
        query = query.filter(Metric.timestamp >= since)

    metrics = query.order_by(Metric.timestamp.desc()).limit(limit).all()
    return metrics


@router.get("/{metric_id}", response_model=MetricRead)
def get_metric(metric_id: UUID, db: Session = Depends(get_db)):
    """Fetch a single metric by ID."""
    metric = db.query(Metric).filter(Metric.id == metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric


@router.delete("/", status_code=204)
def delete_metrics(
    metric_id: UUID | None = Query(None, description="Delete a specific metric by ID"),
    monitor_id: UUID | None = Query(None, description="Delete all metrics for a specific monitor"),
    db: Session = Depends(get_db),
):
    """
    Delete metrics. Either `metric_id` OR `monitor_id` must be provided.
    - If `metric_id` is provided, deletes that metric.
    - If `monitor_id` is provided, deletes all metrics for that monitor.
    """
    if not metric_id and not monitor_id:
        raise HTTPException(
            status_code=400,
            detail="You must provide either 'metric_id' or 'monitor_id'."
        )

    if metric_id:
        metric = db.query(Metric).filter(Metric.id == metric_id).first()
        if not metric:
            raise HTTPException(status_code=404, detail="Metric not found")
        db.delete(metric)
        db.commit()
        return None

    if monitor_id:
        deleted_count = db.query(Metric).filter(Metric.monitor_id == monitor_id).delete()
        db.commit()
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="No metrics found for this monitor")
        return None
