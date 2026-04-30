"""
News × Route Intelligence — maps live RSS articles to route-level risk signals.

For each cached news article, this module checks title + summary for keywords
that indicate risk relevant to specific freight routes on the China → Denmark lane.
Returns a list of deduplicated risk signals sorted by severity.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RiskLevel(str, Enum):
    HIGH   = "high"
    MEDIUM = "medium"
    LOW    = "low"


@dataclass
class RiskSignal:
    route_types: list[str]          # e.g. ["ocean_fcl", "ocean_lcl"]
    level: RiskLevel
    label: str                      # short human label, e.g. "Port congestion"
    detail: str                     # one-sentence explanation
    article_title: str
    article_url: str
    article_source: str


# ---------------------------------------------------------------------------
# Keyword → risk mapping
# Each entry: (keyword_lower, route_types_affected, level, label, detail_template)
# ---------------------------------------------------------------------------
_RULES: list[tuple[str, list[str], RiskLevel, str, str]] = [
    # Port of Rotterdam disruption — hits all ocean routes
    ("congestion",        ["ocean_fcl", "ocean_lcl"],  RiskLevel.HIGH,   "Port congestion",       "Port congestion may add 2–5 days to Rotterdam dwell time."),
    ("strike",            ["ocean_fcl", "ocean_lcl", "air"],  RiskLevel.HIGH,   "Labor strike",          "Strikes can halt loading/unloading and delay all modes."),
    ("closure",           ["ocean_fcl", "ocean_lcl"],  RiskLevel.HIGH,   "Port closure",          "Port or terminal closure may force rerouting or delays."),
    ("disruption",        ["ocean_fcl", "ocean_lcl", "air"],  RiskLevel.MEDIUM, "Route disruption",      "Reported disruption may affect transit reliability."),
    ("delay",             ["ocean_fcl", "ocean_lcl", "air"],  RiskLevel.MEDIUM, "Reported delays",       "General delay signal detected in news."),
    ("backlog",           ["ocean_fcl", "ocean_lcl"],  RiskLevel.MEDIUM, "Container backlog",     "Container backlog can extend lead times by 1–7 days."),
    ("capacity",          ["ocean_fcl", "ocean_lcl", "air"],  RiskLevel.LOW,    "Capacity pressure",     "Tight capacity may push up spot rates."),

    # Suez Canal / Red Sea — critical for CNSHA→NLRTM ocean routes
    ("suez",              ["ocean_fcl", "ocean_lcl"],  RiskLevel.HIGH,   "Suez Canal risk",       "Suez Canal disruption forces Cape of Good Hope rerouting (+12–14 days)."),
    ("red sea",           ["ocean_fcl", "ocean_lcl"],  RiskLevel.HIGH,   "Red Sea risk",          "Red Sea attacks force diversions — adds 10–14 days and fuel costs."),
    ("houthi",            ["ocean_fcl", "ocean_lcl"],  RiskLevel.HIGH,   "Red Sea attacks",       "Houthi attacks in Red Sea actively divert ocean routes."),
    ("cape of good hope", ["ocean_fcl", "ocean_lcl"],  RiskLevel.MEDIUM, "Cape diversion active", "Ships diverting around Africa — 12–14 extra days, +15–20% cost."),

    # Freight rate movements
    ("rate increase",     ["ocean_fcl", "ocean_lcl", "air"],  RiskLevel.MEDIUM, "Freight rate increase",  "Spot rates are rising — benchmark estimates may be understated."),
    ("rate spike",        ["ocean_fcl", "ocean_lcl", "air"],  RiskLevel.HIGH,   "Freight rate spike",     "Sharp rate spike detected — current estimates may understate actual costs."),
    ("surcharge",         ["ocean_fcl", "ocean_lcl"],  RiskLevel.MEDIUM, "New carrier surcharge",  "Carriers adding surcharges — check for GRI, ECA, or PSS additions."),
    ("blank sailing",     ["ocean_fcl", "ocean_lcl"],  RiskLevel.HIGH,   "Blank sailings",         "Blank sailing announcements reduce capacity and push rates up."),
    ("void sailing",      ["ocean_fcl", "ocean_lcl"],  RiskLevel.HIGH,   "Void sailings",          "Carriers cancelling sailings — capacity tightening."),

    # Air freight
    ("airspace",          ["air"],                     RiskLevel.HIGH,   "Airspace restriction",   "Airspace restrictions may reroute cargo flights and add fuel/time costs."),
    ("air cargo",         ["air"],                     RiskLevel.LOW,    "Air cargo update",       "Air cargo market update may affect rates or capacity."),
    ("belly capacity",    ["air"],                     RiskLevel.MEDIUM, "Belly capacity change",  "Changes in belly cargo capacity affect air freight pricing."),

    # Customs / tariffs
    ("tariff",            ["ocean_fcl", "ocean_lcl", "air"],  RiskLevel.MEDIUM, "Tariff change signal",  "New tariff or duty announcement may affect landed cost."),
    ("customs",           ["ocean_fcl", "ocean_lcl", "air"],  RiskLevel.LOW,    "Customs update",        "Customs process change may affect clearance time."),
    ("sanction",          ["ocean_fcl", "ocean_lcl", "air"],  RiskLevel.HIGH,   "Trade sanction",        "Sanctions can block specific carriers, ports, or goods."),

    # Weather / force majeure
    ("storm",             ["ocean_fcl", "ocean_lcl", "air"],  RiskLevel.MEDIUM, "Weather risk",          "Severe weather may delay ocean or air departures."),
    ("typhoon",           ["ocean_fcl", "ocean_lcl", "air"],  RiskLevel.HIGH,   "Typhoon warning",       "Typhoon near China or trans-Pacific route — expect departure delays."),
    ("flood",             ["ocean_fcl", "ocean_lcl"],  RiskLevel.MEDIUM, "Flood risk",            "Flooding near port or inland road may disrupt origin/destination legs."),

    # Rotterdam-specific positive signals
    ("throughput record", ["ocean_fcl", "ocean_lcl"],  RiskLevel.LOW,    "Port efficiency up",    "Rotterdam reporting strong throughput — positive for transit reliability."),
    ("new terminal",      ["ocean_fcl", "ocean_lcl"],  RiskLevel.LOW,    "Capacity expansion",    "New terminal capacity improves long-term reliability."),
]


def _text(article: dict) -> str:
    """Combine title + summary into one lowercase searchable string."""
    return f"{article.get('title', '')} {article.get('summary', '')}".lower()


def extract_risk_signals(articles: list[dict]) -> list[dict]:
    """
    Scan article titles and summaries for route-risk keywords.

    Returns a deduplicated list of risk signal dicts, sorted:
      HIGH first, then MEDIUM, then LOW.
    Each signal de-duplicates by (label, article_url) — one signal per rule per article.
    """
    seen: set[tuple[str, str]] = set()
    signals: list[RiskSignal] = []

    for article in articles:
        text = _text(article)
        for keyword, route_types, level, label, detail in _RULES:
            if keyword not in text:
                continue
            key = (label, article.get("url", ""))
            if key in seen:
                continue
            seen.add(key)
            signals.append(RiskSignal(
                route_types=route_types,
                level=level,
                label=label,
                detail=detail,
                article_title=article.get("title", ""),
                article_url=article.get("url", ""),
                article_source=article.get("source", ""),
            ))

    # Sort: HIGH → MEDIUM → LOW
    order = {RiskLevel.HIGH: 0, RiskLevel.MEDIUM: 1, RiskLevel.LOW: 2}
    signals.sort(key=lambda s: order[s.level])

    return [
        {
            "route_types":    s.route_types,
            "level":          s.level.value,
            "label":          s.label,
            "detail":         s.detail,
            "article_title":  s.article_title,
            "article_url":    s.article_url,
            "article_source": s.article_source,
        }
        for s in signals
    ]


def signals_for_route(all_signals: list[dict], freight_mode: str) -> list[dict]:
    """
    Filter a pre-computed signal list to only those affecting a given freight mode.
    freight_mode: "ocean_fcl" | "ocean_lcl" | "air"
    """
    return [s for s in all_signals if freight_mode in s["route_types"]]


def route_risk_summary(all_signals: list[dict]) -> dict:
    """
    Return a top-level summary dict for the simulation response.
    {
      "total": int,
      "high": int,
      "medium": int,
      "low": int,
      "top_label": str | None,   # label of first HIGH signal, or first MEDIUM if no HIGH
    }
    """
    counts = {"high": 0, "medium": 0, "low": 0}
    top_label: Optional[str] = None

    for s in all_signals:
        counts[s["level"]] += 1

    for s in all_signals:
        if s["level"] == "high":
            top_label = s["label"]
            break
    if top_label is None:
        for s in all_signals:
            if s["level"] == "medium":
                top_label = s["label"]
                break

    return {
        "total":     sum(counts.values()),
        "high":      counts["high"],
        "medium":    counts["medium"],
        "low":       counts["low"],
        "top_label": top_label,
    }
