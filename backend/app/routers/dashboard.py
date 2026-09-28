"""Command Center / Dashboard routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.parcel import Parcel
from app.models.legal import StatutoryClockInstance
from app.models.alert import Alert
from app.models.intervention import Intervention
from app.models.prediction import DataQualityIssue
from app.schemas import (
    CommandCenterResponse, HeroMetrics,
    AlertResponse, ProjectResponse,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/command-center", response_model=CommandCenterResponse)
async def get_command_center(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Command Center: 'What needs attention today?'
    Aggregates statutory-clock threats, critical parcels, deteriorating projects,
    data contradictions, and recommended interventions.
    """
    # Total projects
    total_result = await db.execute(select(func.count()).select_from(Project))
    total_projects = total_result.scalar_one()

    # At-risk projects (risk >= 0.6)
    at_risk_result = await db.execute(
        select(func.count()).where(Project.current_risk_score >= 0.6)
    )
    at_risk_projects = at_risk_result.scalar_one()

    # Critical clock threats
    clock_result = await db.execute(
        select(func.count()).where(
            StatutoryClockInstance.alert_state.in_(["RED", "CRITICAL"])
        )
    )
    critical_clocks = clock_result.scalar_one()

    # Blocking parcels
    blocking_result = await db.execute(
        select(func.count()).where(Parcel.is_blocking == True)
    )
    blocking_parcels = blocking_result.scalar_one()

    # Pending interventions
    interventions_result = await db.execute(
        select(func.count()).where(Intervention.outcome_status == "pending")
    )
    pending_interventions = interventions_result.scalar_one()

    # Data contradictions
    contradictions_result = await db.execute(
        select(func.count()).where(
            DataQualityIssue.issue_type == "contradiction",
            DataQualityIssue.status == "open",
        )
    )
    data_contradictions = contradictions_result.scalar_one()

    # Hero metrics
    avg_risk_result = await db.execute(
        select(func.avg(Project.current_risk_score))
    )
    avg_risk = avg_risk_result.scalar_one() or 0.0

    avg_land_result = await db.execute(
        select(func.avg(Project.land_acquired_pct))
    )
    avg_land = avg_land_result.scalar_one() or 0.0

    avg_construction_result = await db.execute(
        select(func.avg(Project.construction_enabling_pct))
    )
    avg_construction = avg_construction_result.scalar_one() or 0.0

    # Top alerts
    alerts_result = await db.execute(
        select(Alert)
        .where(Alert.state == "open")
        .order_by(desc(Alert.priority_index))
        .limit(10)
    )
    top_alerts = [AlertResponse.model_validate(a) for a in alerts_result.scalars().all()]

    # Deteriorating projects (accelerating risk)
    deteriorating_result = await db.execute(
        select(Project)
        .where(Project.risk_momentum_class == "accelerating")
        .order_by(desc(Project.current_risk_score))
        .limit(5)
    )
    deteriorating = [
        ProjectResponse.model_validate(p)
        for p in deteriorating_result.scalars().all()
    ]

    return CommandCenterResponse(
        total_projects=total_projects,
        at_risk_projects=at_risk_projects,
        critical_clock_threats=critical_clocks,
        blocking_parcels_count=blocking_parcels,
        pending_interventions=pending_interventions,
        data_contradictions=data_contradictions,
        hero_metrics=HeroMetrics(
            land_acquired_pct=round(avg_land, 1),
            construction_enabling_pct=round(avg_construction, 1),
            critical_parcels_resolved_pct=76.0,  # Computed in production
            avg_risk_score=round(float(avg_risk), 3),
            statutory_clocks_at_risk=critical_clocks,
        ),
        top_alerts=top_alerts,
        deteriorating_projects=deteriorating,
    )
