"""
Intervention model — allow-listed actions from playbooks.
Logged for causal estimation (spec Section 10.2).
"""

import uuid
from datetime import date

from sqlalchemy import String, Text, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.models.base import Base, BiTemporalMixin, AuditMixin, generate_uuid


class AllowedAction(Base, AuditMixin):
    """Allow-listed administrative actions that can be recommended."""

    __tablename__ = "allowed_actions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    typical_duration_days: Mapped[int | None] = mapped_column(default=None)
    active: Mapped[bool] = mapped_column(default=True)


class Intervention(Base, BiTemporalMixin, AuditMixin):
    """
    A tracked intervention/action taken on a project.
    Records what, when, who, why chosen, eligibility, and outcome for causal estimation.
    """

    __tablename__ = "interventions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    action_code: Mapped[str] = mapped_column(String(50), ForeignKey("allowed_actions.code"), nullable=False)
    owner_role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(200), nullable=True)
    chosen_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    eligibility_criteria: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome_status: Mapped[str] = mapped_column(String(50), default="pending")
    modelled_risk_before: Mapped[float | None] = mapped_column(default=None)
    modelled_risk_after: Mapped[float | None] = mapped_column(default=None)
