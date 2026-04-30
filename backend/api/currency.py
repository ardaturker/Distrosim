"""
ECB Exchange Rate API client.
Free, no key required.
Returns EUR-based rates (CNY, DKK, USD).
"""
import httpx
from api.benchmark import DataPoint, _now
from db.cache import cache_get, cache_set
from config import ECB_API_BASE, CACHE_TTL, HTTP_TIMEOUT

# Fallback rates (approximate mid-2024)
_FALLBACK = {
    "CNY": 7.85,   # EUR 1 = CNY 7.85
    "DKK": 7.46,   # EUR 1 = DKK 7.46
    "USD": 1.08,   # EUR 1 = USD 1.08
}


async def get_eur_rate(currency: str) -> DataPoint:
    """
    Returns: how many units of {currency} per 1 EUR.
    e.g. get_eur_rate("USD") → ~1.08
    """
    currency = currency.upper()
    if currency == "EUR":
        return DataPoint(value=1.0, unit="EUR/EUR", source="Identity", timestamp=_now(), confidence="live", error_low=1.0, error_high=1.0)

    params = {"currency": currency}
    cached = await cache_get("ecb_fx", params)
    if cached:
        return DataPoint(**cached)

    try:
        # ECB SDMX REST API
        url = f"{ECB_API_BASE}/EXR/D.{currency}.EUR.SP00.A"
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            resp = await client.get(url, params={"format": "jsondata", "lastNObservations": 1})
            resp.raise_for_status()
            data = resp.json()

        # Navigate ECB SDMX JSON structure
        series = data["dataSets"][0]["series"]
        obs = list(series.values())[0]["observations"]
        rate = float(list(obs.values())[-1][0])

        dp = DataPoint(
            value=round(rate, 4), unit=f"EUR/{currency}",
            source="ECB Exchange Rate API (live)",
            timestamp=_now(), confidence="live",
            error_low=round(rate * 0.995, 4),
            error_high=round(rate * 1.005, 4),
        )
        await cache_set("ecb_fx", params, dp.to_dict(), CACHE_TTL["exchange_rates"])
        return dp
    except Exception:
        pass

    fallback = _FALLBACK.get(currency, 1.0)
    dp = DataPoint(
        value=fallback, unit=f"EUR/{currency}",
        source=f"ECB API fallback — approximate mid-2024 rate",
        timestamp=_now(), confidence="benchmark",
        error_low=round(fallback * 0.97, 4),
        error_high=round(fallback * 1.03, 4),
    )
    await cache_set("ecb_fx", params, dp.to_dict(), CACHE_TTL["exchange_rates"])
    return dp


async def usd_to_eur(usd_amount: float) -> float:
    """Convert USD amount to EUR using live ECB rate."""
    rate = await get_eur_rate("USD")
    # rate.value = EUR per USD... actually ECB gives units of CCY per EUR
    # get_eur_rate("USD") returns EUR 1 = X USD, so 1 USD = 1/X EUR
    return usd_amount / rate.value


async def eur_to_usd(eur_amount: float) -> float:
    rate = await get_eur_rate("USD")
    return eur_amount * rate.value
