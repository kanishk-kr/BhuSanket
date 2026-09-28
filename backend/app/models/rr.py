"""
Rehabilitation & Resettlement (R&R) models.
"""

import uuid
from datetime import date

from sqlalchemy import String, Text, Integer, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.models.base import Base, BiTemporalMixin, AuditMixin, generate_uuid


class RRPlan(Base, BiTemporalMixin, AuditMixin):
    __tablename__ = "rr_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    total_families: Mapped[int | None] = mapped_column(Integer, nullable=True)
    families_resettled: Mapped[int | None] = mapped_column(Integer, nullable=True)
    site_readiness: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")


class RRMilestone(Base, AuditMixin):
    __tablename__ = "rr_milestones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    rr_plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rr_plans.id"), nullable=False)
    milestone: Mapped[str] = mapped_column(String(300), nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, default=False)
