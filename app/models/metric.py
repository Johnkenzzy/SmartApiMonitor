from sqlalchemy import Column, ForeignKey, Integer, Boolean, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base

class Metric(Base):
    __tablename__ = "metrics"

    monitor_id = Column(UUID(as_uuid=True), ForeignKey("monitors.id", ondelete="CASCADE"), primary_key=True)
    timestamp = Column(TIMESTAMP, primary_key=True, server_default=text("CURRENT_TIMESTAMP"))
    response_ms = Column(Integer)  # latency in ms
    status_code = Column(Integer)
    is_up = Column(Boolean)  # True = success, False = failure
