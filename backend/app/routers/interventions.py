"""Intervention routes."""

import uuid
from typing import Annotated
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.intervention import Intervention, AllowedAction
from app.engine.scenario import ALLOWED_ACTIONS
from app.schemas import InterventionCreate, InterventionResponse

router = APIRouter(prefix="/interventions", tags=["Interventions"])


@router.get("/actions")
async def list_allowed_actions():
    """List all allow-listed administrative actions."""
    return [
        {"code": code, **details}
        for code, details in ALLOWED_ACTIONS.items()
    ]


@router.post("", response_model=InterventionResponse, status_code=201)
async def create_intervention(
    data: InterventionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Create and assign an intervention."""
    if data.action_code not in ALLOWED_ACTIONS:
        raise HTTPException(status_code=400, detail="Action not in allow-list (FR-21)")

    intervention = Intervention(
        project_id=data.project_id,
        action_code=data.action_code,
        owner_role=data.owner_role,
        assigned_to=data.assigned_to,
        chosen_reason=data.chosen_reason,
        start_date=date.today(),
        due_date=data.due_date,
    )
    db.add(intervention)
    await db.flush()
    await db.refresh(intervention)
    return InterventionResponse.model_validate(intervention)


@router.get("", response_model=list[InterventionResponse])
async def list_interventions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    project_id: uuid.UUID | None = None,
    status: str | None = None,
):
    """List interventions with optional filtering."""
    query = select(Intervention).order_by(Intervention.created_at.desc())
    if project_id:
        query = query.where(Intervention.project_id == project_id)
    if status:
        query = query.where(Intervention.outcome_status == status)
    result = await db.execute(query)
    return [InterventionResponse.model_validate(i) for i in result.scalars().all()]


@router.patch("/{intervention_id}/complete")
async def complete_intervention(
    intervention_id: uuid.UUID,
    outcome: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Record intervention outcome."""
    result = await db.execute(select(Intervention).where(Intervention.id == intervention_id))
    intervention = result.scalar_one_or_none()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    intervention.outcome = outcome
    intervention.outcome_status = "completed"
    intervention.end_date = date.today()
    return {"status": "completed"}
