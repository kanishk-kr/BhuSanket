"""Alert routes."""

import uuid
from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.alert import Alert
from app.schemas import AlertResponse, AlertAcknowledge, AlertSnooze

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    state: str | None = None,
    severity: str | None = None,
    limit: int = Query(50, ge=1, le=200),
):
    """List alerts ordered by priority index."""
    query = select(Alert).order_by(desc(Alert.priority_index)).limit(limit)
    if state:
        query = query.where(Alert.state == state)
    if severity:
        query = query.where(Alert.severity == severity)
    result = await db.execute(query)
    return [AlertResponse.model_validate(a) for a in result.scalars().all()]


@router.post("/{alert_id}/ack")
async def acknowledge_alert(
    alert_id: uuid.UUID,
    data: AlertAcknowledge,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Acknowledge an alert."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.state = "acknowledged"
    alert.acknowledged_at = datetime.now(timezone.utc)
    alert.acknowledged_by = data.acknowledged_by
    return {"status": "acknowledged"}


@router.post("/{alert_id}/snooze")
async def snooze_alert(
    alert_id: uuid.UUID,
    data: AlertSnooze,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Snooze an alert (requires a reason per spec FR-13)."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if not data.reason:
        raise HTTPException(status_code=400, detail="Snooze reason is required")

    alert.state = "snoozed"
    alert.snoozed_until = data.snooze_until
    alert.snooze_reason = data.reason
    return {"status": "snoozed", "until": data.snooze_until}
