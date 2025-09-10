from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class AlertBase(BaseModel):
    monitor_id: UUID
    message: str
    channel: str  # "email", "sms", "slack"

class AlertCreate(AlertBase):
    pass

class AlertRead(AlertBase):
    id: UUID
    triggered_at: datetime

    class Config:
        from_attributes = True
