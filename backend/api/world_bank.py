"""
World Bank Logistics Performance Index (LPI) API client.
Free, no API key required.
Endpoint: https://api.worldbank.org/v2/
"""
import httpx
from api.benchmark import DataPoint, get_country, _now
from db.cache import cache_get, cache_set
from config import WORLD_BANK_API_BASE, CACHE_TTL, HTTP_TIMEOUT

# World Bank indicator code for LPI overall score
LPI_INDICATOR = "LP.LPI.OVRL.XQ"


async def get_lpi(iso2: str) -> DataPoint:
    """Fetch LPI score for a country. Falls back to country_list.json value."""
    params = {"iso2": iso2, "indicator": "lpi"}
    cached = await cache_get("world_bank_lpi", params)
    if cached:
        return DataPoint(**cached)

    country_data = get_country(iso2)
    fallback_score = country_data["lpi_score_fallback"] if country_data else 3.0
    fallback_source = country_data.get("lpi_source", "World Bank LPI 2023 estimate") if country_data else "default"

    try:
        # World Bank uses ISO3 codes
        iso3 = country_data["iso3"] if country_data else iso2
        url = f"{WORLD_BANK_API_BASE}/country/{iso3}/indicator/{LPI_INDICATOR}"
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            resp = await client.get(url, params={"format": "json", "mrv": 1, "per_page": 1})
            resp.raise_for_status()
            data = resp.json()

        if isinstance(data, list) and len(data) > 1 and data[1]:
            entry = data[1][0]
            value = entry.get("value")
            if value is not None:
                dp = DataPoint(
                    value=float(value),
                    unit="LPI score (1-5)",
                    source="World Bank LPI API (live)",
                    timestamp=_now(),
                    confidence="live",
                    error_low=float(value) - 0.2,
                    error_high=float(value) + 0.2,
                )
                await cache_set("world_bank_lpi", params, dp.to_dict(), CACHE_TTL["lpi_scores"])
                return dp
    except Exception:
        pass

    dp = DataPoint(
        value=fallback_score,
        unit="LPI score (1-5)",
        source=fallback_source,
        timestamp=_now(),
        confidence="benchmark",
        error_low=fallback_score - 0.3,
        error_high=fallback_score + 0.3,
    )
    await cache_set("world_bank_lpi", params, dp.to_dict(), CACHE_TTL["lpi_scores"])
    return dp


async def get_lpi_both(dest_iso2: str = "DK") -> tuple[DataPoint, DataPoint]:
    """Returns (china_lpi, destination_lpi)."""
    cn = await get_lpi("CN")
    dest = await get_lpi(dest_iso2)
    return cn, dest
