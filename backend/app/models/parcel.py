"""
Parcel and ParcelIdentityMap models.
ULPIN-first identity resolution per spec Section 6.2.
"""

import uuid
from datetime import datetime, date

from sqlalchemy import (
    String, Text, Float, Integer, Boolean, Date, DateTime,
    ForeignKey, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry

from app.models.base import Base, BiTemporalMixin, AuditMixin, generate_uuid


class Parcel(Base, BiTemporalMixin, AuditMixin):
    """
    A land parcel identified by ULPIN (14-char Bhu-Aadhaar) or fallback identifiers.
    Carries geometry, land use, criticality weight, and usability status.
    """

    __tablename__ = "parcels"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    # ULPIN-first identity (nullable for parcels not yet in ULPIN)
    ulpin: Mapped[str | None] = mapped_column(String(14), nullable=True, index=True)
    survey_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    khasra_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sub_parcel_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    village_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    village_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tehsil: Mapped[str | None] = mapped_column(String(200), nullable=True)
    district: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Geometry and area
    area_hectares: Mapped[float | None] = mapped_column(Float, nullable=True)
    geometry = mapped_column(Geometry("POLYGON", srid=4326), nullable=True)

    # Classification
    land_use: Mapped[str | None] = mapped_column(String(100), nullable=True)
    scheduled_area_flag: Mapped[bool] = mapped_column(Boolean, default=False)

    # Acquisition status
    acquisition_status: Mapped[str] = mapped_column(
        String(50), default="not_started", nullable=False
    )
    possession_status: Mapped[str] = mapped_column(
        String(50), default="not_granted", nullable=False
    )
    encumbrance_free: Mapped[bool] = mapped_column(Boolean, default=False)
    access_available: Mapped[bool] = mapped_column(Boolean, default=False)

    # Criticality and usability (spec Section 8.2)
    criticality_weight: Mapped[float] = mapped_column(Float, default=0.5)
    usability_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_blocking: Mapped[bool] = mapped_column(Boolean, default=False)

    # Project / Package linkage
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True
    )
    package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("packages.id"), nullable=True
    )

    # Validity interval (for subdivisions/mergers — spec Section J.29)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    identity_maps: Mapped[list["ParcelIdentityMap"]] = relationship(
        back_populates="parcel", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Parcel {self.ulpin or self.survey_no or self.id}>"


class ParcelIdentityMap(Base, AuditMixin):
    """
    Maps a parcel to external identifiers with confidence scoring.
    Resolution follows: ULPIN → geometry overlap → village+survey →
    owner/doc → fuzzy → human confirmation (spec Section 6.2).
    """

    __tablename__ = "parcel_identity_maps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    parcel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parcels.id"), nullable=False
    )
    external_id_type: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str] = mapped_column(String(200), nullable=False)
    match_method: Mapped[str] = mapped_column(String(50), nullable=False)
    match_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reviewer_decision: Mapped[str | None] = mapped_column(String(50), nullable=True)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    parcel: Mapped["Parcel"] = relationship(back_populates="identity_maps")
