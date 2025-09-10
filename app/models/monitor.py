# app/models/monitor.py
from sqlalchemy import Column, String, Integer, TIMESTAMP, text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db import Base

class Monitor(Base):
    __tablename__ = "monitors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    frequency_sec = Column(Integer, default=60)  # check frequency
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
