"""
Owner model — pseudonymised per spec Section 12 (privacy).
Owners are linked to parcels via a many-to-many ownership table.
"""

import uuid
from datetime import date

from sqlalchemy import String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, BiTemporalMixin, AuditMixin, generate_uuid


class Owner(Base, BiTemporalMixin, AuditMixin):
    """
    A pseudonymised land owner or interested person.
    Identity is never exposed in public views; accessed only by authorised revenue officials.
    """

    __tablename__ = "owners"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    # Pseudonymised identifier (never real name in model features)
    owner_pid: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    owner_type: Mapped[str] = mapped_column(
        String(50), default="individual", nullable=False
    )  # individual, joint, institution, government
    deceased_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    heir_count: Mapped[int | None] = mapped_column(default=None)
    relationship_flags: Mapped[str | None] = mapped_column(String(200), nullable=True)

    ownerships: Mapped[list["ParcelOwnership"]] = relationship(
        back_populates="owner", lazy="selectin"
    )


class ParcelOwnership(Base, BiTemporalMixin, AuditMixin):
    """
    Many-to-many link between parcels and owners with share information.
    Carries validity interval for ownership changes.
    """

    __tablename__ = "parcel_ownerships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    parcel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parcels.id"), nullable=False
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("owners.id"), nullable=False
    )
    share: Mapped[float] = mapped_column(Float, default=1.0)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    owner: Mapped["Owner"] = relationship(back_populates="ownerships")
