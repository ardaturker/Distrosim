"""
Per-step cost and lead time calculator for China → Denmark routes.
Calls API clients (live or cached/benchmark fallback).
Returns StepResult objects with DataPoint provenance.
"""
from __future__ import annotations
import math
from dataclasses import dataclass

from api import benchmark as bm
from api.wto import get_mfn_duty, get_vat_rate_dk
from api.currency import usd_to_eur

# 1 TEU = 33.2 CBM (standard 20ft container)
TEU_CBM = 33.2
# 1 40ft container = 67.7 CBM
FEU_CBM = 67.7
# Volumetric weight divisor for air (IATA standard)
AIR_VOL_DIVISOR = 6000  # cm³ per kg


@dataclass
class StepResult:
    step_id: str
    step_name: str
    mode: str
    cost_per_unit_usd: float
    cost_total_usd: float
    lead_time_days: float
    source: str
    confidence: str         # "live" | "cached" | "benchmark"
    error_low_usd: float    # lower bound per unit (90% CI)
    error_high_usd: float   # upper bound per unit (90% CI)
    notes: str = ""

    def to_dict(self) -> dict:
        return self.__dict__


class StepCalculator:
    """
    Calculates cost/time for each step in a route.

    All costs are computed per unit in USD.
    Formula notes are in each method.
    """

    def __init__(
        self,
        hs_code: str,
        production_cost_usd: float,
        product_value_usd: float,
        weight_kg: float,
        length_cm: float,
        width_cm: float,
        height_cm: float,
        annual_volume: int,
        units_per_pallet: int = 50,
        units_per_parcel: int = 1,
    ):
        self.hs_code = hs_code
        self.production_cost = production_cost_usd
        self.product_value = product_value_usd
        self.weight_kg = weight_kg
        self.length_cm = length_cm
        self.width_cm = width_cm
        self.height_cm = height_cm
        self.annual_volume = annual_volume
        self.units_per_pallet = units_per_pallet
        self.units_per_parcel = units_per_parcel
        self.tariff_surcharge_pct: float = 0.0  # set after init for tariff scenario
        self.destination: dict = {}              # set after init with destinations.json entry
        self.lane: str = "CHN-DNK"              # set after init — benchmark lane key
        self.inland_country: str = "DNK"         # set after init — dest inland/warehouse country key

        # Derived
        self.cbm_per_unit = (length_cm * width_cm * height_cm) / 1_000_000
        self.total_cbm = self.cbm_per_unit * annual_volume
        self.total_weight_kg = weight_kg * annual_volume
        self.volumetric_weight_kg = (length_cm * width_cm * height_cm) / AIR_VOL_DIVISOR
        self.chargeable_weight_kg = max(weight_kg, self.volumetric_weight_kg)

        # Number of 40ft containers needed (annual shipment)
        self.num_feu = math.ceil(self.total_cbm / FEU_CBM)

    async def calculate(self, step_id: str, step_name: str, mode: str) -> StepResult:
        """Dispatch to the correct calculation method."""
        dispatch = {
            "ex_works":       self._ex_works,
            "origin_inland":  self._origin_inland,
            "export_customs": self._export_customs,
            "thc_origin":     self._thc_origin,
            "intl_freight":   self._intl_freight,
            "insurance":      self._insurance,
            "thc_dest":       self._thc_dest,
            "import_customs": self._import_customs,
            "dest_inland":    self._dest_inland,
            "warehousing":    self._warehousing,
            "last_mile":      self._last_mile,
        }
        fn = dispatch.get(step_id)
        if fn is None:
            return StepResult(step_id, step_name, mode, 0.0, 0.0, 0.0, "unknown", "benchmark", 0.0, 0.0)
        return await fn(step_id, step_name, mode)

    # ── Step methods ──────────────────────────────────────────────────────────

    async def _ex_works(self, step_id, step_name, mode) -> StepResult:
        """Baseline = production cost per unit. No additional cost."""
        cost = self.production_cost
        return StepResult(
            step_id=step_id, step_name=step_name, mode=mode,
            cost_per_unit_usd=cost, cost_total_usd=cost * self.annual_volume,
            lead_time_days=0.0,
            source="User input — known production cost",
            confidence="live",
            error_low_usd=cost, error_high_usd=cost,
            notes="Factory gate cost. All subsequent steps are additive.",
        )

    async def _origin_inland(self, step_id, step_name, mode) -> StepResult:
        """Truck from factory to Shanghai port or Pudong airport."""
        if mode == "road_to_airport":
            dp = bm.origin_inland_air_kg()
            cost_total = dp.value * self.total_weight_kg
            low_total = dp.error_low * self.total_weight_kg
            high_total = dp.error_high * self.total_weight_kg
            days = bm.origin_inland_days().value
        else:
            # Road to port: cost per container, split by annual volume
            dp = bm.origin_inland_road("regional_50_200km")
            cost_total = dp.value * self.num_feu
            low_total = dp.error_low * self.num_feu
            high_total = dp.error_high * self.num_feu
            days = bm.origin_inland_days().value

        return StepResult(
            step_id=step_id, step_name=step_name, mode=mode,
            cost_per_unit_usd=cost_total / self.annual_volume,
            cost_total_usd=cost_total,
            lead_time_days=days,
            source=dp.source, confidence=dp.confidence,
            error_low_usd=low_total / self.annual_volume,
            error_high_usd=high_total / self.annual_volume,
            notes="Factory → Shanghai port/airport. Assumes regional distance 50-200 km.",
        )

    async def _export_customs(self, step_id, step_name, mode) -> StepResult:
        """Chinese customs export broker fee (flat per shipment)."""
        dp = bm.customs_export_broker()
        # Amortize per unit across annual volume
        return StepResult(
            step_id=step_id, step_name=step_name, mode=mode,
            cost_per_unit_usd=dp.value / self.annual_volume,
            cost_total_usd=dp.value,
            lead_time_days=1.0,
            source=dp.source, confidence=dp.confidence,
            error_low_usd=dp.error_low / self.annual_volume,
            error_high_usd=dp.error_high / self.annual_volume,
            notes="One-time export broker fee per shipment. Amortized over annual volume.",
        )

    async def _thc_origin(self, step_id, step_name, mode) -> StepResult:
        """Terminal Handling Charge at Shanghai port."""
        dp = bm.thc_origin()
        cost_total = dp.value * self.num_feu
        return StepResult(
            step_id=step_id, step_name=step_name, mode=mode,
            cost_per_unit_usd=cost_total / self.annual_volume,
            cost_total_usd=cost_total,
            lead_time_days=1.0,
            source=dp.source, confidence=dp.confidence,
            error_low_usd=(dp.error_low * self.num_feu) / self.annual_volume,
            error_high_usd=(dp.error_high * self.num_feu) / self.annual_volume,
            notes=f"THC at Shanghai for {self.num_feu} × 40ft container(s).",
        )

    async def _intl_freight(self, step_id, step_name, mode) -> StepResult:
        """International freight: ocean FCL, LCL, or air."""
        lane = self.lane
        dest_city = self.destination.get("city_name", "destination")
        hub = self.destination.get("hub_port_name", "hub port")

        if mode == "ocean_fcl":
            try:
                dp_rate = bm.ocean_fcl_rate(lane, "40ft")
                dp_transit = bm.ocean_fcl_transit(lane)
            except (KeyError, TypeError):
                dp_rate = bm.ocean_fcl_rate("CHN-DNK", "40ft")
                dp_transit = bm.ocean_fcl_transit("CHN-DNK")
            cost_total = dp_rate.value * self.num_feu
            low_total = dp_rate.error_low * self.num_feu
            high_total = dp_rate.error_high * self.num_feu
            days = dp_transit.value
            notes = f"{self.num_feu} × 40ft FCL, Shanghai → {hub} → {dest_city}, ~{int(days)} days transit."

        elif mode == "ocean_lcl":
            try:
                dp_rate = bm.ocean_lcl_rate(lane)
                dp_surcharge = bm.ocean_lcl_surcharge(lane)
                dp_transit = bm.ocean_lcl_transit(lane)
            except (KeyError, TypeError):
                dp_rate = bm.ocean_lcl_rate("CHN-DNK")
                dp_surcharge = bm.ocean_lcl_surcharge("CHN-DNK")
                dp_transit = bm.ocean_lcl_transit("CHN-DNK")
            # LCL: CBM-based + flat surcharge
            freight_total = dp_rate.value * self.total_cbm
            surcharge = dp_surcharge.value
            cost_total = freight_total + surcharge
            low_total = dp_rate.error_low * self.total_cbm + dp_surcharge.error_low
            high_total = dp_rate.error_high * self.total_cbm + dp_surcharge.error_high
            days = dp_transit.value
            notes = f"{self.total_cbm:.2f} CBM @ ${dp_rate.value}/CBM + surcharges. ~{int(days)} days."
            dp_rate = dp_rate  # keep reference for source

        elif mode == "air":
            try:
                dp_rate = bm.air_rate(lane)
                dp_min = bm.air_min_charge(lane)
                dp_transit = bm.air_transit(lane)
            except (KeyError, TypeError):
                dp_rate = bm.air_rate("CHN-DNK")
                dp_min = bm.air_min_charge("CHN-DNK")
                dp_transit = bm.air_transit("CHN-DNK")
            freight_total = max(
                self.chargeable_weight_kg * self.annual_volume * dp_rate.value,
                dp_min.value,
            )
            cost_total = freight_total
            low_total = max(self.chargeable_weight_kg * self.annual_volume * dp_rate.error_low, dp_min.error_low)
            high_total = self.chargeable_weight_kg * self.annual_volume * dp_rate.error_high
            days = dp_transit.value
            notes = f"Chargeable weight {self.chargeable_weight_kg:.2f} kg/unit × {self.annual_volume} units @ ${dp_rate.value}/kg. ~{int(days)} days."

        else:
            return StepResult(step_id, step_name, mode, 0, 0, 0, "unknown", "benchmark", 0, 0)

        return StepResult(
            step_id=step_id, step_name=step_name, mode=mode,
            cost_per_unit_usd=cost_total / self.annual_volume,
            cost_total_usd=cost_total,
            lead_time_days=days,
            source=dp_rate.source, confidence=dp_rate.confidence,
            error_low_usd=low_total / self.annual_volume,
            error_high_usd=high_total / self.annual_volume,
            notes=notes,
        )

    async def _insurance(self, step_id, step_name, mode) -> StepResult:
        """Cargo insurance = % of CIF value (product value + est. freight)."""
        dp = bm.insurance_rate()
        # CIF value = product value × annual volume (simplification)
        cif_total = self.product_value * self.annual_volume
        cost_total = cif_total * (dp.value / 100)
        return StepResult(
            step_id=step_id, step_name=step_name, mode=mode,
            cost_per_unit_usd=cost_total / self.annual_volume,
            cost_total_usd=cost_total,
            lead_time_days=0.0,
            source=dp.source, confidence=dp.confidence,
            error_low_usd=(cif_total * (dp.error_low / 100)) / self.annual_volume,
            error_high_usd=(cif_total * (dp.error_high / 100)) / self.annual_volume,
            notes=f"Marine cargo insurance at {dp.value}% of CIF value (${cif_total:,.0f}).",
        )

    async def _thc_dest(self, step_id, step_name, mode) -> StepResult:
        """Terminal Handling Charge at destination port."""
        thc_key = f"{self.inland_country}_destination"
        try:
            dp = bm.thc_destination(country=thc_key)
        except (KeyError, TypeError):
            dp = bm.thc_destination("DNK_destination")
        cost_total = dp.value * self.num_feu
        return StepResult(
            step_id=step_id, step_name=step_name, mode=mode,
            cost_per_unit_usd=cost_total / self.annual_volume,
            cost_total_usd=cost_total,
            lead_time_days=1.0,
            source=dp.source, confidence=dp.confidence,
            error_low_usd=(dp.error_low * self.num_feu) / self.annual_volume,
            error_high_usd=(dp.error_high * self.num_feu) / self.annual_volume,
            notes=f"THC at {self.destination.get('hub_port_name', 'destination port')} for {self.num_feu} × 40ft container(s).",
        )

    async def _import_customs(self, step_id, step_name, mode) -> StepResult:
        """
        Import duty (WTO MFN rate × product value) + VAT + broker fee.
        VAT rate taken from destination config; duty from WTO API with benchmark fallback.
        """
        duty_dp = await get_mfn_duty(self.hs_code)
        # Use destination-specific VAT rate if available, otherwise fall back to DK
        dest_vat = self.destination.get("vat_rate")
        if dest_vat is not None:
            from api.benchmark import DataPoint as _DP
            vat_dp = _DP(value=dest_vat, unit="%",
                         source=f"{self.destination.get('name','Destination')} standard VAT rate",
                         timestamp="static", confidence="benchmark",
                         error_low=dest_vat, error_high=dest_vat)
        else:
            vat_dp = await get_vat_rate_dk()
        try:
            broker_dp = bm.customs_import_broker(country=self.inland_country)
            days_dp = bm.customs_import_days(country=self.inland_country)
        except (KeyError, TypeError):
            broker_dp = bm.customs_import_broker("DNK")
            days_dp = bm.customs_import_days("DNK")

        # Duty per unit (MFN + optional tariff scenario surcharge)
        effective_duty_pct = duty_dp.value + self.tariff_surcharge_pct
        duty_per_unit = self.product_value * (effective_duty_pct / 100)
        # VAT base = (product_value + duty + est. CIF freight share)
        # Simplified: VAT on (product_value + duty)
        vat_base_per_unit = self.product_value + duty_per_unit
        vat_per_unit = vat_base_per_unit * (vat_dp.value / 100)
        # Broker fee amortized
        broker_per_unit = broker_dp.value / self.annual_volume

        total_per_unit = duty_per_unit + vat_per_unit + broker_per_unit
        total = total_per_unit * self.annual_volume

        # Error bounds
        duty_low = self.product_value * ((duty_dp.error_low + self.tariff_surcharge_pct) / 100)
        duty_high = self.product_value * ((duty_dp.error_high + self.tariff_surcharge_pct) / 100)
        vat_low = (self.product_value + duty_low) * (vat_dp.value / 100)
        vat_high = (self.product_value + duty_high) * (vat_dp.value / 100)
        broker_low = broker_dp.error_low / self.annual_volume
        broker_high = broker_dp.error_high / self.annual_volume
        error_low = duty_low + vat_low + broker_low
        error_high = duty_high + vat_high + broker_high

        source = f"{duty_dp.source}; VAT: {vat_dp.source}"
        confidence = "live" if duty_dp.confidence == "live" else "benchmark"

        return StepResult(
            step_id=step_id, step_name=step_name, mode=mode,
            cost_per_unit_usd=round(total_per_unit, 4),
            cost_total_usd=round(total, 2),
            lead_time_days=days_dp.value,
            source=source, confidence=confidence,
            error_low_usd=round(error_low, 4),
            error_high_usd=round(error_high, 4),
            notes=(
                f"Duty: {duty_dp.value}% MFN"
                + (f" + {self.tariff_surcharge_pct}% surcharge" if self.tariff_surcharge_pct else "")
                + f" → ${duty_per_unit:.2f}/unit | "
                f"VAT: {vat_dp.value}% → ${vat_per_unit:.2f}/unit | "
                f"Broker: ${broker_dp.value:.0f}/shipment"
            ),
        )

    async def _dest_inland(self, step_id, step_name, mode) -> StepResult:
        """Truck from destination port/airport to destination warehouse."""
        try:
            dp = bm.dest_inland_road("regional_50_200km", country=self.inland_country)
            dp_days = bm.dest_inland_days(country=self.inland_country)
        except (KeyError, TypeError):
            dp = bm.dest_inland_road("regional_50_200km", "DNK")
            dp_days = bm.dest_inland_days("DNK")
        cost_total = dp.value * self.num_feu
        return StepResult(
            step_id=step_id, step_name=step_name, mode=mode,
            cost_per_unit_usd=cost_total / self.annual_volume,
            cost_total_usd=cost_total,
            lead_time_days=dp_days.value,
            source=dp.source, confidence=dp.confidence,
            error_low_usd=(dp.error_low * self.num_feu) / self.annual_volume,
            error_high_usd=(dp.error_high * self.num_feu) / self.annual_volume,
            notes=f"Port/airport → {self.destination.get('name', 'destination')} warehouse. Regional distance.",
        )

    async def _warehousing(self, step_id, step_name, mode) -> StepResult:
        """
        Warehousing in Denmark.
        Storage = sqm × months × rate/sqm/month.
        Assumes 1 pallet = 1.6 sqm, units_per_pallet stacked.
        """
        try:
            dp_storage = bm.warehouse_storage(self.inland_country)
            inb_dp, out_dp = bm.warehouse_handling(self.inland_country)
            avg_months = bm.warehouse_avg_months(self.inland_country)
        except (KeyError, TypeError):
            dp_storage = bm.warehouse_storage("DNK")
            inb_dp, out_dp = bm.warehouse_handling("DNK")
            avg_months = bm.warehouse_avg_months("DNK")

        sqm_per_unit = 1.6 / self.units_per_pallet
        storage_per_unit = sqm_per_unit * avg_months * dp_storage.value
        handling_per_unit = inb_dp.value + out_dp.value
        total_per_unit = storage_per_unit + handling_per_unit

        storage_low = sqm_per_unit * avg_months * dp_storage.error_low
        storage_high = sqm_per_unit * avg_months * dp_storage.error_high
        error_low = storage_low + inb_dp.error_low + out_dp.error_low
        error_high = storage_high + inb_dp.error_high + out_dp.error_high

        return StepResult(
            step_id=step_id, step_name=step_name, mode=mode,
            cost_per_unit_usd=round(total_per_unit, 4),
            cost_total_usd=round(total_per_unit * self.annual_volume, 2),
            lead_time_days=avg_months * 30.0,  # storage duration in days
            source=dp_storage.source, confidence=dp_storage.confidence,
            error_low_usd=round(error_low, 4),
            error_high_usd=round(error_high, 4),
            notes=(
                f"Storage: ${dp_storage.value}/sqm/month × {sqm_per_unit:.3f} sqm/unit × {avg_months} months | "
                f"Handling in+out: ${handling_per_unit:.2f}/unit"
            ),
        )

    async def _last_mile(self, step_id, step_name, mode) -> StepResult:
        """Last-mile delivery in Denmark — B2B pallet or B2C parcel."""
        country = self.inland_country
        dest_name = self.destination.get("city_name", country)
        if mode == "b2b":
            dp = bm.last_mile_b2b(country=country)
            cost_per_unit = dp.value / self.units_per_pallet
            low_per_unit = dp.error_low / self.units_per_pallet
            high_per_unit = dp.error_high / self.units_per_pallet
            days = 2.0
            notes = f"Pallet road delivery in {dest_name}. ${dp.value}/pallet ÷ {self.units_per_pallet} units/pallet."
        else:  # b2c
            dp = bm.last_mile_b2c(country=country)
            cost_per_unit = dp.value / self.units_per_parcel
            low_per_unit = dp.error_low / self.units_per_parcel
            high_per_unit = dp.error_high / self.units_per_parcel
            days = 2.0
            notes = f"Parcel delivery in {dest_name}. ${dp.value}/parcel."

        return StepResult(
            step_id=step_id, step_name=step_name, mode=mode,
            cost_per_unit_usd=round(cost_per_unit, 4),
            cost_total_usd=round(cost_per_unit * self.annual_volume, 2),
            lead_time_days=days,
            source=dp.source, confidence=dp.confidence,
            error_low_usd=round(low_per_unit, 4),
            error_high_usd=round(high_per_unit, 4),
            notes=notes,
        )
