import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    TIMESTAMP,
    text,
    Boolean,
    ForeignKey,
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class Monitor(Base):
    __tablename__ = "monitors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    url = Column(String(2048), nullable=False)
    frequency_sec = Column(Integer, nullable=False, default=60)
    max_latency_ms = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    user = relationship("User", back_populates="monitors")
    last_checked_at = Column(TIMESTAMP, nullable=True)
    celery_task_id = Column(String, nullable=True, server_default=None,)  # store scheduled Celery task ID
    created_at = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        CheckConstraint("frequency_sec > 0", name="check_frequency_positive"),
        Index("idx_monitor_active", "is_active"),
    )

    def __repr__(self):
        return (
            f"<Monitor(id={self.id}, name={self.name}, url={self.url}, "
            f"frequency={self.frequency_sec}s, active={self.is_active})>"
        )
