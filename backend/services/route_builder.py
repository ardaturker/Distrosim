"""
Route permutation engine for China (Shanghai) → destination.
Generates all valid distribution route definitions.
Each route is a sequence of step IDs with selected modes.
"""
from dataclasses import dataclass, field


@dataclass
class StepDef:
    step_id: str
    name: str
    mode: str           # specific mode for this step
    required: bool = True
    notes: str = ""


@dataclass
class RouteDef:
    route_id: str
    route_name: str
    freight_mode: str       # "ocean_fcl" | "ocean_lcl" | "air"
    last_mile_type: str     # "b2b" | "b2c"
    steps: list[StepDef] = field(default_factory=list)
    description: str = ""


def build_routes(
    freight_mode_pref: str = "all",
    last_mile_pref: str = "both",
    destination: dict | None = None,
) -> list[RouteDef]:
    """
    Generate valid China→destination distribution routes.

    freight_mode_pref: "all" | "ocean" | "air"
    last_mile_pref: "both" | "b2b" | "b2c"
    destination: destinations.json entry dict for dynamic step labels

    Returns list of RouteDef objects (6-8 routes for "all"/"both").
    """
    dest = destination or {}
    routes: list[RouteDef] = []

    freight_modes = _resolve_freight_modes(freight_mode_pref)
    last_mile_types = _resolve_last_mile(last_mile_pref)

    for fm in freight_modes:
        for lm in last_mile_types:
            route = _make_route(fm, lm, dest)
            if route:
                routes.append(route)

    return routes


def _resolve_freight_modes(pref: str) -> list[str]:
    if pref == "ocean":
        return ["ocean_fcl", "ocean_lcl"]
    if pref == "air":
        return ["air"]
    return ["ocean_fcl", "ocean_lcl", "air"]


def _resolve_last_mile(pref: str) -> list[str]:
    if pref == "b2b":
        return ["b2b"]
    if pref == "b2c":
        return ["b2c"]
    return ["b2b", "b2c"]


def _make_route(freight_mode: str, last_mile: str, dest: dict) -> RouteDef | None:
    lm_label = "B2B Pallet" if last_mile == "b2b" else "B2C Parcel"

    city       = dest.get("city_name", "Destination")
    hub        = dest.get("hub_port_name", "Hub Port")
    air_code   = dest.get("air_airport_code", "Dest Airport")
    country    = dest.get("country", "EU")
    duty_label = dest.get("duty_regime", "Import Customs & Duties")

    if freight_mode == "ocean_fcl":
        route_name = f"Ocean FCL + {lm_label}"
        route_id = f"ocean_fcl_{last_mile}"
        description = f"Full Container Load via Shanghai → {hub} → {city}. Best for volumes > 5 CBM."
        steps = [
            StepDef("ex_works",       "Ex-Works (Factory)",                     "factory"),
            StepDef("origin_inland",  "Origin Inland Transport",                 "road_to_port"),
            StepDef("export_customs", "Export Customs & Docs",                   "standard"),
            StepDef("thc_origin",     "Origin Port Handling (THC)",              "shanghai_port"),
            StepDef("intl_freight",   "Ocean Freight — FCL 40ft",                "ocean_fcl"),
            StepDef("insurance",      "Freight Insurance",                       "standard"),
            StepDef("thc_dest",       f"Destination Port Handling ({hub})",      dest.get("port_code", "dest_port")),
            StepDef("import_customs", duty_label,                                "standard"),
            StepDef("dest_inland",    "Destination Inland Transport",            "road_from_port"),
            StepDef("warehousing",    f"Warehousing ({country})",                "standard"),
            StepDef("last_mile",      f"Last-Mile Delivery ({lm_label})",        last_mile),
        ]

    elif freight_mode == "ocean_lcl":
        route_name = f"Ocean LCL + {lm_label}"
        route_id = f"ocean_lcl_{last_mile}"
        description = f"Less-than-Container Load via Shanghai → {hub} → {city}. Best for volumes 0.5–5 CBM."
        steps = [
            StepDef("ex_works",       "Ex-Works (Factory)",                     "factory"),
            StepDef("origin_inland",  "Origin Inland Transport",                 "road_to_port"),
            StepDef("export_customs", "Export Customs & Docs",                   "standard"),
            StepDef("thc_origin",     "Origin Port Handling (THC)",              "shanghai_port"),
            StepDef("intl_freight",   "Ocean Freight — LCL",                     "ocean_lcl"),
            StepDef("insurance",      "Freight Insurance",                       "standard"),
            StepDef("thc_dest",       f"Destination Port Handling ({hub})",      dest.get("port_code", "dest_port")),
            StepDef("import_customs", duty_label,                                "standard"),
            StepDef("dest_inland",    "Destination Inland Transport",            "road_from_port"),
            StepDef("warehousing",    f"Warehousing ({country})",                "standard"),
            StepDef("last_mile",      f"Last-Mile Delivery ({lm_label})",        last_mile),
        ]

    elif freight_mode == "air":
        route_name = f"Air Freight + {lm_label}"
        route_id = f"air_{last_mile}"
        description = f"Air freight Shanghai Pudong → {air_code}. Fastest option, highest per-unit cost."
        steps = [
            StepDef("ex_works",       "Ex-Works (Factory)",                     "factory"),
            StepDef("origin_inland",  "Origin Inland Transport",                 "road_to_airport"),
            StepDef("export_customs", "Export Customs & Docs",                   "standard"),
            StepDef("intl_freight",   f"Air Freight — PVG → {air_code}",         "air"),
            StepDef("insurance",      "Freight Insurance",                       "standard"),
            StepDef("import_customs", duty_label,                                "standard"),
            StepDef("dest_inland",    "Destination Inland Transport",            "road_from_airport"),
            StepDef("warehousing",    f"Warehousing ({country})",                "standard"),
            StepDef("last_mile",      f"Last-Mile Delivery ({lm_label})",        last_mile),
        ]

    else:
        return None

    return RouteDef(
        route_id=route_id,
        route_name=route_name,
        freight_mode=freight_mode,
        last_mile_type=last_mile,
        steps=steps,
        description=description,
    )
