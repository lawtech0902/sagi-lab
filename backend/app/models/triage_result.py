import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.entity import ExtractedEntity


class TriageResult(Base):
    __tablename__ = "triage_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("alerts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Classification
    alert_source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    alert_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # ATT&CK Mapping
    tactic: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    technique: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Analysis
    conclusion: Mapped[str] = mapped_column(Text, nullable=False)
    investigation_steps: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Metadata
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    alert: Mapped["Alert"] = relationship("Alert", back_populates="triage_result")
    entities: Mapped[List["ExtractedEntity"]] = relationship(
        "ExtractedEntity", back_populates="triage_result", cascade="all, delete-orphan"
    )
