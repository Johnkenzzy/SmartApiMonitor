from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class AlertRead(BaseModel):
    id: UUID
    monitor_id: UUID
    triggered_at: datetime
    message: str
    channel: str | None = None

    class Config:
        from_attributes = True
