"""Grievance model."""

import uuid
from datetime import date

from sqlalchemy import String, Text, Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, BiTemporalMixin, AuditMixin, generate_uuid


class Grievance(Base, BiTemporalMixin, AuditMixin):
    __tablename__ = "grievances"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    parcel_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("parcels.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    text_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="open")
    verified_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
