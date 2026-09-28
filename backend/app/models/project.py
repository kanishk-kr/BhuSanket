"""
Project, Package, Milestone, and Dependency models.
Covers the project entity and its structural decomposition into segments.
"""

import uuid
from datetime import datetime, date

from sqlalchemy import (
    String, Text, Float, Integer, Date, DateTime,
    ForeignKey, Enum as SAEnum, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry

from app.models.base import Base, BiTemporalMixin, AuditMixin, generate_uuid

import enum


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    DELAYED = "delayed"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project(Base, BiTemporalMixin, AuditMixin):
    """
    A land acquisition project (e.g., a highway corridor).
    Links to a legal regime template and a requiring body.
    """

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    code: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    requiring_body_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    regime_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("legal_process_templates.id"),
        nullable=True,
    )
    jurisdiction: Mapped[str | None] = mapped_column(String(200), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    geometry = mapped_column(Geometry("GEOMETRY", srid=4326), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default=ProjectStatus.ACTIVE.value, nullable=False
    )
    total_parcels: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_area_hectares: Mapped[float | None] = mapped_column(Float, nullable=True)
    land_acquired_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    construction_enabling_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Risk tracking
    current_risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_momentum: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_momentum_class: Mapped[str | None] = mapped_column(String(20), nullable=True)
    model_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    packages: Mapped[list["Package"]] = relationship(back_populates="project", lazy="selectin")
    stages: Mapped[list["Stage"]] = relationship(back_populates="project", lazy="selectin")
    milestones: Mapped[list["Milestone"]] = relationship(back_populates="project", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Project {self.code or self.id}: {self.name}>"


class Package(Base, BiTemporalMixin, AuditMixin):
    """
    A segment of a linear project (e.g., chainage km 0-10).
    Contains parcels and has a need-by date for construction.
    """

    __tablename__ = "packages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    chainage_start: Mapped[float | None] = mapped_column(Float, nullable=True)
    chainage_end: Mapped[float | None] = mapped_column(Float, nullable=True)
    geometry = mapped_column(Geometry("GEOMETRY", srid=4326), nullable=True)
    need_by_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")

    project: Mapped["Project"] = relationship(back_populates="packages")

    def __repr__(self) -> str:
        return f"<Package {self.id}: ch {self.chainage_start}-{self.chainage_end}>"


class Milestone(Base, AuditMixin):
    """Project-level critical milestones."""

    __tablename__ = "milestones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    critical_milestone_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    depends_on: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="milestones")


class DependencyType(str, enum.Enum):
    STAGE_TO_STAGE = "stage_to_stage"
    PARCEL_TO_WORKFRONT = "parcel_to_workfront"
    CLEARANCE_TO_POSSESSION = "clearance_to_possession"
    APPROVAL_TO_STAGE = "approval_to_stage"


class Dependency(Base, AuditMixin):
    """
    Typed dependency edge in the project dependency graph.
    Links acquisition stages, parcel groups, clearances, and construction packages.
    """

    __tablename__ = "dependencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    from_node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    from_node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    to_node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    to_node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    dependency_type: Mapped[str] = mapped_column(String(50), nullable=False)
    lag_days: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)


# Forward reference for Stage
from app.models.stage import Stage  # noqa: E402
