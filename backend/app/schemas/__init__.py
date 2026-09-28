"""
Pydantic schemas for API request/response validation.
"""

from __future__ import annotations

import uuid
from datetime import datetime
import datetime as dt
from pydantic import BaseModel, Field, ConfigDict


# ─── Auth ────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserBrief | None = None


class UserBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    full_name: str
    role_name: str | None = None
    jurisdiction: str | None = None


# ─── Projects ────────────────────────────────────────────────────────────
class ProjectBase(BaseModel):
    name: str
    code: str | None = None
    requiring_body_id: str | None = None
    regime_id: str | None = None
    jurisdiction: str | None = None
    state: str | None = None
    district: str | None = None
    sector: str | None = None
    budget: float | None = None
    status: str = "active"


class ProjectCreate(ProjectBase):
    template_id: uuid.UUID | None = None


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    template_id: uuid.UUID | None = None
    total_parcels: int | None = None
    total_area_hectares: float | None = None
    land_acquired_pct: float | None = None
    construction_enabling_pct: float | None = None
    current_risk_score: float | None = None
    risk_momentum: float | None = None
    risk_momentum_class: str | None = None
    model_confidence: float | None = None
    data_confidence: float | None = None
    created_at: datetime


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int
    page: int
    page_size: int


# ─── Stages ──────────────────────────────────────────────────────────────
class StageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    status: str
    sequence_order: int
    original_commitment_date: dt.date | None = None
    approved_baseline_date: dt.date | None = None
    forecast_date: dt.date | None = None
    actual_start: dt.date | None = None
    actual_end: dt.date | None = None
    delay_probability: float | None = None
    p50_date: dt.date | None = None
    p80_date: dt.date | None = None
    p90_date: dt.date | None = None
    baseline_integrity_score: float | None = None


# ─── Risk ────────────────────────────────────────────────────────────────
class RiskResponse(BaseModel):
    project_id: uuid.UUID
    risk_score: float
    model_confidence: float | None = None
    data_confidence: float | None = None
    risk_momentum: float | None = None
    risk_momentum_class: str | None = None
    risk_trajectory: list[float] | None = None
    prediction_time: datetime | None = None


class RiskTimelinePoint(BaseModel):
    date: date
    risk_score: float
    model_confidence: float | None = None


class RiskTimelineResponse(BaseModel):
    project_id: uuid.UUID
    timeline: list[RiskTimelinePoint]


# ─── Statutory Clocks ────────────────────────────────────────────────────
class ClockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    clock_code: str | None = None
    section_reference: str | None = None
    description: str | None = None
    start_date: dt.date | None = None
    deadline: dt.date | None = None
    days_remaining: int | None = None
    deadline_risk: float | None = None
    alert_state: str
    extension_count: int = 0
    total_paused_days: int = 0
    breached: bool = False
    consequence: str | None = None


# ─── Parcels ─────────────────────────────────────────────────────────────
class ParcelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    ulpin: str | None = None
    survey_no: str | None = None
    village_name: str | None = None
    district: str | None = None
    area_hectares: float | None = None
    acquisition_status: str
    possession_status: str
    criticality_weight: float
    usability_score: float
    is_blocking: bool


class BlockingParcelsResponse(BaseModel):
    project_id: uuid.UUID
    total_parcels: int
    blocking_parcels: list[ParcelResponse]
    construction_enabling_pct: float | None = None
    land_acquired_pct: float | None = None


# ─── Evidence & Explanations ─────────────────────────────────────────────
class EvidenceRecord(BaseModel):
    source: str
    record_type: str
    description: str
    date: dt.date | None = None
    confidence: float = 1.0
    grade: str = "HIGH"  # HIGH, MEDIUM, LOW


class DriverExplanation(BaseModel):
    feature_name: str
    display_name: str
    contribution: float
    direction: str  # positive, negative
    description: str
    evidence: list[EvidenceRecord] = []
    grade: str = "HIGH"


class ExplanationResponse(BaseModel):
    project_id: uuid.UUID
    risk_score: float
    summary: str
    drivers: list[DriverExplanation]
    total_evidence_records: int


# ─── Scenarios ───────────────────────────────────────────────────────────
class ScenarioRequest(BaseModel):
    actions: list[ScenarioAction]


class ScenarioAction(BaseModel):
    action_code: str
    delta: dict  # e.g., {"compensation_lag_days": -30}


class ScenarioResponse(BaseModel):
    project_id: uuid.UUID
    baseline_risk: float
    scenario_risk: float
    risk_change: float
    actions: list[ScenarioAction]
    label: str = "This is a model simulation, not a guarantee."
    p50_date_baseline: dt.date | None = None
    p50_date_scenario: dt.date | None = None


# ─── Alerts ──────────────────────────────────────────────────────────────
class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    alert_type: str
    title: str
    description: str | None = None
    severity: str
    priority_index: float | None = None
    owner_role: str | None = None
    state: str
    due_date: dt.date | None = None
    created_at: datetime


class AlertAcknowledge(BaseModel):
    acknowledged_by: str


class AlertSnooze(BaseModel):
    snooze_until: datetime
    reason: str


# ─── Interventions ───────────────────────────────────────────────────────
class InterventionCreate(BaseModel):
    project_id: uuid.UUID
    action_code: str
    owner_role: str | None = None
    assigned_to: str | None = None
    chosen_reason: str | None = None
    due_date: dt.date | None = None


class InterventionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    action_code: str
    owner_role: str | None = None
    assigned_to: str | None = None
    start_date: dt.date | None = None
    due_date: dt.date | None = None
    outcome_status: str
    modelled_risk_before: float | None = None
    modelled_risk_after: float | None = None
    created_at: datetime


# ─── Data Quality ────────────────────────────────────────────────────────
class DataQualityResponse(BaseModel):
    project_id: uuid.UUID
    overall_confidence: float | None = None
    domain_confidence: dict = {}  # {project, compensation, legal, land_records, rr}
    issues: list[DataQualityIssueResponse] = []
    last_sync: datetime | None = None


class DataQualityIssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    issue_type: str
    severity: str
    description: str | None = None
    status: str


# ─── Events ──────────────────────────────────────────────────────────────
class EventCreate(BaseModel):
    entity_id: uuid.UUID
    entity_type: str
    event_type: str
    effective_at: datetime
    source_id: str | None = None
    confidence: float = 1.0
    payload: dict | None = None


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    entity_id: uuid.UUID
    entity_type: str
    event_type: str
    effective_at: datetime
    observed_at: datetime
    confidence: float
    payload: dict | None = None


# ─── Dashboard / Command Center ─────────────────────────────────────────
class CommandCenterResponse(BaseModel):
    total_projects: int
    at_risk_projects: int
    critical_clock_threats: int
    blocking_parcels_count: int
    pending_interventions: int
    data_contradictions: int
    hero_metrics: HeroMetrics
    top_alerts: list[AlertResponse]
    deteriorating_projects: list[ProjectResponse]


class HeroMetrics(BaseModel):
    land_acquired_pct: float
    construction_enabling_pct: float
    critical_parcels_resolved_pct: float
    avg_risk_score: float
    statutory_clocks_at_risk: int


# ─── GIS ─────────────────────────────────────────────────────────────────
class GeoProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    risk_score: float | None = None
    status: str
    lat: float | None = None
    lng: float | None = None
    geometry_geojson: dict | None = None


# ─── Governance ──────────────────────────────────────────────────────────
class ModelPerformanceResponse(BaseModel):
    model_id: uuid.UUID
    version: str
    model_type: str
    metrics: dict
    is_active: bool
    approved_by: str | None = None


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    actor: str
    action: str
    entity_type: str | None = None
    entity_id: str | None = None
    timestamp: datetime
    hash: str | None = None


# Fix forward references
TokenResponse.model_rebuild()
ScenarioRequest.model_rebuild()
CommandCenterResponse.model_rebuild()
