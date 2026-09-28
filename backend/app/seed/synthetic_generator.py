"""
Synthetic data generator (Digital Twin) — spec Section H.
Generates 1,000-3,000 synthetic land acquisition projects with planted causal structure
for pipeline testing and model validation.
"""

import uuid
import random
import json
from datetime import date, datetime, timedelta, timezone
from faker import Faker

fake = Faker("en_IN")

# Causal structure from spec Section H:
# Ownership complexity ↑ → documentation delay ↑ → compensation delay ↑
# → grievances ↑ → litigation probability ↑ → stay ↑ → possession delay ↑

STATES = [
    "Rajasthan", "Maharashtra", "Gujarat", "Madhya Pradesh",
    "Uttar Pradesh", "Karnataka", "Tamil Nadu", "Andhra Pradesh",
    "Telangana", "Odisha", "Jharkhand", "Bihar",
]

DISTRICTS = {
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Ajmer", "Kota"],
    "Maharashtra": ["Pune", "Nagpur", "Nashik", "Aurangabad", "Thane"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Agra", "Varanasi", "Prayagraj"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubli", "Mangaluru", "Belgaum"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli"],
    "Andhra Pradesh": ["Vijayawada", "Visakhapatnam", "Guntur", "Tirupati", "Nellore"],
    "Telangana": ["Hyderabad", "Warangal", "Karimnagar", "Nizamabad", "Khammam"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Hazaribagh"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga"],
}

SECTORS = ["highways", "railways", "irrigation", "industrial", "urban_development", "power"]

STAGE_SEQUENCE = [
    {"name": "SIA Commenced", "code": "SIA_COMMENCED", "base_duration": (30, 120)},
    {"name": "SIA Completed", "code": "SIA_COMPLETED", "base_duration": (60, 180)},
    {"name": "Expert Group Appraisal", "code": "EXPERT_GROUP_APPRAISAL_DONE", "base_duration": (30, 90)},
    {"name": "Preliminary Notification (Section 11)", "code": "PRELIM_NOTIFICATION_PUBLISHED", "base_duration": (15, 60)},
    {"name": "Objections Window", "code": "OBJECTION_WINDOW", "base_duration": (60, 60)},
    {"name": "R&R Scheme Approved", "code": "RR_SCHEME_APPROVED", "base_duration": (30, 120)},
    {"name": "Declaration (Section 19)", "code": "DECLARATION_PUBLISHED", "base_duration": (30, 180)},
    {"name": "Survey & Measurement", "code": "SURVEY_COMPLETED", "base_duration": (30, 90)},
    {"name": "Award (Section 25)", "code": "AWARD_MADE", "base_duration": (60, 365)},
    {"name": "Compensation Disbursed", "code": "COMPENSATION_DISBURSED", "base_duration": (30, 180)},
    {"name": "Possession Granted", "code": "POSSESSION_GRANTED", "base_duration": (15, 90)},
]


def generate_project(project_number: int) -> dict:
    """Generate a single synthetic project with causal structure."""
    state = random.choice(STATES)
    district = random.choice(DISTRICTS[state])
    sector = random.choice(SECTORS)

    project_id = str(uuid.uuid4())
    start_date = date.today() - timedelta(days=random.randint(180, 1200))

    # Project parameters
    total_km = random.uniform(10, 200)
    num_packages = max(1, int(total_km / random.uniform(15, 30)))
    total_parcels = random.randint(50, 500)
    budget_crores = total_km * random.uniform(5, 25)

    # Causal factors (planted — spec Section H)
    ownership_complexity = random.uniform(1, 8)
    admin_capacity = random.uniform(0.3, 1.0)
    funds_gap = random.uniform(0, 0.5)

    # Derived delays (causal chain)
    doc_delay_factor = 1.0 + (ownership_complexity / 8.0) * 1.5
    comp_delay_factor = doc_delay_factor * (1.0 + funds_gap)
    grievance_prob = min(0.9, 0.1 + ownership_complexity / 10 + funds_gap)
    litigation_prob = min(0.7, grievance_prob * 0.4)
    stay_prob = litigation_prob * 0.3

    has_litigation = random.random() < litigation_prob
    has_stay = has_litigation and random.random() < stay_prob
    has_grievances = random.random() < grievance_prob
    num_grievances = random.randint(1, 15) if has_grievances else 0
    extension_count = random.randint(0, 3) if random.random() < 0.3 else 0

    # Generate stages with planted delays
    stages = []
    current_date = start_date
    for i, stage_def in enumerate(STAGE_SEQUENCE):
        min_d, max_d = stage_def["base_duration"]
        base_duration = random.randint(min_d, max_d)

        # Apply causal delay factors
        if stage_def["code"] in ["SURVEY_COMPLETED", "AWARD_MADE"]:
            actual_duration = int(base_duration * doc_delay_factor)
        elif stage_def["code"] in ["COMPENSATION_DISBURSED"]:
            actual_duration = int(base_duration * comp_delay_factor)
        elif stage_def["code"] in ["POSSESSION_GRANTED"]:
            stay_addition = random.randint(60, 300) if has_stay else 0
            actual_duration = int(base_duration * (1 + funds_gap) + stay_addition)
        else:
            actual_duration = int(base_duration / admin_capacity)

        # Determine if stage is completed
        stage_end = current_date + timedelta(days=actual_duration)
        is_completed = stage_end <= date.today()
        is_current = not is_completed and current_date <= date.today()

        status = "completed" if is_completed else ("in_progress" if is_current else "not_started")

        stages.append({
            "id": str(uuid.uuid4()),
            "name": stage_def["name"],
            "code": stage_def["code"],
            "sequence_order": i,
            "planned_start": current_date.isoformat(),
            "actual_start": current_date.isoformat() if status != "not_started" else None,
            "actual_end": stage_end.isoformat() if is_completed else None,
            "original_commitment_date": (current_date + timedelta(days=base_duration)).isoformat(),
            "approved_baseline_date": (current_date + timedelta(days=base_duration)).isoformat(),
            "status": status,
            "base_duration_days": base_duration,
            "actual_duration_days": actual_duration if is_completed else None,
        })

        if is_completed:
            current_date = stage_end

    # Generate parcels
    parcels_acquired = int(total_parcels * random.uniform(0.5, 0.98))
    blocking_parcels = random.randint(2, min(20, total_parcels - parcels_acquired + 1))
    land_acquired_pct = round(parcels_acquired / total_parcels * 100, 1)

    # Construction-enabling (different from acquired %)
    critical_resolved = max(0, parcels_acquired - blocking_parcels)
    construction_enabling_pct = round(critical_resolved / total_parcels * 100, 1)

    # Risk score (derived from causal structure)
    base_risk = 0.3
    risk_from_delay = min(0.3, comp_delay_factor / 10)
    risk_from_litigation = 0.15 if has_litigation else 0
    risk_from_stay = 0.2 if has_stay else 0
    risk_from_blocking = min(0.15, blocking_parcels / total_parcels)
    risk = min(0.98, base_risk + risk_from_delay + risk_from_litigation + risk_from_stay + risk_from_blocking)

    # Risk momentum
    momentum = random.uniform(-10, 20)
    if risk > 0.7:
        momentum = random.uniform(5, 25)
    momentum_class = "stable" if abs(momentum) < 5 else ("rising" if momentum < 15 else "accelerating")

    project = {
        "id": project_id,
        "name": f"{sector.replace('_', ' ').title()} Project - {district} {fake.word().title()} Corridor",
        "code": f"LA-{state[:2].upper()}-{district[:3].upper()}-{project_number:04d}",
        "state": state,
        "district": district,
        "sector": sector,
        "jurisdiction": f"{state} - {district}",
        "requiring_body_id": f"RB-{sector[:3].upper()}-{random.randint(1, 50):03d}",
        "budget": round(budget_crores, 2),
        "status": "active" if risk < 0.9 else ("delayed" if random.random() > 0.3 else "active"),
        "total_parcels": total_parcels,
        "total_area_hectares": round(total_km * random.uniform(5, 20), 1),
        "land_acquired_pct": land_acquired_pct,
        "construction_enabling_pct": construction_enabling_pct,
        "current_risk_score": round(risk, 3),
        "risk_momentum": round(momentum, 2),
        "risk_momentum_class": momentum_class,
        "model_confidence": round(random.uniform(0.5, 0.95), 3),
        "data_confidence": round(random.uniform(0.3, 0.9), 3),
        "stages": stages,
        "num_packages": num_packages,
        "total_km": round(total_km, 1),
        # Causal factors (for model validation)
        "_causal": {
            "ownership_complexity": round(ownership_complexity, 2),
            "admin_capacity": round(admin_capacity, 2),
            "funds_gap": round(funds_gap, 2),
            "has_litigation": has_litigation,
            "has_stay": has_stay,
            "num_grievances": num_grievances,
            "extension_count": extension_count,
            "blocking_parcels": blocking_parcels,
        },
    }

    return project


def generate_synthetic_dataset(n_projects: int = 1500) -> list[dict]:
    """Generate full synthetic dataset per spec Section H."""
    projects = []
    for i in range(n_projects):
        projects.append(generate_project(i + 1))

    # Validate delay distribution resembles MoSPI aggregates
    # (spec Section H: 1-12, 13-24, 25-60, 60+ months)
    return projects


def generate_parcels_for_project(project: dict) -> list[dict]:
    """Generate synthetic parcels for a project."""
    parcels = []
    total = project["total_parcels"]
    blocking_count = project["_causal"]["blocking_parcels"]

    for i in range(total):
        is_blocking = i < blocking_count
        acquired = random.random() < (project["land_acquired_pct"] / 100)

        parcels.append({
            "id": str(uuid.uuid4()),
            "project_id": project["id"],
            "ulpin": f"{random.randint(10, 99)}{random.randint(100000000000, 999999999999)}" if random.random() > 0.3 else None,
            "survey_no": f"{random.randint(1, 999)}/{random.choice('ABCDEF')}",
            "village_name": fake.city(),
            "district": project["district"],
            "area_hectares": round(random.uniform(0.1, 10.0), 2),
            "land_use": random.choice(["agricultural", "barren", "residential", "forest", "commercial"]),
            "acquisition_status": "acquired" if acquired else random.choice(["in_progress", "not_started", "disputed"]),
            "possession_status": "granted" if (acquired and random.random() > 0.2) else "not_granted",
            "criticality_weight": 1.0 if is_blocking else round(random.uniform(0.2, 0.8), 2),
            "usability_score": round(random.uniform(0.0, 1.0), 2) if acquired else 0.0,
            "is_blocking": is_blocking and not acquired,
            "encumbrance_free": acquired and random.random() > 0.15,
            "access_available": acquired and random.random() > 0.1,
        })

    return parcels


def generate_alerts_for_project(project: dict) -> list[dict]:
    """Generate synthetic alerts for a project."""
    alerts = []
    risk = project["current_risk_score"]
    causal = project["_causal"]

    if risk > 0.7:
        alerts.append({
            "id": str(uuid.uuid4()),
            "project_id": project["id"],
            "alert_type": "risk_threshold_crossed",
            "title": f"High risk detected: {project['name']}",
            "description": f"Risk score {risk:.0%} exceeds threshold. {causal['blocking_parcels']} parcels blocking workfront.",
            "severity": "high" if risk > 0.8 else "medium",
            "priority_index": round(risk * 100 * random.uniform(0.8, 1.0), 1),
            "state": "open",
        })

    if causal["has_stay"]:
        alerts.append({
            "id": str(uuid.uuid4()),
            "project_id": project["id"],
            "alert_type": "court_stay_detected",
            "title": f"Court stay active on {project['code']}",
            "description": "Court stay affecting parcel acquisition. Statutory clocks paused.",
            "severity": "high",
            "priority_index": round(90 + random.uniform(0, 10), 1),
            "state": "open",
        })

    return alerts


if __name__ == "__main__":
    # Generate and save dataset
    dataset = generate_synthetic_dataset(1500)
    print(f"Generated {len(dataset)} synthetic projects")

    # Stats
    risks = [p["current_risk_score"] for p in dataset]
    delayed = sum(1 for p in dataset if p["status"] == "delayed")
    with_litigation = sum(1 for p in dataset if p["_causal"]["has_litigation"])
    with_stays = sum(1 for p in dataset if p["_causal"]["has_stay"])

    print(f"Average risk: {sum(risks)/len(risks):.2f}")
    print(f"Delayed: {delayed}/{len(dataset)}")
    print(f"With litigation: {with_litigation}")
    print(f"With stays: {with_stays}")

    with open("synthetic_data.json", "w") as f:
        json.dump(dataset, f, indent=2, default=str)
