"""
DistroSim backend configuration.
All API keys are optional - system falls back to benchmark data gracefully.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR.parent / "data"
DB_PATH = BASE_DIR / "cache.db"

# Free APIs (no key required)
WORLD_BANK_API_BASE = "https://api.worldbank.org/v2"
WTO_API_BASE = "https://api.wto.org/timeseries/v1"
ECB_API_BASE = "https://data-api.ecb.europa.eu/service/data"

# Paid APIs (optional - will use benchmark fallback if not set)
FREIGHTOS_API_KEY = os.getenv("FREIGHTOS_API_KEY", "")
EASYSHIP_API_KEY = os.getenv("EASYSHIP_API_KEY", "")
DUTIFY_API_KEY = os.getenv("DUTIFY_API_KEY", "")
DESCARTES_API_KEY = os.getenv("DESCARTES_API_KEY", "")
WTO_API_KEY = os.getenv("WTO_API_KEY", "")  # WTO has optional auth for higher rate limits

# CORS — comma-separated list of allowed origins
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if o.strip()
]

# Cache TTLs (seconds)
CACHE_TTL = {
    "freight_rates": 4 * 3600,       # 4 hours
    "customs_duties": 24 * 3600,     # 24 hours
    "lpi_scores": 7 * 24 * 3600,     # 7 days
    "exchange_rates": 3600,           # 1 hour
    "benchmark": 30 * 24 * 3600,     # 30 days (static)
}

# ML model configuration
ML_CONFIDENCE_TARGET = 0.90          # 90% prediction interval
ML_SYNTHETIC_SAMPLES = 600           # Training samples generated per model
ML_RANDOM_SEED = 42

# Demo defaults
DEMO_PRODUCT = {
    "product_name": "Electronic Thermostat",
    "hs_code": "9032.10",
    "origin_country": "CN",
    "destination_country": "DK",
    "production_cost_usd": 8.00,
    "product_value_usd": 35.00,
    "weight_kg": 0.5,
    "length_cm": 15.0,
    "width_cm": 10.0,
    "height_cm": 3.0,
    "annual_volume": 5000,
    "freight_mode_preference": "all"
}

# Simulation limits
MAX_ROUTES = 8          # Max routes to return
MAX_ROUTE_PERMUTATIONS = 100    # Internal permutation limit before pruning
HTTP_TIMEOUT = 8.0      # Seconds before API call times out
