"""Event ingestion routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.event import Event
from app.schemas import EventCreate, EventResponse

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=EventResponse, status_code=201)
async def ingest_event(
    data: EventCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Ingest a new event into the append-only event store."""
    event = Event(
        entity_id=data.entity_id,
        entity_type=data.entity_type,
        event_type=data.event_type,
        effective_at=data.effective_at,
        source_id=data.source_id,
        confidence=data.confidence,
        payload=data.payload,
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return EventResponse.model_validate(event)


@router.post("/batch", response_model=list[EventResponse], status_code=201)
async def ingest_events_batch(
    events: list[EventCreate],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Batch ingest events."""
    created = []
    for data in events:
        event = Event(
            entity_id=data.entity_id,
            entity_type=data.entity_type,
            event_type=data.event_type,
            effective_at=data.effective_at,
            source_id=data.source_id,
            confidence=data.confidence,
            payload=data.payload,
        )
        db.add(event)
        created.append(event)

    await db.flush()
    for e in created:
        await db.refresh(e)
    return [EventResponse.model_validate(e) for e in created]


@router.get("", response_model=list[EventResponse])
async def list_events(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    entity_id: uuid.UUID | None = None,
    event_type: str | None = None,
    limit: int = 50,
):
    """Query events with optional filters."""
    query = select(Event).order_by(Event.observed_at.desc()).limit(limit)
    if entity_id:
        query = query.where(Event.entity_id == entity_id)
    if event_type:
        query = query.where(Event.event_type == event_type)
    result = await db.execute(query)
    return [EventResponse.model_validate(e) for e in result.scalars().all()]
