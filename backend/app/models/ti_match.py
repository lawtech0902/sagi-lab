import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, Boolean, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.entity import ExtractedEntity


class TiMatch(Base):
    __tablename__ = "ti_matches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("extracted_entities.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    vt_detected: Mapped[bool] = mapped_column(Boolean, nullable=False)
    vt_positives: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vt_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vt_scan_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    vt_permalink: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    vt_response: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    entity: Mapped["ExtractedEntity"] = relationship(
        "ExtractedEntity", back_populates="ti_match"
    )
