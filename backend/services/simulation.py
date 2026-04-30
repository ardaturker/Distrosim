"""
Simulation orchestrator.
Builds routes → calculates steps → applies ML adjustments → ranks → returns results.
"""
from __future__ import annotations
import asyncio
import time
import uuid
from datetime import datetime

import json
from pathlib import Path

from services.route_builder import build_routes, RouteDef
from services.step_calculator import StepCalculator, StepResult
from api.world_bank import get_lpi_both
from api.co2 import calculate_co2
from api.news import fetch_rotterdam_news
from api.news_intelligence import extract_risk_signals, signals_for_route, route_risk_summary
from models.cost_predictor import predict_cost_multiplier
from models.lead_time_predictor import predict_lead_time_multiplier
from models.error_margin import get_step_interval, route_confidence_score
from models.route_optimizer import rank_routes
from config import DEMO_PRODUCT

_DATA_DIR = Path(__file__).parent.parent.parent / "data"

def _load_destinations() -> dict:
    path = _DATA_DIR / "destinations.json"
    dests = json.loads(path.read_text())
    return {d["id"]: d for d in dests}

_DESTINATIONS = _load_destinations()


async def run_simulation(req: dict) -> dict:
    """
    Main simulation entry point.

    req keys: product_name, hs_code, production_cost_usd, product_value_usd,
              weight_kg, length_cm, width_cm, height_cm, annual_volume,
              freight_mode_preference, last_mile_preference,
              weight_cost, weight_time, weight_reliability
    """
    t0 = time.time()

    hs_code              = req.get("hs_code", "9032.10")
    hs_chapter           = int(hs_code.replace(".", "")[:2])
    annual_volume        = int(req.get("annual_volume", 5000))
    freight_pref         = req.get("freight_mode_preference", "all")
    last_mile_pref       = req.get("last_mile_preference", "both")
    weight_cost          = float(req.get("weight_cost", 0.40))
    weight_time          = float(req.get("weight_time", 0.30))
    weight_rel           = float(req.get("weight_reliability", 0.30))
    tariff_surcharge_pct = float(req.get("tariff_surcharge_pct", 0.0))
    destination_id       = req.get("destination_id", "dk_aarhus")
    destination          = _DESTINATIONS.get(destination_id, _DESTINATIONS["dk_aarhus"])

    # Normalize weights
    total_w = weight_cost + weight_time + weight_rel
    if total_w > 0:
        weight_cost /= total_w
        weight_time /= total_w
        weight_rel  /= total_w

    # Fetch LPI scores + news articles in parallel (both use dynamic destination)
    dest_iso2   = destination.get("country_code", "DK")
    dest_region = destination.get("region_id", "global")
    (cn_lpi, dest_lpi), news_data = await asyncio.gather(
        get_lpi_both(dest_iso2=dest_iso2),
        fetch_rotterdam_news(limit=50, region=dest_region),
    )
    all_articles = news_data.get("articles", [])
    lpi_avg = (cn_lpi.value + dest_lpi.value) / 2

    # Pre-compute news risk signals once for all routes
    all_signals = extract_risk_signals(all_articles)

    weight_kg_val = float(req.get("weight_kg", 0.5))

    # Step calculator
    calc = StepCalculator(
        hs_code=hs_code,
        production_cost_usd=float(req.get("production_cost_usd", 8.0)),
        product_value_usd=float(req.get("product_value_usd", 35.0)),
        weight_kg=weight_kg_val,
        length_cm=float(req.get("length_cm", 15.0)),
        width_cm=float(req.get("width_cm", 10.0)),
        height_cm=float(req.get("height_cm", 3.0)),
        annual_volume=annual_volume,
    )
    calc.tariff_surcharge_pct = tariff_surcharge_pct
    calc.destination = destination
    calc.lane = destination.get("benchmark_lane", "CHN-DNK")
    calc.inland_country = destination.get("inland_benchmark_country", "DNK")

    # Build route definitions (pass destination for dynamic step labels)
    route_defs = build_routes(freight_pref, last_mile_pref, destination=destination)

    # Calculate each route
    route_results = []
    api_sources_used: set[str] = set()
    fallback_steps: list[str] = []

    for rdef in route_defs:
        step_results: list[StepResult] = []

        for sdef in rdef.steps:
            sr = await calc.calculate(sdef.step_id, sdef.name, sdef.mode)

            # Apply conformal prediction intervals on top of benchmark error bounds
            ml_low, ml_high = get_step_interval(
                step_id=sdef.step_id,
                base_cost=sr.cost_per_unit_usd,
                freight_mode=rdef.freight_mode,
                lpi_avg=lpi_avg,
                annual_volume=annual_volume,
                weight_kg=float(req.get("weight_kg", 0.5)),
            )
            # Use the wider of: benchmark bounds vs ML conformal bounds
            sr.error_low_usd = min(sr.error_low_usd, ml_low)
            sr.error_high_usd = max(sr.error_high_usd, ml_high)

            step_results.append(sr)
            api_sources_used.add(sr.source.split("—")[0].strip()[:40])
            if sr.confidence == "benchmark":
                fallback_steps.append(f"{rdef.route_id}/{sdef.step_id}")

        # CO2 emissions (GLEC Framework v3)
        co2_result = calculate_co2(rdef.freight_mode, weight_kg_val, annual_volume, destination)

        # Route-specific risk signals from live news
        route_signals = signals_for_route(all_signals, rdef.freight_mode)

        # ML cost + time adjustments
        cbm = calc.cbm_per_unit
        cost_mult = predict_cost_multiplier(
            lpi_origin=cn_lpi.value,
            lpi_dest=dest_lpi.value,
            freight_mode=rdef.freight_mode,
            weight_kg=weight_kg_val,
            cbm=cbm,
            annual_volume=annual_volume,
            hs_chapter=hs_chapter,
            last_mile=rdef.last_mile_type,
        )
        lead_mult = predict_lead_time_multiplier(
            lpi_origin=cn_lpi.value,
            lpi_dest_customs=dest_lpi.value,
            freight_mode=rdef.freight_mode,
        )

        # Sum up costs and times
        total_cost = sum(s.cost_per_unit_usd for s in step_results)
        total_cost_ml = total_cost * max(0.7, min(cost_mult, 1.5))  # clamp multiplier
        total_time = sum(s.lead_time_days for s in step_results)
        total_time_ml = total_time * max(0.7, min(lead_mult, 1.5))

        total_error_low = sum(s.error_low_usd for s in step_results)
        total_error_high = sum(s.error_high_usd for s in step_results)

        conf_score = route_confidence_score([s.to_dict() for s in step_results])

        route_results.append({
            "route_id":                 rdef.route_id,
            "route_name":               rdef.route_name,
            "freight_mode":             rdef.freight_mode,
            "last_mile_type":           rdef.last_mile_type,
            "description":              rdef.description,
            "steps":                    [s.to_dict() for s in step_results],
            "total_cost_per_unit_usd":  round(total_cost_ml, 2),
            "total_cost_benchmark_usd": round(total_cost, 2),
            "total_lead_time_days":     round(total_time_ml, 1),
            "total_lead_time_benchmark_days": round(total_time, 1),
            "ml_cost_multiplier":       round(cost_mult, 3),
            "ml_lead_multiplier":       round(lead_mult, 3),
            "error_low_usd":            round(total_error_low, 2),
            "error_high_usd":           round(total_error_high, 2),
            "confidence_score":         conf_score,
            # CO2 emissions (GLEC Framework v3 / ISO 14083)
            "co2_kg_per_unit":          co2_result.kg_co2e_per_unit,
            "co2_breakdown":            co2_result.breakdown,
            "co2_methodology":          co2_result.methodology,
            # News × Route Intelligence
            "risk_signals":             route_signals,
            "risk_signal_count":        len(route_signals),
            "risk_level":               route_signals[0]["level"] if route_signals else "none",
        })

    # Rank routes
    route_results = rank_routes(
        route_results,
        weight_cost=weight_cost,
        weight_time=weight_time,
        weight_reliability=weight_rel,
    )

    elapsed = round(time.time() - t0, 2)

    return {
        "simulation_id":     str(uuid.uuid4())[:8],
        "timestamp":         datetime.utcnow().isoformat() + "Z",
        "elapsed_s":         elapsed,
        "product": {
            "name":           req.get("product_name", "Unknown"),
            "hs_code":        hs_code,
            "annual_volume":  annual_volume,
            "weight_kg":      weight_kg_val,
            "value_usd":      float(req.get("product_value_usd", 35.0)),
        },
        "lane": {
            "origin":           "China (Shanghai / CNSHA)",
            "destination":      destination["name"],
            "destination_id":   destination["id"],
            "destination_flag": destination.get("flag", ""),
            "hub_port":         destination.get("hub_port_name", ""),
            "origin_lpi":       {"value": round(cn_lpi.value, 2), "source": cn_lpi.source},
            "dest_lpi":         {"value": round(dest_lpi.value, 2), "source": dest_lpi.source},
        },
        "tariff_scenario": {
            "surcharge_pct":  tariff_surcharge_pct,
            "label":          (
                "China +301 (25%)" if tariff_surcharge_pct == 25.0
                else f"Custom (+{tariff_surcharge_pct}%)" if tariff_surcharge_pct > 0
                else "Standard (MFN only)"
            ),
        },
        "route_risk_summary":  route_risk_summary(all_signals),
        "routes":              route_results,
        "num_routes":          len(route_results),
        "api_sources_used":    sorted(api_sources_used),
        "fallback_step_count": len(set(fallback_steps)),
        "data_freshness":      "Live APIs used where available. Benchmark fallback applied to freight/last-mile costs.",
    }
