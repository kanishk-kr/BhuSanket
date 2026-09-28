"""
Scenario simulator — what-if analysis with allow-listed actions only.
Computes f(x ⊕ Δ) and labels output as model simulation (spec Section 10.1).
"""

from app.engine.prediction import HazardModel


# Allow-listed actions per spec Section 10.1 / FR-11
ALLOWED_ACTIONS = {
    "EXPEDITE_COMPENSATION": {
        "name": "Expedite Compensation Disbursal",
        "modifiable_features": ["compensation_delay_days"],
        "category": "financial",
        "typical_effect": {"compensation_delay_days": -30},
    },
    "REVENUE_CAMP": {
        "name": "Conduct Revenue Camp",
        "modifiable_features": ["pending_mutations", "ownership_complexity"],
        "category": "documentation",
        "typical_effect": {"pending_mutations": -5, "ownership_complexity": -1},
    },
    "LEGAL_REVIEW": {
        "name": "Initiate Legal Review",
        "modifiable_features": ["litigation_active"],
        "category": "legal",
        "typical_effect": {"litigation_active": False},
    },
    "SURVEY_TEAM": {
        "name": "Deploy Additional Survey Team",
        "modifiable_features": ["survey_pending_count"],
        "category": "technical",
        "typical_effect": {"survey_pending_count": -10},
    },
    "RR_MEETING": {
        "name": "R&R Consultation Meeting",
        "modifiable_features": ["grievance_count", "rr_completion_pct"],
        "category": "social",
        "typical_effect": {"grievance_count": -3, "rr_completion_pct": 0.1},
    },
    "ESCALATE_APPROVAL": {
        "name": "Escalate Approval Request",
        "modifiable_features": ["approval_pending_days"],
        "category": "administrative",
        "typical_effect": {"approval_pending_days": -15},
    },
    "VERIFICATION_CAMP": {
        "name": "Conduct Verification Camp",
        "modifiable_features": ["ownership_complexity", "pending_mutations"],
        "category": "documentation",
        "typical_effect": {"ownership_complexity": -2, "pending_mutations": -3},
    },
    "BATCH_COMPENSATION": {
        "name": "Batch Compensation Processing",
        "modifiable_features": ["compensation_delay_days", "pending_payments"],
        "category": "financial",
        "typical_effect": {"compensation_delay_days": -45, "pending_payments": -10},
    },
}


def validate_action(action_code: str) -> bool:
    """Check if an action is in the allow-list. Reject unauthorized actions (FR-21)."""
    return action_code in ALLOWED_ACTIONS


def simulate_scenario(
    baseline_features: dict,
    actions: list[dict],
) -> dict:
    """
    Evaluate f(x ⊕ Δ) for the given actions.
    Returns baseline and scenario risk with change metrics.
    """
    model = HazardModel()

    # Baseline prediction
    baseline_pred = model.predict(baseline_features)

    # Apply action deltas to features
    scenario_features = _apply_deltas(baseline_features, actions)

    # Scenario prediction
    scenario_pred = model.predict(scenario_features)

    risk_change = scenario_pred.delay_probability - baseline_pred.delay_probability

    return {
        "baseline_risk": round(baseline_pred.delay_probability, 4),
        "scenario_risk": round(scenario_pred.delay_probability, 4),
        "risk_change": round(risk_change, 4),
        "p50_date_baseline": baseline_pred.p50_date,
        "p50_date_scenario": scenario_pred.p50_date,
        "p90_date_baseline": baseline_pred.p90_date,
        "p90_date_scenario": scenario_pred.p90_date,
        "actions_applied": [a.get("action_code") for a in actions],
        "label": "This is a model simulation, not a guarantee.",
    }


def _apply_deltas(features: dict, actions: list[dict]) -> dict:
    """Apply action deltas to a copy of the feature dict."""
    modified = {
        **features,
        "risk_factors": {**features.get("risk_factors", {})},
    }

    for action in actions:
        code = action.get("action_code", "")
        if code not in ALLOWED_ACTIONS:
            continue

        delta = action.get("delta") or ALLOWED_ACTIONS[code].get("typical_effect", {})
        for key, value in delta.items():
            if key in modified.get("risk_factors", {}):
                current = modified["risk_factors"][key]
                if isinstance(value, bool):
                    modified["risk_factors"][key] = value
                elif isinstance(current, (int, float)):
                    modified["risk_factors"][key] = max(0, current + value)

    return modified
