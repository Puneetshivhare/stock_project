"""
Prediction API routes — forecast per commodity, all commodities.
"""

from fastapi import APIRouter, Query, HTTPException

from backend.config import MARKETS, DEFAULT_MARKET, FORECAST_HORIZONS
from backend.ml.forecaster import forecast_commodity, forecast_all_commodities

router = APIRouter(prefix="/api/predict", tags=["Predictions"])


@router.get("/{commodity}")
async def predict_commodity(
    commodity: str,
    market: str = Query(DEFAULT_MARKET),
    horizon: int = Query(7, description="Forecast horizon in days (1, 7, or 30)"),
):
    """Get price forecast for a specific commodity."""
    if market not in MARKETS:
        raise HTTPException(status_code=400, detail=f"Invalid market: {market}")
    if commodity not in ["gold", "silver", "copper"]:
        raise HTTPException(status_code=400, detail=f"Invalid commodity: {commodity}")
    if horizon not in FORECAST_HORIZONS:
        raise HTTPException(status_code=400, detail=f"Invalid horizon: {horizon}. Use {FORECAST_HORIZONS}")

    try:
        result = forecast_commodity(market, commodity, horizon)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")


@router.get("/all/forecasts")
async def predict_all(
    market: str = Query(DEFAULT_MARKET),
    horizon: int = Query(7),
):
    """Get forecasts for all commodities in a market."""
    if market not in MARKETS:
        raise HTTPException(status_code=400, detail=f"Invalid market: {market}")

    results = forecast_all_commodities(market, horizon)
    return {
        "market": market,
        "horizon": horizon,
        "forecasts": results,
    }
