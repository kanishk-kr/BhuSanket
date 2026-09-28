"""
Statutory Deadline Engine — the core legal intelligence component.
Computes clock arithmetic, deadline risk, and alert states per spec Appendix A.3.
"""

from datetime import date, timedelta
from dataclasses import dataclass

from app.config import get_settings

settings = get_settings()


@dataclass
class ClockResult:
    """Result of statutory clock computation."""
    clock_id: str
    start_date: date
    duration_days: int
    pause_days: int
    deadline: date
    days_remaining: int
    deadline_risk: float
    alert_state: str  # GREEN, AMBER, RED, CRITICAL, CANNOT_EVALUATE
    consequence: str
    section_reference: str
    description: str


def compute_deadline(
    start_date: date,
    duration_days: int,
    pause_intervals: list[tuple[date, date]] | None = None,
) -> date:
    """
    Compute the adjusted deadline accounting for pause periods.
    deadline = start + duration + Σ|pause_intervals|
    """
    total_paused = 0
    if pause_intervals:
        for pause_start, pause_end in pause_intervals:
            if pause_end and pause_start:
                total_paused += max(0, (pause_end - pause_start).days)
            elif pause_start:
                # Open-ended pause (stay still active)
                total_paused += max(0, (date.today() - pause_start).days)

    return start_date + timedelta(days=duration_days + total_paused)


def compute_days_remaining(deadline: date, as_of: date | None = None) -> int:
    """Days remaining until deadline."""
    ref_date = as_of or date.today()
    return (deadline - ref_date).days


def compute_deadline_risk(
    days_remaining: int,
    estimated_completion_probability: float | None = None,
    stage_survival_curve: list[float] | None = None,
) -> float:
    """
    DeadlineRisk = P(stage completion time > deadline | x)
    If we have a survival curve, use it. Otherwise, heuristic from days remaining.
    """
    if stage_survival_curve is not None and len(stage_survival_curve) > 0:
        # The survival curve gives P(not completed by bucket k)
        # DeadlineRisk = S(deadline_bucket)
        bucket_width = settings.hazard_bucket_width_days
        deadline_bucket = max(0, days_remaining) // bucket_width
        if deadline_bucket < len(stage_survival_curve):
            return stage_survival_curve[deadline_bucket]
        return stage_survival_curve[-1]

    if estimated_completion_probability is not None:
        return 1.0 - estimated_completion_probability

    # Heuristic fallback based on days remaining
    if days_remaining <= 0:
        return 0.95
    elif days_remaining <= 30:
        return 0.8
    elif days_remaining <= 90:
        return 0.5
    elif days_remaining <= 180:
        return 0.3
    else:
        return 0.1


def compute_alert_state(deadline_risk: float, days_remaining: int) -> str:
    """
    Alert states per spec Appendix A.3:
    GREEN: DeadlineRisk < 0.2
    AMBER: 0.2 - 0.5
    RED: 0.5 - 0.8
    CRITICAL: > 0.8 or days_remaining below minimum
    """
    if days_remaining <= 0:
        return "CRITICAL"
    if deadline_risk >= settings.deadline_risk_red:
        return "CRITICAL"
    if deadline_risk >= settings.deadline_risk_amber:
        return "RED"
    if deadline_risk >= settings.deadline_risk_green:
        return "AMBER"
    return "GREEN"


def evaluate_clock(
    start_date: date,
    duration_days: int,
    pause_intervals: list[tuple[date, date]] | None = None,
    section_reference: str = "",
    description: str = "",
    consequence: str = "REVIEW",
    clock_id: str = "",
    survival_curve: list[float] | None = None,
    completion_prob: float | None = None,
) -> ClockResult:
    """
    Full statutory clock evaluation.
    Returns the computed deadline, days remaining, risk, and alert state.
    """
    deadline = compute_deadline(start_date, duration_days, pause_intervals)
    days_remaining = compute_days_remaining(deadline)
    deadline_risk = compute_deadline_risk(days_remaining, completion_prob, survival_curve)
    alert_state = compute_alert_state(deadline_risk, days_remaining)

    total_paused = 0
    if pause_intervals:
        for ps, pe in pause_intervals:
            if pe and ps:
                total_paused += max(0, (pe - ps).days)
            elif ps:
                total_paused += max(0, (date.today() - ps).days)

    return ClockResult(
        clock_id=clock_id,
        start_date=start_date,
        duration_days=duration_days,
        pause_days=total_paused,
        deadline=deadline,
        days_remaining=days_remaining,
        deadline_risk=deadline_risk,
        alert_state=alert_state,
        consequence=consequence,
        section_reference=section_reference,
        description=description,
    )


# ─── RFCTLARR 2013 Clock Configurations (spec Appendix A.2) ─────────────
RFCTLARR_2013_CLOCKS = [
    {
        "clock_code": "SIA_COMPLETION",
        "section_reference": "4(2)",
        "trigger_event": "SIA_COMMENCED",
        "end_event": "SIA_COMPLETED",
        "duration_days": 180,
        "description": "SIA completion within 6 months of commencement",
        "expiry_consequence": "REVIEW",
        "pause_rules": None,
    },
    {
        "clock_code": "SIA_VALIDITY",
        "section_reference": "14",
        "trigger_event": "EXPERT_GROUP_APPRAISAL_DONE",
        "end_event": "PRELIM_NOTIFICATION_PUBLISHED",
        "duration_days": 365,
        "description": "Preliminary notification within 12 months of SIA appraisal",
        "expiry_consequence": "LAPSE",
        "consequence_description": "SIA report deemed lapsed; fresh SIA required",
        "pause_rules": None,
    },
    {
        "clock_code": "DECLARATION",
        "section_reference": "19(7)",
        "trigger_event": "PRELIM_NOTIFICATION_PUBLISHED",
        "end_event": "DECLARATION_PUBLISHED",
        "duration_days": 365,
        "description": "Declaration within 12 months of preliminary notification",
        "expiry_consequence": "RESCISSION",
        "consequence_description": "Preliminary notification deemed rescinded",
        "pause_rules": {"exclude_court_stay_periods": True},
    },
    {
        "clock_code": "AWARD",
        "section_reference": "25",
        "trigger_event": "DECLARATION_PUBLISHED",
        "end_event": "AWARD_MADE",
        "duration_days": 365,
        "description": "Collector's award within 12 months of declaration",
        "expiry_consequence": "LAPSE",
        "consequence_description": "Entire acquisition proceedings lapse",
        "pause_rules": None,
    },
    {
        "clock_code": "COMPENSATION_PAYMENT",
        "section_reference": "38(1)",
        "trigger_event": "AWARD_MADE",
        "end_event": "COMPENSATION_DISBURSED",
        "duration_days": 90,
        "description": "Compensation within 3 months of award",
        "expiry_consequence": "REVIEW",
        "consequence_description": "Possession preconditions unmet",
        "pause_rules": None,
    },
    {
        "clock_code": "MONETARY_RR",
        "section_reference": "38(1)",
        "trigger_event": "AWARD_MADE",
        "end_event": "RR_MILESTONE_COMPLETED",
        "duration_days": 180,
        "description": "Monetary R&R within 6 months of award",
        "expiry_consequence": "REVIEW",
        "pause_rules": None,
    },
    {
        "clock_code": "INFRA_RR",
        "section_reference": "38(1)",
        "trigger_event": "AWARD_MADE",
        "end_event": "RR_MILESTONE_COMPLETED",
        "duration_days": 540,
        "description": "Infrastructural R&R entitlements within 18 months",
        "expiry_consequence": "REVIEW",
        "pause_rules": None,
    },
]
