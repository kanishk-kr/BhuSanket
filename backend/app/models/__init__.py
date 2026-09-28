"""
SQLAlchemy models — complete data dictionary from BhuSanket specification.
All fact tables carry bitemporal fields (effective_from/to, observed_at, source_id).
"""

from app.models.base import Base, BiTemporalMixin, AuditMixin
from app.models.project import Project, Package, Milestone, Dependency
from app.models.parcel import Parcel, ParcelIdentityMap
from app.models.owner import Owner, ParcelOwnership
from app.models.stage import Stage
from app.models.legal import (
    LegalProcessTemplate,
    TemplateStage,
    StatutoryClockDefinition,
    StatutoryClockInstance,
    LegalCase,
)
from app.models.compensation import Compensation
from app.models.event import Event
from app.models.rr import RRPlan, RRMilestone
from app.models.grievance import Grievance
from app.models.approval import Approval
from app.models.intervention import Intervention, AllowedAction
from app.models.prediction import (
    ModelVersion,
    FeatureSnapshot,
    PredictionSnapshot,
    DataSource,
    DataSnapshot,
    DataQualityIssue,
)
from app.models.alert import Alert
from app.models.user import User, Role
from app.models.audit import AuditLog

__all__ = [
    "Base",
    "BiTemporalMixin",
    "AuditMixin",
    "Project",
    "Package",
    "Milestone",
    "Dependency",
    "Parcel",
    "ParcelIdentityMap",
    "Owner",
    "ParcelOwnership",
    "Stage",
    "LegalProcessTemplate",
    "TemplateStage",
    "StatutoryClockDefinition",
    "StatutoryClockInstance",
    "LegalCase",
    "Compensation",
    "Event",
    "RRPlan",
    "RRMilestone",
    "Grievance",
    "Approval",
    "Intervention",
    "AllowedAction",
    "ModelVersion",
    "FeatureSnapshot",
    "PredictionSnapshot",
    "DataSource",
    "DataSnapshot",
    "DataQualityIssue",
    "Alert",
    "User",
    "Role",
    "AuditLog",
]
