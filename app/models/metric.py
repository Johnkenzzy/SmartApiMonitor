import uuid
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Boolean,
    TIMESTAMP,
    Text,
    text,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    monitor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("monitors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    response_ms = Column(Integer, nullable=True)  # latency in ms (null if down)
    status_code = Column(Integer, nullable=True)  # HTTP status code or None
    is_up = Column(Boolean, nullable=False, default=False)
    error = Column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "response_ms IS NULL OR response_ms >= 0",
            name="check_response_ms_positive"
        ),
        Index("idx_metric_monitor_timestamp", "monitor_id", "timestamp"),
    )

    def __repr__(self):
        return (
            f"<Metric(id={self.id}, monitor_id={self.monitor_id}, is_up={self.is_up}, "
            f"status_code={self.status_code}, response_ms={self.response_ms}, "
            f"error={self.error}, timestamp={self.timestamp})>"
        )
