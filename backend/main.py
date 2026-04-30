"""
DistroSim FastAPI backend.
Endpoints:
  POST /simulate       — run full simulation
  GET  /hs-codes/search — autocomplete HS code lookup
  GET  /demo           — return demo request body
  GET  /health         — health check
  GET  /cache/stats    — cache statistics
"""
from __future__ import annotations
import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from db.cache import init_db, cache_stats, cache_prune
import aiosqlite
from config import DB_PATH
from services.simulation import run_simulation
from api.news import fetch_rotterdam_news, get_region_list
from api.news_intelligence import extract_risk_signals, route_risk_summary as build_risk_summary
from models.cost_predictor import train_model as train_cost
from models.lead_time_predictor import train_model as train_lead
from models.error_margin import train_model as train_error
from config import DEMO_PRODUCT

DATA_DIR = Path(__file__).parent.parent / "data"

_hs_codes: list[dict] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    _hs_codes.extend(json.loads((DATA_DIR / "hs_codes.json").read_text()))
    train_cost()
    train_lead()
    train_error()
    yield
    # Shutdown (nothing needed)


app = FastAPI(
    title="DistroSim API",
    description="Supply chain distribution cost simulator — China → Denmark",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ─────────────────────────────────────────────────

class SimulationRequest(BaseModel):
    product_name: str = Field(default="Electronic Thermostat")
    hs_code: str = Field(default="9032.10", description="6-digit HS code (dots optional)")
    production_cost_usd: float = Field(default=8.0, gt=0)
    product_value_usd: float = Field(default=35.0, gt=0)
    weight_kg: float = Field(default=0.5, gt=0)
    length_cm: float = Field(default=15.0, gt=0)
    width_cm: float = Field(default=10.0, gt=0)
    height_cm: float = Field(default=3.0, gt=0)
    annual_volume: int = Field(default=5000, ge=1)
    freight_mode_preference: str = Field(default="all", pattern="^(all|ocean|air)$")
    last_mile_preference: str = Field(default="both", pattern="^(both|b2b|b2c)$")
    weight_cost: float = Field(default=0.40, ge=0, le=1)
    weight_time: float = Field(default=0.30, ge=0, le=1)
    weight_reliability: float = Field(default=0.30, ge=0, le=1)
    tariff_surcharge_pct: float = Field(default=0.0, ge=0, le=300, description="Additional duty % on top of MFN rate (tariff scenario)")
    destination_id: str = Field(default="dk_aarhus", description="Destination ID from /destinations")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/destinations")
async def get_destinations():
    """List all supported destination countries/ports."""
    from services.simulation import _DESTINATIONS
    return list(_DESTINATIONS.values())


@app.get("/health")
async def health():
    return {"status": "ok", "service": "DistroSim API", "lane": "China → Denmark"}


@app.get("/demo")
async def demo():
    """Return the default demo request body."""
    return DEMO_PRODUCT


@app.post("/simulate")
async def simulate(req: SimulationRequest):
    try:
        result = await run_simulation(req.model_dump())
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/hs-codes/search")
async def search_hs_codes(q: str = ""):
    """Fuzzy search HS codes by code or description. Returns code, description, weight_kg."""
    if not q or len(q) < 2:
        results = _hs_codes[:10]
    else:
        q_lower = q.lower()
        results = [
            h for h in _hs_codes
            if q_lower in h["code"] or q_lower in h["description"].lower()
        ][:20]
    return [
        {"code": h["code"], "description": h["description"], "weight_kg": h.get("typical_weight_kg")}
        for h in results
    ]


@app.get("/news/regions")
async def get_news_regions():
    """List all available news regions."""
    return get_region_list()


@app.get("/news")
async def get_news(limit: int = 30, region: str = "rotterdam"):
    """
    Supply chain news aggregated from RSS feeds for the given port region.
    Cached per region for 1 hour.
    region: rotterdam | hamburg | antwerp | istanbul | felixstowe | global
    """
    return await fetch_rotterdam_news(limit=min(limit, 50), region=region)


@app.get("/news/risks")
async def get_news_risks(region: str = "rotterdam"):
    """
    Scan cached news for route-risk signals without running a simulation.
    Returns all signals grouped by severity + a top-level summary.
    """
    news_data = await fetch_rotterdam_news(limit=50, region=region)
    articles = news_data.get("articles", [])
    signals = extract_risk_signals(articles)
    return {
        "summary":  build_risk_summary(signals),
        "signals":  signals,
        "articles_scanned": len(articles),
    }


@app.get("/route-map")
async def get_route_map(destination_id: str = "dk_aarhus"):
    """Dynamic route geometry for the Leaflet.js interactive map."""
    import math
    from services.simulation import _DESTINATIONS

    dest = _DESTINATIONS.get(destination_id, _DESTINATIONS["dk_aarhus"])

    sha_lat, sha_lng = 31.2304, 121.4737
    pvg_lat, pvg_lng = 31.1434, 121.8052

    hub_name = dest.get("hub_port_name", "Hub Port")
    hub_lat  = dest.get("hub_port_lat", 51.923)
    hub_lng  = dest.get("hub_port_lng", 4.479)

    city_name = dest.get("city_name", dest.get("name", "Destination"))
    dest_lat  = dest.get("lat", hub_lat)
    dest_lng  = dest.get("lng", hub_lng)

    air_code = dest.get("air_airport_code", "Dest Airport")
    air_lat  = dest.get("air_airport_lat", dest_lat)
    air_lng  = dest.get("air_airport_lng", dest_lng)

    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        return round(R * 2 * math.asin(math.sqrt(a)))

    ocean_km = _haversine(sha_lat, sha_lng, hub_lat, hub_lng)
    road_km  = _haversine(hub_lat, hub_lng, dest_lat, dest_lng)
    air_km   = _haversine(pvg_lat, pvg_lng, air_lat, air_lng)

    ocean_days = max(14, round(ocean_km / 754))
    road_days  = max(1, round(road_km / 600))
    air_days   = max(1, round(air_km / 5000) + 1)

    return {
        "waypoints": [
            {"name": "Shanghai (CNSHA)", "lat": sha_lat, "lng": sha_lng, "type": "origin"},
            {"name": hub_name,           "lat": hub_lat, "lng": hub_lng, "type": "hub"},
            {"name": city_name,          "lat": dest_lat, "lng": dest_lng, "type": "destination"},
        ],
        "legs": [
            {
                "from": "Shanghai (CNSHA)",
                "to": hub_name,
                "mode": "ocean",
                "distance_km": ocean_km,
                "label": f"Ocean freight (~{ocean_days} days)",
            },
            {
                "from": hub_name,
                "to": city_name,
                "mode": "road",
                "distance_km": road_km,
                "label": f"Road ({road_days}–{road_days + 1} days)",
            },
        ],
        "air_waypoints": [
            {"name": "Shanghai Pudong (PVG)", "lat": pvg_lat, "lng": pvg_lng, "type": "origin"},
            {"name": air_code,                "lat": air_lat, "lng": air_lng, "type": "destination"},
        ],
        "air_legs": [
            {
                "from": "Shanghai Pudong (PVG)",
                "to": air_code,
                "mode": "air",
                "distance_km": air_km,
                "label": f"Air freight (~{air_days} days)",
            },
        ],
    }


@app.get("/cache/stats")
async def get_cache_stats():
    return await cache_stats()


@app.delete("/cache/news")
async def clear_news_cache():
    """Delete all cached news entries so next /news call re-fetches from RSS."""
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("DELETE FROM api_cache WHERE cache_key LIKE 'news:%'")
        await db.commit()
        return {"deleted": cur.rowcount}
