"""
Legal process template, template stages, and statutory clock models.
Law is configurable data — adding a regime or state amendment means authoring
data, not code (spec Design Principle 4, Section 5).
"""

import uuid
from datetime import datetime, date
import enum

from sqlalchemy import (
    String, Text, Float, Integer, Boolean, Date, DateTime,
    ForeignKey, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.models.base import Base, AuditMixin, generate_uuid


class LegalProcessTemplate(Base, AuditMixin):
    """
    A versioned legal process template defining the acquisition regime.
    E.g., RFCTLARR 2013, National Highways Act 1956, Gujarat Amendment.
    """

    __tablename__ = "legal_process_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    jurisdiction: Mapped[str] = mapped_column(String(200), nullable=False)
    legal_regime: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Legal review tracking
    legal_review_status: Mapped[str] = mapped_column(
        String(50), default="pending_review"
    )
    reviewed_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    reviewed_on: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Template configuration (constraints, not features — spec Section 5.3)
    template_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    stages: Mapped[list["TemplateStage"]] = relationship(
        back_populates="template", lazy="selectin"
    )
    clock_definitions: Mapped[list["StatutoryClockDefinition"]] = relationship(
        back_populates="template", lazy="selectin"
    )


class TemplateStage(Base, AuditMixin):
    """
    A stage definition within a legal process template.
    Defines allowed transitions, required documents, and owner roles.
    """

    __tablename__ = "template_stages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legal_process_templates.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    section_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Dependencies and transitions
    depends_on_stages: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    allowed_transitions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Required documents and owner roles
    required_documents: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    owner_role: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Duration expectations
    expected_duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    silence_threshold_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    template: Mapped["LegalProcessTemplate"] = relationship(back_populates="stages")


class ExpiryConsequence(str, enum.Enum):
    LAPSE = "LAPSE"
    RESCISSION = "RESCISSION"
    REVIEW = "REVIEW"
    ADDITIONAL_APPROVAL = "ADDITIONAL_APPROVAL"
    RE_INITIATION = "RE_INITIATION"
    NONE = "NONE"


class StatutoryClockDefinition(Base, AuditMixin):
    """
    A statutory clock definition per spec Appendix A.1.
    Defines the legal time limit for a governed step.
    """

    __tablename__ = "statutory_clock_definitions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legal_process_templates.id"), nullable=False
    )
    clock_code: Mapped[str] = mapped_column(String(50), nullable=False)
    section_reference: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Trigger and end events
    trigger_event: Mapped[str] = mapped_column(String(100), nullable=False)
    end_event: Mapped[str] = mapped_column(String(100), nullable=False)

    # Duration
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_description: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Pause and extension rules
    pause_rules: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    extension_rule: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Consequence
    expiry_consequence: Mapped[str] = mapped_column(
        String(50), default=ExpiryConsequence.REVIEW.value, nullable=False
    )
    consequence_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Validity
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Legal review
    legal_review_status: Mapped[str] = mapped_column(
        String(50), default="pending_review"
    )

    template: Mapped["LegalProcessTemplate"] = relationship(
        back_populates="clock_definitions"
    )


class ClockAlertState(str, enum.Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"
    CRITICAL = "CRITICAL"
    CANNOT_EVALUATE = "CANNOT_EVALUATE"


class StatutoryClockInstance(Base, AuditMixin):
    """
    A running instance of a statutory clock for a specific project stage.
    Tracks start, pauses, deadline, extensions, and alert state.
    """

    __tablename__ = "statutory_clock_instances"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stages.id"), nullable=False
    )
    clock_definition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("statutory_clock_definitions.id"), nullable=False
    )
    start_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Clock state
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    days_remaining: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deadline_risk: Mapped[float | None] = mapped_column(Float, nullable=True)
    alert_state: Mapped[str] = mapped_column(
        String(20), default=ClockAlertState.GREEN.value
    )

    # Pauses and extensions
    pause_intervals_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    total_paused_days: Mapped[int] = mapped_column(Integer, default=0)
    extension_count: Mapped[int] = mapped_column(Integer, default=0)

    # Completion
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    breached: Mapped[bool] = mapped_column(Boolean, default=False)


class LegalCase(Base, AuditMixin):
    """
    A court case or reference affecting one or more parcels.
    Stays cause clock pauses per template rules.
    """

    __tablename__ = "legal_cases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    case_no: Mapped[str] = mapped_column(String(200), nullable=False)
    court: Mapped[str] = mapped_column(String(200), nullable=False)
    case_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parcel_ids: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True
    )

    # Stay tracking
    stay_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    stay_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    stay_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    stay_scope: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Case progress
    filing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_hearing: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_order_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    order_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
