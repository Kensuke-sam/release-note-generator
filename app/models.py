from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def generate_id() -> str:
    return str(uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )


class DeploymentRecord(Base, TimestampMixin):
    __tablename__ = "deployment_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    environment: Mapped[str] = mapped_column(String(255), nullable=False)
    change_summary: Mapped[str] = mapped_column(Text, nullable=False)
    issue_refs: Mapped[list[str]] = mapped_column(JSON, nullable=False)


class ReleaseNoteDraft(Base, TimestampMixin):
    __tablename__ = "release_note_drafts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    deployment_record_id: Mapped[str] = mapped_column(
        ForeignKey("deployment_records.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    headline: Mapped[str] = mapped_column(String(255), nullable=False)
    audience_summary: Mapped[str] = mapped_column(Text, nullable=False)
    rollback_plan: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(255), nullable=False)
