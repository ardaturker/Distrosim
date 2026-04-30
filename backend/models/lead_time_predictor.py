"""
XGBoost lead time adjustment model.
Predicts a lead time multiplier relative to benchmark transit days.
"""
from __future__ import annotations
import numpy as np
from xgboost import XGBRegressor
from config import ML_SYNTHETIC_SAMPLES, ML_RANDOM_SEED

rng = np.random.default_rng(ML_RANDOM_SEED + 1)

FREIGHT_MODE_MAP = {"ocean_fcl": 0, "ocean_lcl": 1, "air": 2}

_model: XGBRegressor | None = None


def _generate_training_data(n: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Features: [lpi_origin, lpi_dest_customs, freight_mode, season, port_congestion]
    Target: lead_time_multiplier (1.0 = benchmark avg)
    """
    lpi_origin   = rng.uniform(3.0, 4.2, n)
    lpi_customs  = rng.uniform(2.8, 4.5, n)   # customs sub-score for destination
    freight_mode = rng.integers(0, 3, n)
    season       = rng.integers(1, 5, n).astype(float)   # 1=Q1..4=Q4 (Q4 busier)
    congestion   = rng.uniform(1.0, 2.5, n)   # port congestion index

    X = np.column_stack([lpi_origin, lpi_customs, freight_mode, season, congestion])

    # Air is fastest; FCL faster than LCL (consolidation time)
    air_factor   = np.where(freight_mode == 2, 0.65, 1.0)
    lcl_factor   = np.where(freight_mode == 1, 1.15, 1.0)
    customs_factor = 1.0 + 0.04 * (4.0 - lpi_customs)
    season_factor  = np.where(season == 4, 1.08, 1.0)   # Q4 slowdown
    congestion_f   = 0.90 + 0.06 * congestion
    noise = rng.normal(0, 0.05, n)

    y = 1.0 * air_factor * lcl_factor * customs_factor * season_factor * congestion_f + noise
    y = np.clip(y, 0.50, 2.00)
    return X, y


def train_model() -> None:
    global _model
    X, y = _generate_training_data(ML_SYNTHETIC_SAMPLES)
    _model = XGBRegressor(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.08,
        random_state=ML_RANDOM_SEED + 1,
        verbosity=0,
    )
    _model.fit(X, y)


def predict_lead_time_multiplier(
    lpi_origin: float,
    lpi_dest_customs: float,
    freight_mode: str,
    season: int = 2,        # 1-4, current quarter
    port_congestion: float = 1.5,
) -> float:
    if _model is None:
        return 1.0
    fm = FREIGHT_MODE_MAP.get(freight_mode, 0)
    X = np.array([[lpi_origin, lpi_dest_customs, fm, float(season), port_congestion]])
    return float(_model.predict(X)[0])
