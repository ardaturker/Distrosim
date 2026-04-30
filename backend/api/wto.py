"""
WTO Tariff API client — fetches MFN tariff rate by HS code + reporter country.
Free, no key required (optional key increases rate limits).
Endpoint: https://api.wto.org/timeseries/v1/
"""
import httpx
from api.benchmark import DataPoint, import_duty_rate_fallback, _now
from db.cache import cache_get, cache_set
from config import WTO_API_BASE, WTO_API_KEY, CACHE_TTL, HTTP_TIMEOUT

# WTO reporter code for EU/Denmark
EU_REPORTER = "EUN"   # EU as a bloc (Denmark uses EU tariff schedule)


async def get_mfn_duty(hs_code: str, reporter: str = EU_REPORTER) -> DataPoint:
    """
    Fetch MFN ad valorem duty rate for a given HS code.
    hs_code: e.g. "9032.10" — strips dots and uses 6-digit HS
    reporter: WTO reporter code (default EU)
    Falls back to benchmark chapter rate if API fails.
    """
    hs_clean = hs_code.replace(".", "")[:6]
    hs_chapter = hs_clean[:2]

    params = {"hs": hs_clean, "reporter": reporter}
    cached = await cache_get("wto_mfn", params)
    if cached:
        return DataPoint(**cached)

    try:
        headers = {}
        if WTO_API_KEY:
            headers["Ocp-Apim-Subscription-Key"] = WTO_API_KEY

        url = f"{WTO_API_BASE}/data"
        query = {
            "i": "HS_MFN_ADVALOREM",
            "r": reporter,
            "ps": "2023",
            "pc": hs_clean,
            "fmt": "json",
            "per_page": 5,
        }
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            resp = await client.get(url, params=query, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        # WTO response: {"Dataset": [{"Value": 1.7, ...}], ...}
        dataset = data.get("Dataset", [])
        if dataset:
            values = [d["Value"] for d in dataset if d.get("Value") is not None]
            if values:
                avg_rate = sum(values) / len(values)
                dp = DataPoint(
                    value=round(avg_rate, 2),
                    unit="%",
                    source=f"WTO MFN Tariff API — HS {hs_clean} → EU (live)",
                    timestamp=_now(),
                    confidence="live",
                    error_low=round(min(values), 2),
                    error_high=round(max(values), 2),
                )
                await cache_set("wto_mfn", params, dp.to_dict(), CACHE_TTL["customs_duties"])
                return dp
    except Exception:
        pass

    # Fallback: chapter-level benchmark
    dp = import_duty_rate_fallback(hs_chapter)
    dp.source = f"EU TARIC benchmark — HS chapter {hs_chapter} (WTO API unavailable)"
    await cache_set("wto_mfn", params, dp.to_dict(), CACHE_TTL["customs_duties"])
    return dp


async def get_vat_rate_dk() -> DataPoint:
    """Denmark VAT rate — fixed 25%, no API needed."""
    return DataPoint(
        value=25.0, unit="%",
        source="SKAT (Danish Tax Agency) — fixed 25% since 1992",
        timestamp=_now(), confidence="benchmark",
        error_low=25.0, error_high=25.0,
    )
