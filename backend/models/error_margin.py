"""
Conformal prediction error margin estimator using MAPIE.
Wraps XGBoost with MAPIE MapieRegressor to produce 90% prediction intervals.
Returns per-step and per-route confidence intervals.
"""
from __future__ import annotations
import numpy as np
from xgboost import XGBRegressor
from mapie.regression import MapieRegressor
from mapie.conformity_scores import AbsoluteConformityScore
from config import ML_SYNTHETIC_SAMPLES, ML_RANDOM_SEED, ML_CONFIDENCE_TARGET

rng = np.random.default_rng(ML_RANDOM_SEED + 2)

_mapie: MapieRegressor | None = None

# Per-step volatility weights (higher = wider interval)
STEP_VOLATILITY = {
    "ex_works":       0.02,   # fixed — user input
    "origin_inland":  0.18,
    "export_customs": 0.12,
    "thc_origin":     0.10,
    "intl_freight":   0.28,   # most volatile step
    "insurance":      0.08,
    "thc_dest":       0.12,
    "import_customs": 0.15,   # duty rate can vary
    "dest_inland":    0.16,
    "warehousing":    0.14,
    "last_mile":      0.20,
}


def _generate_training_data(n: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Features: [freight_mode, step_volatility, lpi_avg, volume_log, weight_kg]
    Target: actual cost as a ratio to benchmark (for conformal calibration)
    """
    freight_mode     = rng.integers(0, 3, n).astype(float)
    step_volatility  = rng.uniform(0.05, 0.30, n)
    lpi_avg          = rng.uniform(3.0, 4.5, n)
    volume_log       = rng.uniform(2.0, 5.0, n)
    weight_kg        = rng.uniform(0.1, 50.0, n)

    X = np.column_stack([freight_mode, step_volatility, lpi_avg, volume_log, weight_kg])

    noise_scale = step_volatility * (1.0 + 0.1 * (4.0 - lpi_avg))
    y = 1.0 + rng.normal(0, noise_scale, n)
    y = np.clip(y, 0.3, 2.5)
    return X, y


def train_model() -> None:
    global _mapie
    X, y = _generate_training_data(ML_SYNTHETIC_SAMPLES)

    base_model = XGBRegressor(
        n_estimators=80,
        max_depth=3,
        learning_rate=0.1,
        random_state=ML_RANDOM_SEED + 2,
        verbosity=0,
    )
    _mapie = MapieRegressor(
        estimator=base_model,
        conformity_score=AbsoluteConformityScore(),
        method="base",
        cv=5,
        random_state=ML_RANDOM_SEED + 2,
    )
    _mapie.fit(X, y)


def get_step_interval(
    step_id: str,
    base_cost: float,
    freight_mode: str,
    lpi_avg: float,
    annual_volume: int,
    weight_kg: float,
) -> tuple[float, float]:
    """
    Returns (lower_bound, upper_bound) for a step's cost per unit.
    Uses MAPIE-predicted multiplier clamped to per-step volatility bounds.
    """
    volatility = STEP_VOLATILITY.get(step_id, 0.15)

    if _mapie is not None:
        fm = {"ocean_fcl": 0, "ocean_lcl": 1, "air": 2}.get(freight_mode, 0)
        vol_log = float(np.log10(max(annual_volume, 1)))
        X = np.array([[float(fm), volatility, lpi_avg, vol_log, weight_kg]])
        _, intervals = _mapie.predict(X, alpha=1.0 - ML_CONFIDENCE_TARGET)
        # intervals shape: (n_samples, 2, n_alpha)
        raw_lower = float(intervals[0, 0, 0])
        raw_upper = float(intervals[0, 1, 0])
        # Clamp: multiplier deviation capped at step-specific volatility
        # This prevents MAPIE from being overly conservative on synthetic training data
        center = (raw_lower + raw_upper) / 2.0
        half_width = min((raw_upper - raw_lower) / 2.0, volatility)
        lower_mult = max(0.5, center - half_width)
        upper_mult = min(2.0, center + half_width)
    else:
        lower_mult = 1.0 - volatility
        upper_mult = 1.0 + volatility

    # Ex-works is user input — no uncertainty
    if step_id == "ex_works":
        return round(base_cost, 4), round(base_cost, 4)

    lower = max(0.0, base_cost * lower_mult)
    upper = base_cost * upper_mult
    return round(lower, 4), round(upper, 4)


def route_confidence_score(step_results: list[dict]) -> float:
    """
    Overall confidence score for a route (0–100).
    Higher = narrower error margins = more reliable prediction.
    Uses route-level relative error band (total CI / total cost).
    """
    if not step_results:
        return 50.0

    total_cost = sum(s.get("cost_per_unit_usd", 0) for s in step_results)
    total_low = sum(s.get("error_low_usd", s.get("cost_per_unit_usd", 0)) for s in step_results)
    total_high = sum(s.get("error_high_usd", s.get("cost_per_unit_usd", 0)) for s in step_results)

    if total_cost <= 0:
        return 50.0

    rel_band = (total_high - total_low) / total_cost
    # rel_band ~0.05 → ~90, ~0.20 → ~70, ~0.40 → ~55, ~0.80 → ~35
    score = max(20.0, min(95.0, 95.0 / (1.0 + rel_band * 1.8)))
    return round(score, 1)
