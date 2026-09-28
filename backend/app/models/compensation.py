"""
Compensation model — tracks assessed, sanctioned, and disbursed amounts per parcel/owner.
"""

import uuid
from datetime import date

from sqlalchemy import String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, BiTemporalMixin, AuditMixin, generate_uuid


class Compensation(Base, BiTemporalMixin, AuditMixin):
    """
    Compensation record for a parcel-owner pair.
    Tracks the full lifecycle: assessment → sanction → disbursal.
    """

    __tablename__ = "compensations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    parcel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parcels.id"), nullable=False
    )
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("owners.id"), nullable=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )

    # Amounts
    assessed_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    sanctioned_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    disbursed_amount: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Dates
    assessment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sanction_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    disbursal_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Status
    payment_status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )  # pending, sanctioned, disbursed, failed, deposited_in_court
    deposited_in_court_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    payment_failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
