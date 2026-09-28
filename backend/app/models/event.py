"""
Event model — append-only event store per spec Appendix C.
Events are never overwritten; corrections create new events that supersede earlier ones.
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.models.base import Base, generate_uuid


class Event(Base):
    """
    An append-only event fact.
    Core of the event-sourced architecture: every state change is an event.
    """

    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Bitemporal
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Source and confidence
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    verification_status: Mapped[str] = mapped_column(
        String(50), default="unverified"
    )  # unverified, verified, rejected

    # Payload (flexible event data)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Supersession chain
    supersedes_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("events.id"), nullable=True
    )

    # Provenance (for document-extracted events — Phase 2)
    document_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    document_page: Mapped[str | None] = mapped_column(String(50), nullable=True)
    extraction_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return f"<Event {self.event_type} on {self.entity_type}:{self.entity_id}>"
