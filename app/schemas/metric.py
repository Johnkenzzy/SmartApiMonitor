from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class MetricRead(BaseModel):
    id: UUID
    monitor_id: UUID
    timestamp: datetime
    response_ms: Optional[int] = None
    status_code: Optional[int] = None
    is_up: bool
    error: Optional[str] = None

    class Config:
        from_attributes = True
