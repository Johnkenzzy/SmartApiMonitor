from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class MetricBase(BaseModel):
    monitor_id: UUID
    response_ms: int
    status_code: int
    is_up: bool

class MetricCreate(MetricBase):
    pass

class MetricRead(MetricBase):
    timestamp: datetime

    class Config:
        from_attributes = True
