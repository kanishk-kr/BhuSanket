"""
Base model class and reusable mixins for bitemporal tracking and auditing.
Every fact table in BhuSanket carries bitemporal fields per Section 6.5 of the spec.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Float, func, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base as _Base


# Re-export for convenience
Base = _Base


class BiTemporalMixin:
    """
    Bitemporal-lite history mixin.
    - effective_from / effective_to: when the fact was true in the real world
    - observed_at: when the system learned about it
    - source_id: which data source provided this fact
    Nothing is overwritten; corrections create new rows that supersede.
    """

    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    effective_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    source_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )


class AuditMixin:
    """Timestamps for create/update tracking."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def generate_uuid() -> uuid.UUID:
    return uuid.uuid4()
