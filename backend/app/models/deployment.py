from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.base import Base


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    service_id: Mapped[str] = mapped_column(String(64), nullable=False)
    service_name: Mapped[str] = mapped_column(String(64), nullable=False)
    author: Mapped[str] = mapped_column(String(64), nullable=False)
    author_email: Mapped[str] = mapped_column(String(128), nullable=False)
    deployed_at: Mapped[str] = mapped_column(String(64), nullable=False)
    time_label: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    commit: Mapped[str] = mapped_column(String(64), nullable=False)
    commit_message: Mapped[str] = mapped_column(Text, nullable=False)
    files_changed: Mapped[str] = mapped_column(String(64), nullable=False)
    diff_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
