"""
Prediction-related models: ModelVersion, FeatureSnapshot, PredictionSnapshot,
DataSource, DataSnapshot, DataQualityIssue.
"""

import uuid
from datetime import datetime, date

from sqlalchemy import String, Text, Float, Integer, Boolean, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.models.base import Base, AuditMixin, generate_uuid


class ModelVersion(Base, AuditMixin):
    """A trained model version with metrics and approval gate."""

    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    model_type: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    training_window_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    training_window_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    metrics_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    hyperparameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    artifact_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    approved_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="candidate")


class FeatureSnapshot(Base):
    """
    Feature values at prediction time T — enables reproducibility
    and prevents leakage (spec Appendix I).
    """

    __tablename__ = "feature_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    prediction_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    features_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    data_snapshot_ids: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PredictionSnapshot(Base):
    """
    Versioned prediction output — stored for audit and reproducibility.
    Linked to feature snapshot and model version.
    """

    __tablename__ = "prediction_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    prediction_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=False)
    feature_snapshot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("feature_snapshots.id"), nullable=False)

    # Outputs
    outputs_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # {delay_prob_7d, delay_prob_30d, delay_prob_60d, delay_prob_90d,
    #  p50_date, p80_date, p90_date, target_a_prob, target_c_prob,
    #  survival_curve: [...]}

    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # SHAP-based drivers
    drivers_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    evidence_ids: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DataSource(Base, AuditMixin):
    """External data source health and sync tracking."""

    __tablename__ = "data_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    health_status: Mapped[str] = mapped_column(String(50), default="unknown")
    last_sync: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_interval_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    config_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class DataSnapshot(Base):
    """Point-in-time snapshot of a data source for reproducibility."""

    __tablename__ = "data_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("data_sources.id"), nullable=False)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    record_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DataQualityIssue(Base, AuditMixin):
    """
    Data quality issues: contradictions, staleness, missing data.
    Severity: low, medium, high, critical (spec Section 6.4).
    """

    __tablename__ = "data_quality_issues"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    issue_type: Mapped[str] = mapped_column(String(50), nullable=False)  # contradiction, staleness, missing
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sources: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="open")
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
