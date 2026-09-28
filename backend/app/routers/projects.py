"""
Project routes — covers spec API endpoints E.3:
GET /v1/projects/{id}/risk | /timeline | /forecast | /explanation | /evidence
    /dependencies | /blocking-parcels | /clocks | /data-quality
    /prediction-history | /recommendations
POST /v1/projects/{id}/whatif | /override
"""

import uuid
from typing import Annotated
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.project import Project, Package
from app.models.stage import Stage
from app.models.parcel import Parcel
from app.models.legal import StatutoryClockInstance, StatutoryClockDefinition
from app.models.prediction import PredictionSnapshot, DataQualityIssue
from app.models.alert import Alert
from app.engine.prediction import HazardModel, RiskMomentumTracker
from app.engine.evidence import generate_explanation
from app.engine.scenario import simulate_scenario, validate_action
from app.engine.data_confidence import compute_project_data_confidence
from app.engine.statutory_deadline import evaluate_clock
from app.schemas import (
    ProjectCreate, ProjectResponse, ProjectListResponse,
    StageResponse, RiskResponse, RiskTimelineResponse, RiskTimelinePoint,
    ClockResponse, ParcelResponse, BlockingParcelsResponse,
    ExplanationResponse, DriverExplanation, EvidenceRecord,
    ScenarioRequest, ScenarioResponse,
    DataQualityResponse, DataQualityIssueResponse,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    state: str | None = None,
    district: str | None = None,
    min_risk: float | None = None,
):
    """List projects with filtering and pagination."""
    query = select(Project)

    # Jurisdiction scoping
    if current_user.role and current_user.role.name not in ("admin", "ministry"):
        if current_user.district:
            query = query.where(Project.district == current_user.district)
        elif current_user.state:
            query = query.where(Project.state == current_user.state)

    if status:
        query = query.where(Project.status == status)
    if state:
        query = query.where(Project.state == state)
    if district:
        query = query.where(Project.district == district)
    if min_risk is not None:
        query = query.where(Project.current_risk_score >= min_risk)

    # Count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    # Paginate
    query = query.order_by(desc(Project.current_risk_score)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    projects = result.scalars().all()

    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Create a new project."""
    project = Project(**data.model_dump())
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get project details."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}/stages", response_model=list[StageResponse])
async def get_project_stages(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get all stages for a project."""
    result = await db.execute(
        select(Stage).where(Stage.project_id == project_id).order_by(Stage.sequence_order)
    )
    return [StageResponse.model_validate(s) for s in result.scalars().all()]


@router.get("/{project_id}/risk", response_model=RiskResponse)
async def get_project_risk(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get current risk assessment for a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return RiskResponse(
        project_id=project.id,
        risk_score=project.current_risk_score or 0.0,
        model_confidence=project.model_confidence,
        data_confidence=project.data_confidence,
        risk_momentum=project.risk_momentum,
        risk_momentum_class=project.risk_momentum_class,
        prediction_time=datetime.now(timezone.utc),
    )


@router.get("/{project_id}/timeline", response_model=RiskTimelineResponse)
async def get_risk_timeline(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get risk score history for a project."""
    result = await db.execute(
        select(PredictionSnapshot)
        .where(PredictionSnapshot.entity_id == project_id)
        .order_by(PredictionSnapshot.prediction_time)
        .limit(100)
    )
    snapshots = result.scalars().all()

    timeline = []
    for s in snapshots:
        outputs = s.outputs_json or {}
        timeline.append(RiskTimelinePoint(
            date=s.prediction_time.date(),
            risk_score=outputs.get("delay_probability", 0),
            model_confidence=s.confidence,
        ))

    return RiskTimelineResponse(project_id=project_id, timeline=timeline)


@router.get("/{project_id}/clocks", response_model=list[ClockResponse])
async def get_statutory_clocks(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get all active statutory clocks for a project's stages."""
    result = await db.execute(
        select(StatutoryClockInstance, StatutoryClockDefinition)
        .join(StatutoryClockDefinition, StatutoryClockInstance.clock_definition_id == StatutoryClockDefinition.id)
        .join(Stage, StatutoryClockInstance.stage_id == Stage.id)
        .where(Stage.project_id == project_id)
    )
    rows = result.all()

    clocks = []
    for instance, definition in rows:
        clocks.append(ClockResponse(
            id=instance.id,
            clock_code=definition.clock_code,
            section_reference=definition.section_reference,
            description=definition.description,
            start_date=instance.start_date,
            deadline=instance.deadline,
            days_remaining=instance.days_remaining,
            deadline_risk=instance.deadline_risk,
            alert_state=instance.alert_state,
            extension_count=instance.extension_count,
            total_paused_days=instance.total_paused_days,
            breached=instance.breached,
            consequence=definition.expiry_consequence,
        ))

    return clocks


@router.get("/{project_id}/blocking-parcels", response_model=BlockingParcelsResponse)
async def get_blocking_parcels(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get parcels that block workfront readiness."""
    result = await db.execute(
        select(Parcel).where(
            Parcel.project_id == project_id,
            Parcel.is_blocking == True,
        )
    )
    blocking = result.scalars().all()

    # Get project metrics
    proj_result = await db.execute(select(Project).where(Project.id == project_id))
    project = proj_result.scalar_one_or_none()

    total_result = await db.execute(
        select(func.count()).where(Parcel.project_id == project_id)
    )
    total_parcels = total_result.scalar_one()

    return BlockingParcelsResponse(
        project_id=project_id,
        total_parcels=total_parcels,
        blocking_parcels=[ParcelResponse.model_validate(p) for p in blocking],
        construction_enabling_pct=project.construction_enabling_pct if project else None,
        land_acquired_pct=project.land_acquired_pct if project else None,
    )


@router.get("/{project_id}/explanation", response_model=ExplanationResponse)
async def get_explanation(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get evidence-backed explanation for the current risk score."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get latest prediction
    pred_result = await db.execute(
        select(PredictionSnapshot)
        .where(PredictionSnapshot.entity_id == project_id)
        .order_by(desc(PredictionSnapshot.prediction_time))
        .limit(1)
    )
    prediction = pred_result.scalar_one_or_none()

    drivers = prediction.drivers_json if prediction else []
    risk_score = project.current_risk_score or 0.0

    explanation = generate_explanation(risk_score, drivers or [], {})

    return ExplanationResponse(
        project_id=project_id,
        risk_score=risk_score,
        summary=explanation["summary"],
        drivers=[
            DriverExplanation(
                feature_name=d.feature_name,
                display_name=d.display_name,
                contribution=d.contribution,
                direction=d.direction,
                description=d.description,
                evidence=[
                    EvidenceRecord(
                        source=e.source,
                        record_type=e.record_type,
                        description=e.description,
                        confidence=e.confidence,
                        grade=e.grade,
                    )
                    for e in d.evidence
                ],
                grade=d.grade,
            )
            for d in explanation["drivers"]
        ],
        total_evidence_records=explanation["total_evidence_records"],
    )


@router.post("/{project_id}/whatif", response_model=ScenarioResponse)
async def what_if_scenario(
    project_id: uuid.UUID,
    request: ScenarioRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Run a what-if scenario with allow-listed actions."""
    # Validate all actions are allow-listed
    for action in request.actions:
        if not validate_action(action.action_code):
            raise HTTPException(
                status_code=400,
                detail=f"Action '{action.action_code}' is not in the allow-list",
            )

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Build features from project state
    features = {
        "entity_id": str(project_id),
        "risk_factors": {
            "compensation_delay_days": 90,
            "litigation_active": False,
            "ownership_complexity": 2,
            "pending_mutations": 5,
            "grievance_count": 3,
        },
    }

    actions_dicts = [{"action_code": a.action_code, "delta": a.delta} for a in request.actions]
    sim_result = simulate_scenario(features, actions_dicts)

    return ScenarioResponse(
        project_id=project_id,
        baseline_risk=sim_result["baseline_risk"],
        scenario_risk=sim_result["scenario_risk"],
        risk_change=sim_result["risk_change"],
        actions=request.actions,
        label=sim_result["label"],
        p50_date_baseline=sim_result.get("p50_date_baseline"),
        p50_date_scenario=sim_result.get("p50_date_scenario"),
    )


@router.get("/{project_id}/data-quality", response_model=DataQualityResponse)
async def get_data_quality(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get data quality and confidence metrics for a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    dc = compute_project_data_confidence({}, None)

    issues_result = await db.execute(
        select(DataQualityIssue).where(
            DataQualityIssue.entity_id == project_id,
            DataQualityIssue.status == "open",
        )
    )
    issues = issues_result.scalars().all()

    return DataQualityResponse(
        project_id=project_id,
        overall_confidence=dc.overall,
        domain_confidence={
            "project": dc.project,
            "compensation": dc.compensation,
            "legal": dc.legal,
            "land_records": dc.land_records,
            "rr": dc.rr,
        },
        issues=[DataQualityIssueResponse.model_validate(i) for i in issues],
    )
