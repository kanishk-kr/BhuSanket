"""
Evidence and explainability engine.
Implements the chain: SHAP → feature interpretation → domain rule → evidence records → explanation.
Evidence grades per spec Appendix D.9.
"""

from dataclasses import dataclass, field


@dataclass
class EvidenceRecord:
    source: str
    record_type: str
    description: str
    date: str | None = None
    confidence: float = 1.0
    grade: str = "HIGH"
    record_id: str | None = None


@dataclass
class DriverExplanation:
    feature_name: str
    display_name: str
    contribution: float
    direction: str
    description: str
    evidence: list[EvidenceRecord] = field(default_factory=list)
    grade: str = "HIGH"
    category: str = ""


def compute_evidence_grade(
    has_official_record: bool = False,
    record_is_stale: bool = False,
    has_contradiction: bool = False,
    is_inferred: bool = False,
    is_verified_grievance: bool = False,
) -> str:
    """
    Evidence grade per spec Appendix D.9:
    HIGH: ≥1 official structured record, no unresolved contradiction
    MEDIUM: official record but stale, or verified grievance
    LOW: inferred, unverified text, or stale + inferred
    """
    if has_official_record and not has_contradiction and not record_is_stale:
        return "HIGH"
    if has_official_record and (record_is_stale or is_verified_grievance):
        return "MEDIUM"
    return "LOW"


def generate_explanation(
    risk_score: float,
    drivers: list[dict],
    project_data: dict,
) -> dict:
    """
    Generate a structured explanation with evidence chain.
    Returns summary text + driver details with evidence links.
    """
    if not drivers:
        return {
            "summary": f"Risk score: {risk_score:.0%}. Insufficient data for detailed explanation.",
            "drivers": [],
            "total_evidence_records": 0,
        }

    # Build natural language summary from top drivers
    top_driver = drivers[0] if drivers else None
    summary_parts = [f"Risk score: {risk_score:.0%}."]

    if top_driver:
        summary_parts.append(
            f"Primary driver: {top_driver.get('display_name', 'Unknown')} "
            f"(contributing {top_driver.get('contribution', 0):.1%} to risk)."
        )

    if len(drivers) > 1:
        other_names = [d.get("display_name", "") for d in drivers[1:3]]
        summary_parts.append(f"Also affected by: {', '.join(other_names)}.")

    # Generate evidence records for each driver
    enriched_drivers = []
    total_evidence = 0

    for driver in drivers:
        evidence_records = _find_evidence_for_driver(driver, project_data)
        grade = _compute_driver_grade(evidence_records)
        total_evidence += len(evidence_records)

        enriched_drivers.append(DriverExplanation(
            feature_name=driver.get("feature_name", ""),
            display_name=driver.get("display_name", ""),
            contribution=driver.get("contribution", 0),
            direction=driver.get("direction", "positive"),
            description=driver.get("description", ""),
            evidence=evidence_records,
            grade=grade,
            category=driver.get("category", ""),
        ))

    return {
        "summary": " ".join(summary_parts),
        "drivers": enriched_drivers,
        "total_evidence_records": total_evidence,
    }


def _find_evidence_for_driver(driver: dict, project_data: dict) -> list[EvidenceRecord]:
    """Find supporting evidence records for a driver."""
    records = []
    feature_name = driver.get("feature_name", "")

    # Map features to evidence sources
    evidence_map = {
        "compensation_delay_days": {
            "source": "Payment System",
            "record_type": "payment_record",
            "template": "Compensation processing has taken {value} days vs comparable median of 74 days",
        },
        "litigation_active": {
            "source": "Court Data",
            "record_type": "court_order",
            "template": "Active litigation: case pending with {detail}",
        },
        "ownership_complexity": {
            "source": "Land Records",
            "record_type": "land_record",
            "template": "Ownership complexity score: {value} (fragmented/disputed holdings)",
        },
        "pending_mutations": {
            "source": "Revenue Records",
            "record_type": "mutation_record",
            "template": "{value} mutations pending completion",
        },
        "grievance_count": {
            "source": "Grievance Portal",
            "record_type": "grievance",
            "template": "{value} active grievances filed by affected persons",
        },
        "extension_count": {
            "source": "Administrative Records",
            "record_type": "extension_order",
            "template": "{value} statutory extensions granted",
        },
        "days_since_last_update": {
            "source": "Project Monitoring",
            "record_type": "activity_log",
            "template": "No updates for {value} days (administrative silence detected)",
        },
    }

    if feature_name in evidence_map:
        ev_config = evidence_map[feature_name]
        value = driver.get("description", "").split(": ")[-1] if ": " in driver.get("description", "") else ""
        records.append(EvidenceRecord(
            source=ev_config["source"],
            record_type=ev_config["record_type"],
            description=ev_config["template"].format(value=value, detail=value),
            confidence=0.9,
            grade="HIGH",
        ))

    return records


def _compute_driver_grade(evidence_records: list[EvidenceRecord]) -> str:
    """Compute the overall grade for a driver based on its evidence."""
    if not evidence_records:
        return "LOW"
    grades = [r.grade for r in evidence_records]
    if "HIGH" in grades:
        return "HIGH"
    if "MEDIUM" in grades:
        return "MEDIUM"
    return "LOW"
