import uuid
from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    monitor_id = Column(
        UUID(as_uuid=True), ForeignKey("monitors.id", ondelete="CASCADE"))
    triggered_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    message = Column(String)
    channel = Column(String)  # e.g. "email", "sms"
