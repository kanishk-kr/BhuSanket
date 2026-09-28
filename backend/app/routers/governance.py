"""Governance routes — model performance, audit, data sources."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.prediction import ModelVersion, DataSource
from app.models.audit import AuditLog
from app.schemas import ModelPerformanceResponse, AuditLogResponse

router = APIRouter(prefix="/governance", tags=["Governance"])


@router.get("/models", response_model=list[ModelPerformanceResponse])
async def list_models(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """List all model versions with performance metrics."""
    result = await db.execute(select(ModelVersion).order_by(desc(ModelVersion.created_at)))
    models = result.scalars().all()
    return [
        ModelPerformanceResponse(
            model_id=m.id,
            version=m.version,
            model_type=m.model_type,
            metrics=m.metrics_json or {},
            is_active=m.is_active,
            approved_by=m.approved_by,
        )
        for m in models
    ]


@router.get("/audit", response_model=list[AuditLogResponse])
async def get_audit_log(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    entity_type: str | None = None,
    entity_id: str | None = None,
    limit: int = Query(100, ge=1, le=500),
):
    """Query the hash-chained audit log."""
    query = select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)
    result = await db.execute(query)
    return [AuditLogResponse.model_validate(a) for a in result.scalars().all()]


@router.get("/data-sources")
async def list_data_sources(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """List data source health and sync status."""
    result = await db.execute(select(DataSource))
    sources = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "source_type": s.source_type,
            "health_status": s.health_status,
            "last_sync": s.last_sync.isoformat() if s.last_sync else None,
        }
        for s in sources
    ]
