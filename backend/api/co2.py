"""
CO2 emission calculator for China → Denmark distribution routes.
Uses GLEC Framework v3 / ISO 14083 emission factors.
No API key required — factors are published standards.

Emission factors (gCO2e per tonne-km):
  Ocean container ship: 8   (GLEC Tier 1, laden average)
  Air freight:          500  (GLEC Tier 1, belly + freighter average)
  Road truck (EU):      62   (GLEC Tier 1, 40t articulated, laden)
  Short-sea feeder:     18   (GLEC Tier 1)

Distances (km, approximate great-circle / routing):
  Shanghai (CNSHA) → Rotterdam (NLRTM):  21100 km  (sea)
  PVG → CPH (air):                        8300 km  (air)
  Rotterdam → Aarhus (road):               850 km  (road, used for FCL/LCL)
  CPH airport → Danish warehouse:          100 km  (road, used for air)
  Shanghai factory → Shanghai port (road): 150 km  (origin inland)
"""

from dataclasses import dataclass

# GLEC Tier 1 emission factors (gCO2e / tonne-km)
EF_OCEAN_CONTAINER = 8.0
EF_AIR_FREIGHT = 500.0
EF_ROAD_EU = 62.0
EF_SHORT_SEA = 18.0

# Fixed distances (km)
DIST_SEA_CNSHA_NLRTM = 21_100
DIST_AIR_PVG_CPH = 8_300
DIST_ROAD_NLRTM_AARHUS = 850
DIST_ROAD_CPH_WAREHOUSE = 100
DIST_ROAD_FACTORY_CNSHA_PORT = 150


@dataclass
class CO2Result:
    kg_co2e_per_unit: float       # total CO2e in kg per unit shipped
    breakdown: dict               # step-level breakdown in kg CO2e/unit
    methodology: str              # "GLEC Framework v3 / ISO 14083"


def calculate_co2(
    freight_mode: str,    # "ocean_fcl" | "ocean_lcl" | "air"
    weight_kg: float,     # per unit
    annual_volume: int,   # used for future scaling, not needed per-unit
    destination: dict | None = None,  # destinations.json entry for dynamic distances
) -> CO2Result:
    """
    Calculate kg CO2e per unit for a given freight mode.
    Formula: emissions (kgCO2e) = weight_t × distance_km × ef_gCO2e_per_tkm / 1000
    """
    weight_t = weight_kg / 1000  # kg → tonnes
    dest = destination or {}

    def leg_kg(dist_km: float, ef_g_per_tkm: float) -> float:
        """Return kg CO2e for one transport leg per unit."""
        return weight_t * dist_km * ef_g_per_tkm / 1000

    if freight_mode in ("ocean_fcl", "ocean_lcl"):
        sea_dist  = dest.get("sea_dist_cnsha_to_hub_km", DIST_SEA_CNSHA_NLRTM)
        road_dist = dest.get("road_dist_hub_to_dest_km", DIST_ROAD_NLRTM_AARHUS)
        origin_inland = leg_kg(DIST_ROAD_FACTORY_CNSHA_PORT, EF_ROAD_EU)
        intl_freight  = leg_kg(sea_dist, EF_OCEAN_CONTAINER)
        dest_inland   = leg_kg(road_dist, EF_ROAD_EU)
    else:  # air
        air_dist      = dest.get("air_dist_pvg_km", DIST_AIR_PVG_CPH)
        air_road_dist = dest.get("air_road_dist_km", DIST_ROAD_CPH_WAREHOUSE)
        origin_inland = leg_kg(DIST_ROAD_FACTORY_CNSHA_PORT, EF_ROAD_EU)
        intl_freight  = leg_kg(air_dist, EF_AIR_FREIGHT)
        dest_inland   = leg_kg(air_road_dist, EF_ROAD_EU)

    breakdown = {
        "origin_inland": round(origin_inland, 4),
        "intl_freight":  round(intl_freight, 4),
        "dest_inland":   round(dest_inland, 4),
    }
    total = sum(breakdown.values())

    return CO2Result(
        kg_co2e_per_unit=round(total, 3),
        breakdown=breakdown,
        methodology="GLEC Framework v3 / ISO 14083",
    )
