"""
Stage model — represents a step in the land acquisition process.
Each stage belongs to a project or package and tracks three date concepts:
original commitment, approved baseline, and forecast (per spec Section 7.5).
"""

import uuid
from datetime import datetime, date
import enum

from sqlalchemy import (
    String, Text, Float, Integer, Date, DateTime,
    ForeignKey, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.models.base import Base, BiTemporalMixin, AuditMixin, generate_uuid


class StageStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    BLOCKED = "blocked"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class Stage(Base, BiTemporalMixin, AuditMixin):
    """
    A single acquisition stage (e.g., SIA, Preliminary Notification, Declaration, Award).
    Linked to a template stage definition for legal compliance.
    """

    __tablename__ = "stages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("packages.id"), nullable=True
    )
    template_stage_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("template_stages.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sequence_order: Mapped[int] = mapped_column(Integer, default=0)

    # Three date concepts (spec Section 7.5 — baseline integrity)
    original_commitment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    approved_baseline_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    proposed_revision_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    forecast_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Actual dates
    planned_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_end: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default=StageStatus.NOT_STARTED.value, nullable=False
    )

    # Risk fields (denormalized from latest prediction)
    delay_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    p50_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    p80_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    p90_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Baseline integrity
    baseline_change_count: Mapped[int] = mapped_column(Integer, default=0)
    baseline_integrity_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="stages")

    def __repr__(self) -> str:
        return f"<Stage {self.name} [{self.status}]>"

    @property
    def is_open(self) -> bool:
        return self.status in (
            StageStatus.NOT_STARTED.value,
            StageStatus.IN_PROGRESS.value,
            StageStatus.DELAYED.value,
            StageStatus.BLOCKED.value,
        )

    @property
    def days_elapsed(self) -> int | None:
        if self.actual_start:
            end = self.actual_end or datetime.utcnow().date()
            return (end - self.actual_start).days
        return None


# Avoid circular import
from app.models.project import Project  # noqa: E402, F811
