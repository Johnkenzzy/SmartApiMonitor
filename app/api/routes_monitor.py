from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db import get_db
from app.models.monitor import Monitor
from app.schemas.monitor import MonitorCreate, MonitorUpdate, MonitorRead
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/monitors", tags=["Monitors"])


@router.get("/", response_model=List[MonitorRead])
def list_monitors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all monitors for the current user."""
    return (
        db.query(Monitor)
        .filter(Monitor.user_id == current_user.id)
        .order_by(Monitor.created_at.desc())
        .all()
    )


@router.post("/", response_model=MonitorRead, status_code=status.HTTP_201_CREATED)
def create_monitor(
    payload: MonitorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new monitor for the current user."""
    monitor = Monitor(**payload.dict(), user_id=current_user.id)
    db.add(monitor)
    db.commit()
    db.refresh(monitor)
    return monitor


@router.get("/{monitor_id}", response_model=MonitorRead)
def get_monitor(
    monitor_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single monitor by ID for the current user."""
    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id, Monitor.user_id == current_user.id)
        .first()
    )
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return monitor


@router.put("/{monitor_id}", response_model=MonitorRead)
def update_monitor(
    monitor_id: UUID,
    payload: MonitorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing monitor for the current user."""
    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id, Monitor.user_id == current_user.id)
        .first()
    )
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(monitor, key, value)

    db.commit()
    db.refresh(monitor)
    return monitor


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitor(
    monitor_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a monitor for the current user."""
    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id, Monitor.user_id == current_user.id)
        .first()
    )
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    db.delete(monitor)
    db.commit()
    return None
