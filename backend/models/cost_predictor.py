"""
XGBoost cost adjustment model.
Trained at startup on synthetic data derived from benchmark rates.
Predicts a cost multiplier relative to the benchmark for a given route+product combo.
"""
from __future__ import annotations
import numpy as np
from xgboost import XGBRegressor
from config import ML_SYNTHETIC_SAMPLES, ML_RANDOM_SEED

rng = np.random.default_rng(ML_RANDOM_SEED)

# Feature encoding
FREIGHT_MODE_MAP = {"ocean_fcl": 0, "ocean_lcl": 1, "air": 2}
LAST_MILE_MAP = {"b2b": 0, "b2c": 1}

_model: XGBRegressor | None = None


def _generate_training_data(n: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic training samples.
    Features: [lpi_origin, lpi_dest, freight_mode, weight_kg, cbm,
               volume_log, hs_chapter, last_mile]
    Target: cost_multiplier (1.0 = benchmark avg, 0.7 = 30% below, 1.5 = 50% above)
    """
    lpi_origin = rng.uniform(3.0, 4.2, n)    # China LPI range
    lpi_dest   = rng.uniform(3.5, 4.5, n)    # Denmark/EU LPI range
    freight_mode = rng.integers(0, 3, n)      # 0=FCL, 1=LCL, 2=Air
    weight_kg  = rng.uniform(0.1, 50.0, n)
    cbm        = rng.uniform(0.0001, 0.5, n)
    volume_log = rng.uniform(2.0, 5.0, n)    # log10(volume) range 100..100k
    hs_chapter = rng.integers(1, 97, n).astype(float)
    last_mile  = rng.integers(0, 2, n)

    X = np.column_stack([lpi_origin, lpi_dest, freight_mode, weight_kg, cbm, volume_log, hs_chapter, last_mile])

    # Cost multiplier: driven by LPI, freight mode (air is expensive), volume discount
    base = 1.0
    lpi_factor = 1.0 - 0.05 * (lpi_dest - 3.8)     # higher dest LPI → lower cost
    air_factor = np.where(freight_mode == 2, 1.25, 1.0)
    lcl_factor = np.where(freight_mode == 1, 1.05, 1.0)
    vol_factor = 1.0 - 0.04 * (volume_log - 3.0)    # higher volume → lower per-unit cost
    noise = rng.normal(0, 0.06, n)

    y = base * lpi_factor * air_factor * lcl_factor * vol_factor + noise
    y = np.clip(y, 0.50, 2.00)
    return X, y


def train_model() -> None:
    global _model
    X, y = _generate_training_data(ML_SYNTHETIC_SAMPLES)
    _model = XGBRegressor(
        n_estimators=120,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=ML_RANDOM_SEED,
        verbosity=0,
    )
    _model.fit(X, y)


def predict_cost_multiplier(
    lpi_origin: float,
    lpi_dest: float,
    freight_mode: str,
    weight_kg: float,
    cbm: float,
    annual_volume: int,
    hs_chapter: int,
    last_mile: str,
) -> float:
    """Returns a cost adjustment multiplier (e.g. 1.12 = 12% above benchmark)."""
    if _model is None:
        return 1.0
    fm = FREIGHT_MODE_MAP.get(freight_mode, 0)
    lm = LAST_MILE_MAP.get(last_mile, 0)
    vol_log = float(np.log10(max(annual_volume, 1)))
    X = np.array([[lpi_origin, lpi_dest, fm, weight_kg, cbm, vol_log, float(hs_chapter), float(lm)]])
    return float(_model.predict(X)[0])
