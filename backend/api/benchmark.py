"""
Benchmark data loader — reads data/*.json files and returns DataPoint objects.
Used as fallback when live APIs are unavailable.
"""
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"

_benchmark: dict = {}
_warehouse: dict = {}
_countries: list = []


def _load() -> None:
    global _benchmark, _warehouse, _countries
    if not _benchmark:
        _benchmark = json.loads((DATA_DIR / "benchmark_rates.json").read_text())
    if not _warehouse:
        _warehouse = json.loads((DATA_DIR / "warehouse_costs.json").read_text())
    if not _countries:
        _countries = json.loads((DATA_DIR / "country_list.json").read_text())


@dataclass
class DataPoint:
    value: float
    unit: str
    source: str
    timestamp: str
    confidence: str          # "live" | "cached" | "benchmark"
    error_low: float         # lower bound of 90% CI
    error_high: float        # upper bound of 90% CI

    def to_dict(self) -> dict:
        return self.__dict__


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _dp(avg: float, min_v: float, max_v: float, unit: str, source: str) -> DataPoint:
    return DataPoint(
        value=avg,
        unit=unit,
        source=source,
        timestamp=_now(),
        confidence="benchmark",
        error_low=min_v,
        error_high=max_v,
    )


# ─── Ocean FCL ────────────────────────────────────────────────────────────────

def ocean_fcl_rate(lane: str = "CHN-DNK", container: str = "40ft") -> DataPoint:
    _load()
    d = _benchmark["ocean_fcl"][lane]
    key = f"{container}_usd_per_teu"
    r = d[key]
    return _dp(r["avg"], r["min"], r["max"], r["unit"], d["source"])


def ocean_fcl_transit(lane: str = "CHN-DNK") -> DataPoint:
    _load()
    d = _benchmark["ocean_fcl"][lane]
    r = d["transit_days"]
    return _dp(r["avg"], r["min"], r["max"], "days", d["source"])


# ─── Ocean LCL ────────────────────────────────────────────────────────────────

def ocean_lcl_rate(lane: str = "CHN-DNK") -> DataPoint:
    _load()
    d = _benchmark["ocean_lcl"][lane]
    r = d["usd_per_cbm"]
    return _dp(r["avg"], r["min"], r["max"], r["unit"], d["source"])


def ocean_lcl_surcharge(lane: str = "CHN-DNK") -> DataPoint:
    _load()
    d = _benchmark["ocean_lcl"][lane]
    r = d["surcharges_usd_per_shipment"]
    return _dp(r["avg"], r["min"], r["max"], "USD/shipment", d["source"])


def ocean_lcl_transit(lane: str = "CHN-DNK") -> DataPoint:
    _load()
    d = _benchmark["ocean_lcl"][lane]
    r = d["transit_days"]
    return _dp(r["avg"], r["min"], r["max"], "days", d["source"])


# ─── Air Freight ──────────────────────────────────────────────────────────────

def air_rate(lane: str = "CHN-DNK") -> DataPoint:
    _load()
    d = _benchmark["air_freight"][lane]
    r = d["usd_per_kg"]
    return _dp(r["avg"], r["min"], r["max"], r["unit"], d["source"])


def air_transit(lane: str = "CHN-DNK") -> DataPoint:
    _load()
    d = _benchmark["air_freight"][lane]
    r = d["transit_days"]
    return _dp(r["avg"], r["min"], r["max"], "days", d["source"])


def air_min_charge(lane: str = "CHN-DNK") -> DataPoint:
    _load()
    d = _benchmark["air_freight"][lane]
    r = d["min_charge_usd"]
    return _dp(r["avg"], r["min"], r["max"], "USD/shipment", d["source"])


# ─── Origin inland ────────────────────────────────────────────────────────────

def origin_inland_road(distance_band: str = "regional_50_200km", country: str = "CHN") -> DataPoint:
    _load()
    d = _benchmark["origin_inland_transport"][country]["usd_per_container_to_port"][distance_band]
    src = _benchmark["origin_inland_transport"][country]["source"]
    return _dp(d["avg"], d["min"], d["max"], d["unit"], src)


def origin_inland_air_kg(country: str = "CHN") -> DataPoint:
    _load()
    d = _benchmark["origin_inland_transport"][country]["usd_per_kg_air_to_airport"]
    src = _benchmark["origin_inland_transport"][country]["source"]
    return _dp(d["avg"], d["min"], d["max"], d["unit"], src)


def origin_inland_days(country: str = "CHN") -> DataPoint:
    _load()
    d = _benchmark["origin_inland_transport"][country]["days"]
    src = _benchmark["origin_inland_transport"][country]["source"]
    return _dp(d["avg"], d["min"], d["max"], "days", src)


# ─── Destination inland ───────────────────────────────────────────────────────

def dest_inland_road(distance_band: str = "regional_50_200km", country: str = "DNK") -> DataPoint:
    _load()
    d = _benchmark["destination_inland_transport"][country]["usd_per_container_from_port"][distance_band]
    src = _benchmark["destination_inland_transport"][country]["source"]
    return _dp(d["avg"], d["min"], d["max"], d["unit"], src)


def dest_inland_days(country: str = "DNK") -> DataPoint:
    _load()
    d = _benchmark["destination_inland_transport"][country]["days"]
    src = _benchmark["destination_inland_transport"][country]["source"]
    return _dp(d["avg"], d["min"], d["max"], "days", src)


# ─── THC ──────────────────────────────────────────────────────────────────────

def thc_origin(country: str = "CHN_origin") -> DataPoint:
    _load()
    d = _benchmark["thc"][country]
    r = d["usd_per_teu"]
    return _dp(r["avg"], r["min"], r["max"], r["unit"], d["source"])


def thc_destination(country: str = "DNK_destination") -> DataPoint:
    _load()
    d = _benchmark["thc"][country]
    r = d["usd_per_teu"]
    return _dp(r["avg"], r["min"], r["max"], r["unit"], d["source"])


# ─── Customs ──────────────────────────────────────────────────────────────────

def customs_export_broker(country: str = "CHN") -> DataPoint:
    _load()
    d = _benchmark["customs_export"][country]
    r = d["broker_fee_usd"]
    return _dp(r["avg"], r["min"], r["max"], r["unit"], d["source"])


def customs_import_broker(country: str = "DNK") -> DataPoint:
    _load()
    d = _benchmark["customs_import_broker"][country]
    r = d["broker_fee_usd"]
    return _dp(r["avg"], r["min"], r["max"], r["unit"], d["source"])


def customs_import_days(country: str = "DNK") -> DataPoint:
    _load()
    d = _benchmark["customs_import_broker"][country]
    r = d["days"]
    return _dp(r["avg"], r["min"], r["max"], "days", d["source"])


# ─── Duties ───────────────────────────────────────────────────────────────────

def import_duty_rate_fallback(hs_chapter: str = "90") -> DataPoint:
    _load()
    d = _benchmark["import_duties_fallback"][f"EU_MFN_chapter{hs_chapter}"]
    if isinstance(d.get("rate_percent"), dict):
        r = d["rate_percent"]
        return _dp(r["avg"], r["min"], r["max"], "%", d["source"])
    return _dp(d["rate_percent"], d["rate_percent"], d["rate_percent"], "%", d["source"])


def vat_rate(country: str = "DNK") -> DataPoint:
    _load()
    key = f"EU_VAT_{country}"
    d = _benchmark["import_duties_fallback"].get(key)
    if d:
        v = d["rate_percent"]
        return DataPoint(value=v, unit="%", source=d["source"], timestamp=_now(), confidence="benchmark", error_low=v, error_high=v)
    return DataPoint(value=25.0, unit="%", source="Default EU VAT", timestamp=_now(), confidence="benchmark", error_low=25.0, error_high=25.0)


# ─── Insurance ────────────────────────────────────────────────────────────────

def insurance_rate() -> DataPoint:
    _load()
    d = _benchmark["freight_insurance"]["standard"]
    r = d["rate_percent_of_cif"]
    return _dp(r["avg"], r["min"], r["max"], "% of CIF value", d["source"])


# ─── Warehouse ────────────────────────────────────────────────────────────────

def warehouse_storage(country: str = "DNK") -> DataPoint:
    _load()
    d = _warehouse[country]["storage"]["usd_per_sqm_month"]
    return _dp(d["avg"], d["min"], d["max"], d["unit"], _warehouse[country]["source"])


def warehouse_handling(country: str = "DNK") -> tuple[DataPoint, DataPoint]:
    """Returns (inbound_dp, outbound_dp)."""
    _load()
    h = _warehouse[country]["handling"]
    src = _warehouse[country]["source"]
    inb = _dp(h["inbound_usd_per_unit"]["avg"], h["inbound_usd_per_unit"]["min"], h["inbound_usd_per_unit"]["max"], h["inbound_usd_per_unit"]["unit"], src)
    out = _dp(h["outbound_usd_per_unit"]["avg"], h["outbound_usd_per_unit"]["min"], h["outbound_usd_per_unit"]["max"], h["outbound_usd_per_unit"]["unit"], src)
    return inb, out


def warehouse_avg_months(country: str = "DNK") -> float:
    _load()
    return _warehouse[country]["avg_storage_months"]


# ─── Last mile (country-aware B2B / B2C benchmarks) ──────────────────────────

def last_mile_b2b(country: str = "DNK") -> DataPoint:
    """Road pallet delivery — benchmark, country-aware with DNK fallback."""
    _load()
    try:
        d = _benchmark["last_mile_b2b"][country]
        return DataPoint(value=d["avg"], unit=d["unit"], source=d["source"],
                         timestamp=_now(), confidence="benchmark",
                         error_low=d["min"], error_high=d["max"])
    except KeyError:
        d = _benchmark["last_mile_b2b"]["DNK"]
        return DataPoint(value=d["avg"], unit=d["unit"],
                         source=d["source"] + " (DNK proxy)",
                         timestamp=_now(), confidence="benchmark",
                         error_low=d["min"], error_high=d["max"])


def last_mile_b2c(country: str = "DNK") -> DataPoint:
    """Parcel delivery — benchmark, country-aware with DNK fallback."""
    _load()
    try:
        d = _benchmark["last_mile_b2c"][country]
        return DataPoint(value=d["avg"], unit=d["unit"], source=d["source"],
                         timestamp=_now(), confidence="benchmark",
                         error_low=d["min"], error_high=d["max"])
    except KeyError:
        d = _benchmark["last_mile_b2c"]["DNK"]
        return DataPoint(value=d["avg"], unit=d["unit"],
                         source=d["source"] + " (DNK proxy)",
                         timestamp=_now(), confidence="benchmark",
                         error_low=d["min"], error_high=d["max"])


# ─── Country lookup ──────────────────────────────────────────────────────────

def get_country(iso2: str) -> dict | None:
    _load()
    for c in _countries:
        if c["iso2"] == iso2:
            return c
    return None
