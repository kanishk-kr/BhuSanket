"""
Prediction engine — discrete-time hazard model + Monte Carlo simulation.
Implements spec Sections 7.1–7.6.
"""

import numpy as np
from datetime import date, timedelta
from dataclasses import dataclass, field

from app.config import get_settings

settings = get_settings()


@dataclass
class PredictionResult:
    """Output of the prediction engine for a single stage."""
    entity_id: str
    delay_probability: float
    survival_curve: list[float] = field(default_factory=list)
    prob_7d: float = 0.0
    prob_30d: float = 0.0
    prob_60d: float = 0.0
    prob_90d: float = 0.0
    p50_date: date | None = None
    p80_date: date | None = None
    p90_date: date | None = None
    target_a_prob: float = 0.0
    target_c_prob: float = 0.0
    confidence: float = 0.5
    drivers: list[dict] = field(default_factory=list)


@dataclass
class MonteCarloResult:
    """Output of Monte Carlo path simulation."""
    project_id: str
    completion_date_p50: date | None = None
    completion_date_p80: date | None = None
    completion_date_p90: date | None = None
    critical_milestone_probs: dict = field(default_factory=dict)
    statutory_clock_probs: dict = field(default_factory=dict)
    exposure_p50: float = 0.0
    exposure_p80: float = 0.0
    exposure_p90: float = 0.0
    paths: list[dict] = field(default_factory=list)


class HazardModel:
    """
    Discrete-time hazard model.
    h_k(x) = P(completes in bucket k | not yet completed, x)
    S(k) = Π_{j<k}(1 - h_j)

    For MVP, uses a synthetic model. In production, trained LightGBM.
    """

    def __init__(self, bucket_width_days: int | None = None):
        self.bucket_width = bucket_width_days or settings.hazard_bucket_width_days
        self.model = None
        self.is_trained = False

    def predict_hazard_rates(self, features: dict, n_buckets: int = 52) -> list[float]:
        """
        Predict hazard rate for each time bucket.
        Returns h_k for k = 0..n_buckets-1.
        """
        if self.is_trained and self.model is not None:
            # Production: use trained LightGBM
            pass

        # MVP: Synthetic hazard model based on features
        base_hazard = 0.03  # ~3% chance of completing in any given week

        # Adjust based on feature signals
        risk_factors = features.get("risk_factors", {})
        compensation_delay = risk_factors.get("compensation_delay_days", 0)
        litigation_active = risk_factors.get("litigation_active", False)
        ownership_complexity = risk_factors.get("ownership_complexity", 1.0)
        days_elapsed = features.get("days_elapsed", 0)

        # Lower hazard (slower completion) when risk factors are high
        modifier = 1.0
        if compensation_delay > 90:
            modifier *= 0.5
        elif compensation_delay > 30:
            modifier *= 0.7
        if litigation_active:
            modifier *= 0.4
        if ownership_complexity > 3:
            modifier *= 0.6

        # Increasing hazard over time (projects eventually complete or lapse)
        hazards = []
        for k in range(n_buckets):
            time_factor = 1.0 + (k * 0.02)  # Slight increase over time
            h_k = min(0.95, base_hazard * modifier * time_factor)
            hazards.append(h_k)

        return hazards

    def compute_survival_curve(self, hazards: list[float]) -> list[float]:
        """S(k) = Π_{j<k}(1 - h_j)"""
        survival = [1.0]
        for h in hazards:
            survival.append(survival[-1] * (1 - h))
        return survival

    def predict(self, features: dict, baseline_date: date | None = None) -> PredictionResult:
        """Full prediction for a stage."""
        hazards = self.predict_hazard_rates(features)
        survival = self.compute_survival_curve(hazards)

        # P(complete within m buckets) = 1 - S(m+1)
        def p_complete_within(days: int) -> float:
            buckets = days // self.bucket_width
            if buckets + 1 < len(survival):
                return 1.0 - survival[buckets + 1]
            return 1.0 - survival[-1]

        prob_7d = p_complete_within(7)
        prob_30d = p_complete_within(30)
        prob_60d = p_complete_within(60)
        prob_90d = p_complete_within(90)

        # Quantile dates (P50, P80, P90)
        ref_date = baseline_date or date.today()

        def quantile_date(quantile: float) -> date | None:
            for k, s in enumerate(survival):
                if (1 - s) >= quantile:
                    return ref_date + timedelta(days=k * self.bucket_width)
            return ref_date + timedelta(days=len(survival) * self.bucket_width)

        p50_date = quantile_date(0.5)
        p80_date = quantile_date(0.8)
        p90_date = quantile_date(0.9)

        # Delay probability (Target A) — P(completion > baseline + tolerance)
        tolerance_days = features.get("tolerance_days", 14)
        baseline = features.get("original_baseline_date")
        if baseline and ref_date:
            days_to_baseline = (baseline - ref_date).days + tolerance_days
            target_a = 1.0 - p_complete_within(max(0, days_to_baseline))
        else:
            target_a = 1.0 - prob_90d

        # Generate SHAP-like drivers (synthetic for MVP)
        drivers = self._generate_drivers(features)

        return PredictionResult(
            entity_id=features.get("entity_id", ""),
            delay_probability=target_a,
            survival_curve=survival,
            prob_7d=round(prob_7d, 4),
            prob_30d=round(prob_30d, 4),
            prob_60d=round(prob_60d, 4),
            prob_90d=round(prob_90d, 4),
            p50_date=p50_date,
            p80_date=p80_date,
            p90_date=p90_date,
            target_a_prob=round(target_a, 4),
            confidence=features.get("model_confidence", 0.7),
            drivers=drivers,
        )

    def _generate_drivers(self, features: dict) -> list[dict]:
        """Generate evidence-backed driver explanations (synthetic SHAP for MVP)."""
        drivers = []
        risk_factors = features.get("risk_factors", {})

        factor_map = {
            "compensation_delay_days": ("Compensation Processing Delay", "financial"),
            "litigation_active": ("Active Litigation", "legal"),
            "ownership_complexity": ("Ownership Complexity", "documentation"),
            "pending_mutations": ("Pending Land Mutations", "documentation"),
            "grievance_count": ("Active Grievances", "social"),
            "extension_count": ("Extensions Granted", "statutory"),
            "vacancy_flag": ("Officer Vacancy", "administrative"),
            "days_since_last_update": ("Administrative Silence", "process"),
        }

        for key, (display_name, category) in factor_map.items():
            value = risk_factors.get(key)
            if value is not None and value:
                contribution = np.random.uniform(0.05, 0.25) if isinstance(value, bool) else min(0.3, value / 300)
                drivers.append({
                    "feature_name": key,
                    "display_name": display_name,
                    "contribution": round(float(contribution), 4),
                    "direction": "positive",
                    "category": category,
                    "description": f"{display_name}: {value}",
                })

        drivers.sort(key=lambda d: d["contribution"], reverse=True)
        return drivers[:6]


class MonteCarloSimulator:
    """
    Monte Carlo path simulation along the dependency graph.
    Samples stage durations to produce project-level completion estimates.
    """

    def __init__(self, n_simulations: int = 1000):
        self.n_simulations = n_simulations
        self.hazard_model = HazardModel()

    def simulate_project(
        self,
        stages: list[dict],
        dependencies: list[dict],
        cost_curves: dict | None = None,
    ) -> MonteCarloResult:
        """Run Monte Carlo simulation for a project."""
        completion_days = []

        for _ in range(self.n_simulations):
            # Sample completion time for each stage
            stage_completions = {}
            for stage in stages:
                features = stage.get("features", {})
                hazards = self.hazard_model.predict_hazard_rates(features)
                survival = self.hazard_model.compute_survival_curve(hazards)

                # Sample from the survival distribution
                u = np.random.random()
                sampled_bucket = 0
                for k, s in enumerate(survival):
                    if (1 - s) >= u:
                        sampled_bucket = k
                        break
                else:
                    sampled_bucket = len(survival) - 1

                # Account for dependencies
                dep_delay = 0
                for dep in dependencies:
                    if dep.get("to_node_id") == stage.get("id"):
                        from_id = dep.get("from_node_id")
                        if from_id in stage_completions:
                            dep_delay = max(dep_delay, stage_completions[from_id])

                total_days = dep_delay + sampled_bucket * settings.hazard_bucket_width_days
                stage_completions[stage.get("id")] = total_days

            if stage_completions:
                completion_days.append(max(stage_completions.values()))

        if not completion_days:
            return MonteCarloResult(project_id="")

        completion_days = np.array(completion_days)
        ref_date = date.today()

        # Financial exposure (spec Appendix D.7)
        exposures = []
        if cost_curves:
            for d in completion_days:
                cost = 0.0
                for curve_name, curve_fn in cost_curves.items():
                    cost += curve_fn(d)
                exposures.append(cost)
            exposures = np.array(exposures)
        else:
            exposures = completion_days * 50000  # Default: ₹50K/day placeholder

        return MonteCarloResult(
            project_id="",
            completion_date_p50=ref_date + timedelta(days=int(np.percentile(completion_days, 50))),
            completion_date_p80=ref_date + timedelta(days=int(np.percentile(completion_days, 80))),
            completion_date_p90=ref_date + timedelta(days=int(np.percentile(completion_days, 90))),
            exposure_p50=float(np.percentile(exposures, 50)),
            exposure_p80=float(np.percentile(exposures, 80)),
            exposure_p90=float(np.percentile(exposures, 90)),
        )


class RiskMomentumTracker:
    """
    Risk velocity and trajectory per spec Section 7.5.
    v = 7 × (r_t − r_{t−k}) / k points per week
    """

    @staticmethod
    def compute_velocity(
        risk_history: list[tuple[date, float]],
        window_days: int | None = None,
    ) -> tuple[float, str]:
        """Compute risk velocity and classify as stable/rising/accelerating."""
        window = window_days or settings.risk_velocity_window_days

        if len(risk_history) < 2:
            return 0.0, "stable"

        risk_history.sort(key=lambda x: x[0])
        recent = risk_history[-1]
        # Find the entry ~window days ago
        target_date = recent[0] - timedelta(days=window)
        past = min(risk_history, key=lambda x: abs((x[0] - target_date).days))

        days_diff = max(1, (recent[0] - past[0]).days)
        velocity = 7.0 * (recent[1] - past[1]) / days_diff

        if abs(velocity) < settings.risk_stable_threshold:
            momentum_class = "stable"
        elif velocity < settings.risk_rising_threshold:
            momentum_class = "rising"
        else:
            momentum_class = "accelerating"

        return round(velocity, 2), momentum_class

    @staticmethod
    def compute_trajectory(
        risk_history: list[tuple[date, float]],
        n_points: int = 3,
    ) -> list[float]:
        """Short forecast of risk trajectory."""
        if len(risk_history) < 2:
            return [risk_history[-1][1]] if risk_history else [0.5]

        risk_history.sort(key=lambda x: x[0])
        recent_values = [r[1] for r in risk_history[-min(5, len(risk_history)):]]

        # Simple linear extrapolation
        if len(recent_values) >= 2:
            slope = (recent_values[-1] - recent_values[0]) / len(recent_values)
            trajectory = []
            for i in range(1, n_points + 1):
                predicted = min(1.0, max(0.0, recent_values[-1] + slope * i))
                trajectory.append(round(predicted, 3))
            return trajectory

        return [recent_values[-1]] * n_points
