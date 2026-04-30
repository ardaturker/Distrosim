"""
Route scoring and ranking.
Scores each route on: cost (40%), lead time (30%), reliability (30%).
Returns ranked list with trade-off explanations.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class RouteScore:
    route_id: str
    cost_score: float       # 0–100 (100 = cheapest)
    time_score: float       # 0–100 (100 = fastest)
    reliability_score: float  # 0–100 (100 = narrowest CI)
    total_score: float      # weighted composite
    rank: int
    badge: str              # "cheapest" | "fastest" | "most_reliable" | ""
    trade_off: str          # human-readable explanation


def rank_routes(
    routes: list[dict],
    weight_cost: float = 0.40,
    weight_time: float = 0.30,
    weight_reliability: float = 0.30,
) -> list[dict]:
    """
    routes: list of route result dicts with keys:
        route_id, total_cost_per_unit_usd, total_lead_time_days, confidence_score
    Returns the same list with added rank_score, rank, badge, trade_off fields.
    Modifies in place and returns.
    """
    if not routes:
        return routes

    costs = [r["total_cost_per_unit_usd"] for r in routes]
    times = [r["total_lead_time_days"] for r in routes]
    confs = [r.get("confidence_score", 50.0) for r in routes]

    min_cost, max_cost = min(costs), max(costs)
    min_time, max_time = min(times), max(times)

    scores: list[RouteScore] = []
    for r in routes:
        cost_score = _normalize(r["total_cost_per_unit_usd"], min_cost, max_cost, invert=True)
        time_score = _normalize(r["total_lead_time_days"], min_time, max_time, invert=True)
        rel_score = r.get("confidence_score", 50.0)

        total = (
            weight_cost * cost_score
            + weight_time * time_score
            + weight_reliability * rel_score
        )
        scores.append(RouteScore(
            route_id=r["route_id"],
            cost_score=round(cost_score, 1),
            time_score=round(time_score, 1),
            reliability_score=round(rel_score, 1),
            total_score=round(total, 1),
            rank=0,
            badge="",
            trade_off="",
        ))

    # Rank by total score descending
    scores.sort(key=lambda s: s.total_score, reverse=True)
    for i, s in enumerate(scores):
        s.rank = i + 1

    # Assign badges
    cheapest_id = min(routes, key=lambda r: r["total_cost_per_unit_usd"])["route_id"]
    fastest_id = min(routes, key=lambda r: r["total_lead_time_days"])["route_id"]
    most_reliable_id = max(routes, key=lambda r: r.get("confidence_score", 0))["route_id"]

    for s in scores:
        badges = []
        if s.route_id == cheapest_id:
            badges.append("cheapest")
        if s.route_id == fastest_id:
            badges.append("fastest")
        if s.route_id == most_reliable_id:
            badges.append("most_reliable")
        s.badge = badges[0] if badges else ""
        s.trade_off = _make_trade_off(s)

    # Merge scores back into route dicts
    score_map = {s.route_id: s for s in scores}
    for r in routes:
        s = score_map.get(r["route_id"])
        if s:
            r["rank"] = s.rank
            r["rank_score"] = s.total_score
            r["cost_score"] = s.cost_score
            r["time_score"] = s.time_score
            r["reliability_score"] = s.reliability_score
            r["badge"] = s.badge
            r["trade_off"] = s.trade_off

    routes.sort(key=lambda r: r.get("rank", 99))
    return routes


def _normalize(value: float, min_v: float, max_v: float, invert: bool = False) -> float:
    if max_v == min_v:
        return 50.0
    score = (value - min_v) / (max_v - min_v) * 100.0
    if invert:
        score = 100.0 - score
    return round(score, 1)


def _make_trade_off(s: RouteScore) -> str:
    parts = []
    if s.cost_score >= 80:
        parts.append("low cost")
    elif s.cost_score <= 30:
        parts.append("higher cost")

    if s.time_score >= 80:
        parts.append("fast transit")
    elif s.time_score <= 30:
        parts.append("slower transit")

    if s.reliability_score >= 70:
        parts.append("high confidence")
    elif s.reliability_score <= 40:
        parts.append("wider uncertainty")

    if not parts:
        return "Balanced option across cost, time, and reliability."
    return "Best for: " + ", ".join(parts) + "."
