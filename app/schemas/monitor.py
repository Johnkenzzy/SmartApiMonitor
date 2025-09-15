from pydantic import BaseModel, HttpUrl, Field, field_serializer, validator
from uuid import UUID
from datetime import datetime
from typing import Optional


class MonitorBase(BaseModel):
    name: str = Field(
        ..., min_length=3, max_length=255,
        description="Friendly name for the monitor"
    )
    url: HttpUrl = Field(
        ..., max_length=2048,
        description="The URL to be monitored"
    )
    frequency_sec: int = Field(
        ..., gt=0,
        description="Frequency (seconds) at which to check the monitor"
    )
    max_latency_ms: Optional[int] = Field(
        None, gt=0,
        description="Optional max response time (ms) before marking as slow"
    )

    # Automatically convert HttpUrl to str before exporting
    @field_serializer("url")
    def serialize_url(self, url: HttpUrl, _info):
        return str(url)


class MonitorCreate(MonitorBase):
    """Schema for creating a new monitor."""
    pass


class MonitorUpdate(BaseModel):
    """Schema for partial updates."""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    url: Optional[HttpUrl] = Field(None, max_length=2048)
    frequency_sec: Optional[int] = Field(None, gt=0)
    max_latency_ms: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

    # Automatically convert HttpUrl to str before exporting
    @field_serializer("url")
    def serialize_url(self, url: HttpUrl, _info):
        return str(url)


class MonitorRead(MonitorBase):
    """Schema for API responses."""
    id: UUID
    user_id: UUID
    is_active: bool
    last_checked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "4b1c1d52-20b3-4fc1-95b3-6b3a91d132e4",
                "user_id": "9d81a1b4-8c44-4f7f-bf48-9a4b7f929b64",
                "name": "API Healthcheck",
                "url": "https://example.com/health",
                "frequency_sec": 60,
                "max_latency_ms": 500,
                "is_active": True,
                "created_at": "2025-09-10T10:00:00Z",
                "updated_at": "2025-09-10T10:30:00Z",
            }
        }
