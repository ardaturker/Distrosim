"""
Rotterdam supply chain news fetcher.
Aggregates RSS feeds from Port of Rotterdam, shipping news sources,
and container/freight trade publications. Filters for Rotterdam relevance.
Caches results for 1 hour.
"""
from __future__ import annotations
import asyncio
import time
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any

import feedparser
import httpx

from db.cache import cache_get, cache_set
from config import HTTP_TIMEOUT

SUPPLY_CHAIN_KEYWORDS = [
    "container", "freight", "shipping", "logistics", "cargo", "supply chain",
    "congestion", "dwell time", "TEU", "fcl", "lcl", "vessel", "port",
    "customs", "tariff", "demurrage", "detention",
]

# Region definitions — region_id → config
REGIONS: dict[str, dict] = {
    "rotterdam": {
        "label": "Rotterdam (NL)",
        "label_tr": "Rotterdam (NL)",
        "port_keywords": ["rotterdam", "maasvlakte", "port of rotterdam", "eur terminal", "ECT", "hutchison ports"],
        "feeds": [
            {"name": "Port of Rotterdam", "url": "https://www.portofrotterdam.com/rss.xml", "category": "port_official", "weight": 3},
            {"name": "Hellenic Shipping News", "url": "https://www.hellenicshippingnews.com/feed/", "category": "shipping", "weight": 2},
            {"name": "Supply Chain Dive", "url": "https://www.supplychaindive.com/feeds/news/", "category": "supply_chain", "weight": 2},
            {"name": "Container News", "url": "https://container-news.com/feed/", "category": "container", "weight": 2},
            {"name": "The Loadstar", "url": "https://theloadstar.com/feed/", "category": "freight", "weight": 2},
        ],
    },
    "hamburg": {
        "label": "Hamburg (DE)",
        "label_tr": "Hamburg (DE)",
        "port_keywords": ["hamburg", "port of hamburg", "hhla", "hamburger hafen", "elbe"],
        "feeds": [
            {"name": "Port of Hamburg", "url": "https://www.hafen-hamburg.de/en/rss/news.xml", "category": "port_official", "weight": 3},
            {"name": "Hellenic Shipping News", "url": "https://www.hellenicshippingnews.com/feed/", "category": "shipping", "weight": 2},
            {"name": "Supply Chain Dive", "url": "https://www.supplychaindive.com/feeds/news/", "category": "supply_chain", "weight": 2},
            {"name": "The Loadstar", "url": "https://theloadstar.com/feed/", "category": "freight", "weight": 2},
            {"name": "Container News", "url": "https://container-news.com/feed/", "category": "container", "weight": 2},
        ],
    },
    "antwerp": {
        "label": "Antwerp (BE)",
        "label_tr": "Antwerp (BE)",
        "port_keywords": ["antwerp", "port of antwerp", "antwerp-bruges", "psa antwerp", "schelde"],
        "feeds": [
            {"name": "Port of Antwerp", "url": "https://www.portofantwerpbruges.com/en/rss", "category": "port_official", "weight": 3},
            {"name": "Hellenic Shipping News", "url": "https://www.hellenicshippingnews.com/feed/", "category": "shipping", "weight": 2},
            {"name": "Supply Chain Dive", "url": "https://www.supplychaindive.com/feeds/news/", "category": "supply_chain", "weight": 2},
            {"name": "Container News", "url": "https://container-news.com/feed/", "category": "container", "weight": 2},
            {"name": "The Loadstar", "url": "https://theloadstar.com/feed/", "category": "freight", "weight": 2},
        ],
    },
    "istanbul": {
        "label": "Istanbul (TR)",
        "label_tr": "İstanbul (TR)",
        "port_keywords": ["istanbul", "ambarli", "kumport", "evyap", "marport", "turkey", "türkiye", "bosphorus"],
        "feeds": [
            {"name": "Hellenic Shipping News", "url": "https://www.hellenicshippingnews.com/feed/", "category": "shipping", "weight": 2},
            {"name": "Supply Chain Dive", "url": "https://www.supplychaindive.com/feeds/news/", "category": "supply_chain", "weight": 2},
            {"name": "Container News", "url": "https://container-news.com/feed/", "category": "container", "weight": 2},
            {"name": "The Loadstar", "url": "https://theloadstar.com/feed/", "category": "freight", "weight": 2},
        ],
    },
    "felixstowe": {
        "label": "Felixstowe (UK)",
        "label_tr": "Felixstowe (UK)",
        "port_keywords": ["felixstowe", "port of felixstowe", "hutchison ports uk", "tilbury", "southampton"],
        "feeds": [
            {"name": "Hellenic Shipping News", "url": "https://www.hellenicshippingnews.com/feed/", "category": "shipping", "weight": 2},
            {"name": "Supply Chain Dive", "url": "https://www.supplychaindive.com/feeds/news/", "category": "supply_chain", "weight": 2},
            {"name": "Container News", "url": "https://container-news.com/feed/", "category": "container", "weight": 2},
            {"name": "The Loadstar", "url": "https://theloadstar.com/feed/", "category": "freight", "weight": 2},
        ],
    },
    "global": {
        "label": "Global Shipping",
        "label_tr": "Küresel Taşımacılık",
        "port_keywords": [],
        "feeds": [
            {"name": "Hellenic Shipping News", "url": "https://www.hellenicshippingnews.com/feed/", "category": "shipping", "weight": 2},
            {"name": "Supply Chain Dive", "url": "https://www.supplychaindive.com/feeds/news/", "category": "supply_chain", "weight": 2},
            {"name": "Container News", "url": "https://container-news.com/feed/", "category": "container", "weight": 2},
            {"name": "The Loadstar", "url": "https://theloadstar.com/feed/", "category": "freight", "weight": 2},
        ],
    },
}


def _parse_date(entry: Any) -> str:
    """Extract ISO date string from a feed entry."""
    for attr in ("published", "updated", "created"):
        raw = getattr(entry, attr, None)
        if raw:
            try:
                dt = parsedate_to_datetime(raw)
                return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                pass
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _relevance_score(title: str, summary: str, source_weight: int, port_keywords: list[str]) -> int:
    """Score 0–100 — higher = more relevant to the selected region's port."""
    text = (title + " " + summary).lower()
    score = 0
    for kw in port_keywords:
        if kw in text:
            score += 20
    for kw in SUPPLY_CHAIN_KEYWORDS:
        if kw in text:
            score += 5
    score += source_weight * 5
    return min(score, 100)


def _is_relevant(title: str, summary: str, source_weight: int) -> bool:
    """Return True if the article is relevant enough to include."""
    text = (title + " " + summary).lower()
    if source_weight >= 3:
        return True
    has_sc = any(kw in text for kw in SUPPLY_CHAIN_KEYWORDS)
    return has_sc


async def _fetch_feed(session: httpx.AsyncClient, source: dict) -> list[dict]:
    """Fetch and parse a single RSS feed. Returns list of article dicts."""
    import re
    try:
        resp = await session.get(source["url"], timeout=HTTP_TIMEOUT, follow_redirects=True)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        articles = []
        for entry in feed.entries[:15]:  # max 15 per source
            title = getattr(entry, "title", "Untitled")
            summary = getattr(entry, "summary", "")
            summary = re.sub(r"<[^>]+>", "", summary).strip()[:300]
            link = getattr(entry, "link", "#")
            pub_date = _parse_date(entry)

            if not _is_relevant(title, summary, source["weight"]):
                continue

            articles.append({
                "title": title,
                "summary": summary,
                "url": link,
                "source": source["name"],
                "category": source["category"],
                "published_at": pub_date,
                "relevance_score": _relevance_score(title, summary, source["weight"], []),
                "rotterdam_tagged": False,  # recomputed per-region in fetch_rotterdam_news
            })
        return articles
    except Exception as exc:
        return [{"_error": str(exc), "_source": source["name"]}]  # propagate error for diagnostics


def _strip_errors(articles: list[dict]) -> tuple[list[dict], list[str]]:
    """Separate real articles from error sentinels."""
    clean, errors = [], []
    for a in articles:
        if "_error" in a:
            errors.append(f"{a['_source']}: {a['_error']}")
        else:
            clean.append(a)
    return clean, errors


async def fetch_rotterdam_news(limit: int = 30, region: str = "rotterdam") -> dict:
    """
    Fetch and aggregate news from all sources for the given region.
    Returns cached result if fresh (< 1 hour old).
    region: one of REGIONS keys — "rotterdam", "hamburg", "antwerp", "istanbul", "felixstowe", "global"
    """
    region_cfg = REGIONS.get(region, REGIONS["rotterdam"])
    port_keywords = region_cfg["port_keywords"]
    feed_sources  = region_cfg["feeds"]

    params = {"type": "port_news", "region": region, "limit": limit, "v": 3}
    cached = await cache_get("news", params)
    if cached:
        return cached

    async with httpx.AsyncClient(headers={"User-Agent": "DistroSim/1.0 (supply chain research)"}) as session:
        tasks = [_fetch_feed(session, src) for src in feed_sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    raw_articles: list[dict] = []
    sources_ok: list[str] = []
    sources_failed: list[str] = []

    for i, result in enumerate(results):
        source_name = feed_sources[i]["name"]
        if isinstance(result, list):
            raw_articles.extend(result)
            sources_ok.append(source_name)
        else:
            sources_failed.append(source_name)

    all_articles, feed_errors = _strip_errors(raw_articles)

    # Mark sources that returned only errors as failed
    for err in feed_errors:
        src = err.split(":")[0]
        if src in sources_ok:
            sources_ok.remove(src)
            sources_failed.append(src)

    # Recompute relevance scores and port_tagged using region keywords
    for a in all_articles:
        a["relevance_score"] = _relevance_score(a["title"], a["summary"], 2, port_keywords)
        a["rotterdam_tagged"] = bool(port_keywords) and any(
            kw in (a["title"] + " " + a["summary"]).lower() for kw in port_keywords
        )

    # Sort: port-tagged first, then by relevance score
    all_articles.sort(key=lambda a: (-int(a["rotterdam_tagged"]), -a["relevance_score"]))

    trimmed = all_articles[:limit]

    output = {
        "articles": trimmed,
        "total": len(trimmed),
        "sources_ok": sources_ok,
        "sources_failed": sources_failed,
        "feed_errors": feed_errors,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "cache_ttl_minutes": 60,
        "region": region,
        "region_label": region_cfg["label"],
        "note": f"Aggregated from supply chain RSS feeds. Filtered for {region_cfg['label']} relevance.",
    }

    await cache_set("news", params, output, ttl=3600)
    return output


def get_region_list() -> list[dict]:
    """Return list of available news regions for the frontend."""
    return [
        {"id": rid, "label": cfg["label"], "label_tr": cfg.get("label_tr", cfg["label"])}
        for rid, cfg in REGIONS.items()
    ]
