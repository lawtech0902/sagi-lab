import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET, ARRAY

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.triage_result import TriageResult


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    alert_name: Mapped[str] = mapped_column(String(255), nullable=False)
    alert_level: Mapped[str] = mapped_column(String(50), nullable=False)

    source_ip: Mapped[Optional[list[str]]] = mapped_column(ARRAY(INET), nullable=True)
    destination_ip: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(INET), nullable=True
    )
    host_ip: Mapped[Optional[str]] = mapped_column(INET, nullable=True)

    first_alert_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    last_alert_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    upload_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    triage_result: Mapped[Optional["TriageResult"]] = relationship(
        "TriageResult",
        back_populates="alert",
        uselist=False,
        cascade="all, delete-orphan",
    )
