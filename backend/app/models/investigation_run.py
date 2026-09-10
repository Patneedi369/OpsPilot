from typing import Any

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InvestigationRun(Base):
    __tablename__ = "investigation_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    incident_id: Mapped[str] = mapped_column(String(32), ForeignKey("incidents.id"), index=True, nullable=False)
    thread_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="running")
    current_step: Mapped[str] = mapped_column(String(64), nullable=False, default="context_collection")
    started_at: Mapped[str] = mapped_column(String(64), nullable=False)
    completed_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    final_result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    approval_decision: Mapped[str | None] = mapped_column(String(32), nullable=True)
    approval_actor: Mapped[str | None] = mapped_column(String(64), nullable=True)
    approval_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    execution_result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    verification_result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
