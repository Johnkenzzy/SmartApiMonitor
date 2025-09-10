from pydantic import BaseModel, HttpUrl
from uuid import UUID
from datetime import datetime

class MonitorBase(BaseModel):
    name: str
    url: HttpUrl
    frequency_sec: int

class MonitorCreate(MonitorBase):
    pass

class MonitorUpdate(BaseModel):
    name: str | None = None
    url: HttpUrl | None = None
    frequency_sec: int | None = None
    is_active: bool | None = None

class MonitorRead(MonitorBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
