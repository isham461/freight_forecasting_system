from pydantic import BaseModel
from typing import Dict, Any

# Standard Bulk Import Routes to ECI
ROUTES = {
    "route_australia": {
        "id": "route_australia",
        "name": "Australia (Port Hedland) to ECI (Paradip)",
        "sailing_days": 15,
        "payload_mt": 160000,
        "cargo_type": "Iron Ore",
        "port_dues": 180000
    },
    "route_south_africa": {
        "id": "route_south_africa",
        "name": "South Africa (Richards Bay) to ECI (Vizag)",
        "sailing_days": 19,
        "payload_mt": 150000,
        "cargo_type": "Coking Coal",
        "port_dues": 180000
    },
    "route_brazil": {
        "id": "route_brazil",
        "name": "Brazil (Tubarao) to ECI (Paradip)",
        "sailing_days": 33,
        "payload_mt": 170000,
        "cargo_type": "High-Grade Iron Ore",
        "port_dues": 180000
    }
}

class VoyageEconomics(BaseModel):
    total_voyage_days: float
    bunker_price_per_mt: float
    total_bunker_expense: float
    charter_hire_expense: float
    total_voyage_cost: float
    landed_freight_cost_per_mt: float

def calculate_voyage_economics(route_id: str, capesize_day_rate: float, brent_crude_usd: float, brent_shock_pct: float = 0, congestion_days: float = 0) -> VoyageEconomics:
    """Computes total voyage costs and landed freight cost per metric ton."""
    route = ROUTES.get(route_id)
    if not route:
        raise ValueError(f"Unknown route_id: {route_id}")
    
    total_voyage_days = route["sailing_days"] + congestion_days
    
    # Capesize vessels burn ~40 MT/day of VLSFO.
    # Bunker price modeled dynamically: Brent * 6.5 * (1 + shock)
    shock_multiplier = 1.0 + (brent_shock_pct / 100.0)
    bunker_price_per_mt = brent_crude_usd * 6.5 * shock_multiplier
    total_bunker_expense = total_voyage_days * 40 * bunker_price_per_mt
    
    charter_hire_expense = total_voyage_days * capesize_day_rate
    port_dues = route["port_dues"]
    
    total_voyage_cost = charter_hire_expense + total_bunker_expense + port_dues
    landed_cost_per_mt = total_voyage_cost / route["payload_mt"]
    
    return VoyageEconomics(
        total_voyage_days=total_voyage_days,
        bunker_price_per_mt=bunker_price_per_mt,
        total_bunker_expense=total_bunker_expense,
        charter_hire_expense=charter_hire_expense,
        total_voyage_cost=total_voyage_cost,
        landed_freight_cost_per_mt=landed_cost_per_mt
    )

def chartering_strategy_optimizer(route_id: str, spot_rate: float, forecasted_30d_rate: float, brent_crude_usd: float, brent_shock_pct: float = 0, congestion_days: float = 0) -> Dict[str, Any]:
    """Compares Spot vs Time Charter Strategy and outputs recommendations."""
    route = ROUTES.get(route_id)
    if not route:
        raise ValueError("Unknown route")
        
    # Economics for immediate spot booking
    spot_econ = calculate_voyage_economics(route_id, spot_rate, brent_crude_usd, brent_shock_pct, congestion_days)
    
    # Economics for 3-Month Time Charter booking (assuming forecasted_30d_rate as proxy for locked rate)
    tc_econ = calculate_voyage_economics(route_id, forecasted_30d_rate, brent_crude_usd, brent_shock_pct, congestion_days)
    
    delta_total_cost = tc_econ.total_voyage_cost - spot_econ.total_voyage_cost
    payload = route["payload_mt"]
    
    # Logic: if spot rate is vastly cheaper than time charter, stick to spot.
    # If time charter proxy (forecasted 30d rate) is vastly cheaper, lock time charter.
    delta_pct = (forecasted_30d_rate - spot_rate) / spot_rate
    
    if delta_pct <= -0.05:
        # Market is dropping, locking in spot now is more expensive than future proxy.
        recommendation = "DELAY SPOT CHARTER"
        exposure = abs(delta_total_cost)
        exposure_desc = f"Wait for market drop. Securing spot now risks an overpayment of ${exposure:,.0f} across {payload:,} MT payload."
    elif delta_pct >= 0.05:
        # Market is surging, locking in time charter proxy now prevents future exposure.
        recommendation = "LOCK 3-MONTH TIME CHARTER"
        exposure = abs(delta_total_cost)
        exposure_desc = f"Market surging. Lock term charter to avoid projected spot exposure of +${exposure:,.0f} across {payload:,} MT payload."
    else:
        recommendation = "SPOT CHARTER NOW"
        exposure = 0
        exposure_desc = f"Market stable. Proceed with single spot voyage. Minimal delta between spot and term rates."
        
    return {
        "spot_economics": spot_econ.model_dump(),
        "tc_economics": tc_econ.model_dump(),
        "delta_total_cost": delta_total_cost,
        "recommendation": recommendation,
        "exposure_desc": exposure_desc
    }

# --- NEW: Fleet Simulation & Split-Cargo ---

FLEET_SIMULATION_DATA = {
    "ports": {
        "Dampier": [-20.3, 118.57],
        "Paradip": [20.26, 86.67],
        "Richards_Bay": [-28.8, 32.0],
        "Visakhapatnam": [17.68, 83.21],
        "Tubarao": [-20.28, -40.24]
    },
    "routes": {
        "route_australia": [ [-20.3, 118.57], [-6.2, 105.4], [5.9, 95.3], [20.26, 86.67] ],
        "route_south_africa": [ [-28.8, 32.0], [-10.0, 55.0], [5.0, 75.0], [17.68, 83.21] ],
        "route_brazil": [ [-20.28, -40.24], [-35.0, 20.0], [-10.0, 55.0], [5.0, 75.0], [20.26, 86.67] ]
    },
    "vessels": [
        {"id": "V001", "name": "Bulk Pioneer", "imo": "IMO9123456", "route": "route_australia", "speed": 13.5, "position": [-6.2, 105.4], "eta": "2026-10-05"},
        {"id": "V002", "name": "Oceanic Ore", "imo": "IMO9988776", "route": "route_south_africa", "speed": 12.0, "position": [-10.0, 55.0], "eta": "2026-10-12"},
        {"id": "V003", "name": "Cape Titan", "imo": "IMO9345678", "route": "route_brazil", "speed": 14.1, "position": [-10.0, 55.0], "eta": "2026-10-25"}
    ]
}

def split_cargo_optimizer(route_id: str, capesize_day_rate: float, brent_crude_usd: float, brent_shock_pct: float = 0, congestion_days: float = 0) -> Dict[str, Any]:
    """Compares 1x Capesize vs 2x Panamax economics."""
    route = ROUTES.get(route_id)
    if not route:
        raise ValueError("Unknown route")
        
    total_voyage_days = route["sailing_days"] + congestion_days
    shock_multiplier = 1.0 + (brent_shock_pct / 100.0)
    bunker_price_per_mt = brent_crude_usd * 6.5 * shock_multiplier
    
    # Baseline: 1x Capesize
    cape_bunker = total_voyage_days * 40 * bunker_price_per_mt
    cape_hire = total_voyage_days * capesize_day_rate
    cape_total = cape_bunker + cape_hire + route["port_dues"]
    cape_landed = cape_total / route["payload_mt"]
    
    # Alternative: 2x Panamax (80,000 MT each)
    panamax_day_rate = 0.65 * capesize_day_rate
    panamax_bunker_per_ship = total_voyage_days * 28 * bunker_price_per_mt
    panamax_hire_per_ship = total_voyage_days * panamax_day_rate
    panamax_total_per_ship = panamax_bunker_per_ship + panamax_hire_per_ship + route["port_dues"] # Assuming same port dues per ship for simplicity
    
    twin_panamax_total = panamax_total_per_ship * 2
    twin_panamax_landed = twin_panamax_total / route["payload_mt"]
    
    savings = cape_landed - twin_panamax_landed
    is_split_cheaper = savings > 0
    
    return {
        "capesize": {
            "total_voyage_days": total_voyage_days,
            "total_bunker_expense": cape_bunker,
            "charter_hire_expense": cape_hire,
            "total_voyage_cost": cape_total,
            "landed_cost_per_mt": cape_landed
        },
        "twin_panamax": {
            "total_voyage_days": total_voyage_days,
            "total_bunker_expense": panamax_bunker_per_ship * 2,
            "charter_hire_expense": panamax_hire_per_ship * 2,
            "total_voyage_cost": twin_panamax_total,
            "landed_cost_per_mt": twin_panamax_landed
        },
        "savings_per_mt": savings,
        "is_split_cheaper": is_split_cheaper
    }
