import pandas as pd
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from src.recommender import get_charter_advisory

app = FastAPI(title="SIH26006 Freight Forecasting API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model artifacts
try:
    artifacts = joblib.load('models/freight_forecaster.joblib')
except Exception as e:
    print(f"Warning: Could not load model artifacts. {e}")
    artifacts = {}

class MarketFeatures(BaseModel):
    BDI_Price: float
    Capesize_Price: float
    Brent_Close: float
    Brent_High: float
    Brent_Low: float
    Brent_Open: float
    Brent_Volume: float
    DXY_Close: float
    DXY_High: float
    DXY_Low: float
    DXY_Open: float
    DXY_Volume: float
    Capesize_lag_1d: float
    Capesize_lag_3d: float
    Capesize_lag_7d: float
    Capesize_lag_14d: float
    Capesize_lag_30d: float
    Capesize_sma_7d: float
    Capesize_std_7d: float
    BDI_sma_7d: float
    BDI_std_7d: float
    Capesize_sma_30d: float
    Capesize_std_30d: float
    BDI_sma_30d: float
    BDI_std_30d: float
    Capesize_to_Brent_ratio: float
    Month: int
    Quarter: int
    DayOfWeek: int

@app.get("/api/rates/historical")
def get_historical_rates():
    """Returns the last 90 trading days of historical data."""
    try:
        df = pd.read_csv('data/featured_freight_data.csv')
        df = df.tail(90).fillna(0) # Handle any NaNs for JSON serialization
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rates/forecast")
def get_forecast(features: MarketFeatures):
    """
    Ingests latest market values, runs inference via freight_forecaster.joblib, 
    and returns 7-, 14-, and 30-day forecast values.
    """
    if not artifacts:
        raise HTTPException(status_code=500, detail="Models not loaded")
        
    feature_dict = features.model_dump()
    forecasts = {}
    
    for horizon in ['7-Day', '14-Day', '30-Day']:
        if horizon not in artifacts:
            continue
            
        model = artifacts[horizon]['model']
        scaler = artifacts[horizon]['scaler']
        feature_cols = artifacts[horizon]['features']
        
        # Prepare feature vector in the exact order the model expects
        try:
            x_raw = np.array([[feature_dict[col] for col in feature_cols]])
            x_scaled = scaler.transform(x_raw)
            pred = model.predict(x_scaled)[0]
            forecasts[horizon] = float(pred)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Inference error on {horizon}: {str(e)}")
            
    return {"forecasts": forecasts}

class AdvisoryRequest(BaseModel):
    current_spot: float
    predicted_14d: float

@app.post("/api/advisory")
def get_advisory(req: AdvisoryRequest):
    """
    Returns the chartering recommendation badge, confidence score, and projected cost savings.
    """
    advisory = get_charter_advisory(req.current_spot, req.predicted_14d)
    return advisory

# --- NEW: Logistics & Route Economics ---
from src.logistics_engine import ROUTES, calculate_voyage_economics, chartering_strategy_optimizer, FLEET_SIMULATION_DATA, split_cargo_optimizer

@app.get("/api/logistics/routes")
def get_routes():
    """Returns metadata for all supported origin routes."""
    return {"routes": ROUTES}

class VoyageCalculatorRequest(BaseModel):
    route_id: str
    custom_spot_rate: float
    forecasted_30d_rate: float
    brent_crude_usd: float
    brent_shock_pct: float = 0.0
    congestion_days: float = 0.0

@app.post("/api/logistics/voyage-calculator")
def calculate_voyage(req: VoyageCalculatorRequest):
    """
    Ingests route parameters, custom spot rates, Brent shock percentages, and congestion delays.
    Outputs the calculated economics and procurement strategy.
    """
    try:
        strategy = chartering_strategy_optimizer(
            route_id=req.route_id,
            spot_rate=req.custom_spot_rate,
            forecasted_30d_rate=req.forecasted_30d_rate,
            brent_crude_usd=req.brent_crude_usd,
            brent_shock_pct=req.brent_shock_pct,
            congestion_days=req.congestion_days
        )
        return strategy
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/logistics/fleet-simulation")
def get_fleet_simulation():
    """Returns active simulated vessel coordinates, route polylines, and port coordinates."""
    return FLEET_SIMULATION_DATA

@app.post("/api/logistics/split-cargo-eval")
def eval_split_cargo(req: VoyageCalculatorRequest):
    """
    Computes and compares Capesize vs. 2x Panamax economics for the selected route.
    """
    try:
        eval_result = split_cargo_optimizer(
            route_id=req.route_id,
            capesize_day_rate=req.custom_spot_rate,
            brent_crude_usd=req.brent_crude_usd,
            brent_shock_pct=req.brent_shock_pct,
            congestion_days=req.congestion_days
        )
        return eval_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
