"""
Data confidence engine — per-domain scoring per spec Section 6.3.
"""

from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class DataConfidenceResult:
    overall: float
    project: float
    compensation: float
    legal: float
    land_records: float
    rr: float


def compute_data_confidence(
    completeness: float,
    freshness_days: float,
    cross_source_agreement: float,
    identity_confidence: float,
    weights: dict | None = None,
) -> float:
    """
    DC_domain = w_c·completeness + w_f·freshness + w_a·agreement + w_i·identity_confidence
    Freshness decays with days since last successful sync.
    """
    w = weights or {"completeness": 0.3, "freshness": 0.25, "agreement": 0.25, "identity": 0.2}

    freshness_score = max(0, 1.0 - (freshness_days / 90.0))

    return (
        w["completeness"] * completeness
        + w["freshness"] * freshness_score
        + w["agreement"] * cross_source_agreement
        + w["identity"] * identity_confidence
    )


def compute_project_data_confidence(
    project_data: dict,
    last_syncs: dict | None = None,
) -> DataConfidenceResult:
    """Compute per-domain data confidence for a project."""
    now = datetime.now(timezone.utc)

    domains = {
        "project": {"completeness": 0.9, "agreement": 0.9, "identity": 0.95},
        "compensation": {"completeness": 0.7, "agreement": 0.8, "identity": 0.85},
        "legal": {"completeness": 0.5, "agreement": 0.7, "identity": 0.8},
        "land_records": {"completeness": 0.6, "agreement": 0.75, "identity": 0.9},
        "rr": {"completeness": 0.65, "agreement": 0.8, "identity": 0.85},
    }

    scores = {}
    for domain, defaults in domains.items():
        data = project_data.get(domain, {})
        completeness = data.get("completeness", defaults["completeness"])
        agreement = data.get("agreement", defaults["agreement"])
        identity = data.get("identity", defaults["identity"])

        last_sync = (last_syncs or {}).get(domain)
        if last_sync:
            freshness_days = (now - last_sync).total_seconds() / 86400
        else:
            freshness_days = 30  # Default: 30 days

        scores[domain] = round(compute_data_confidence(
            completeness, freshness_days, agreement, identity
        ), 3)

    overall = sum(scores.values()) / len(scores)

    return DataConfidenceResult(
        overall=round(overall, 3),
        project=scores["project"],
        compensation=scores["compensation"],
        legal=scores["legal"],
        land_records=scores["land_records"],
        rr=scores["rr"],
    )
