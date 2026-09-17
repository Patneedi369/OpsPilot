from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    workflow_stage: Mapped[str] = mapped_column(String(32), nullable=False)
    service_id: Mapped[str] = mapped_column(String(64), nullable=False)
    service_name: Mapped[str] = mapped_column(String(64), nullable=False)
    started_at: Mapped[str] = mapped_column(String(64), nullable=False)
    duration_label: Mapped[str] = mapped_column(String(32), nullable=False)
    elapsed_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    trigger: Mapped[str] = mapped_column(Text, nullable=False)
    affected_services: Mapped[list] = mapped_column(JSONB, nullable=False)
    blast_radius: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=utcnow,
        default=utcnow,
    )

    events: Mapped[list["IncidentEvent"]] = relationship(back_populates="incident")
    logs: Mapped[list["LogEntry"]] = relationship(back_populates="incident")


if TYPE_CHECKING:
    from app.models.incident_event import IncidentEvent
    from app.models.log_entry import LogEntry
