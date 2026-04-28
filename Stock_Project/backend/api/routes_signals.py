"""
Signals API routes — buy/sell/hold per commodity, all commodities.
"""

from fastapi import APIRouter, Query, HTTPException

from backend.config import MARKETS, DEFAULT_MARKET
from backend.ml.signals import generate_signal, generate_all_signals

router = APIRouter(prefix="/api/signals", tags=["Signals"])


@router.get("/all")
async def all_signals(
    market: str = Query(DEFAULT_MARKET),
    horizon: int = Query(7),
):
    """Get buy/sell/hold signals for all commodities."""
    if market not in MARKETS:
        raise HTTPException(status_code=400, detail=f"Invalid market: {market}")

    results = generate_all_signals(market, horizon)
    return {
        "market": market,
        "signals": results,
    }


@router.get("/{commodity}")
async def commodity_signal(
    commodity: str,
    market: str = Query(DEFAULT_MARKET),
    horizon: int = Query(7),
):
    """Get buy/sell/hold signal for a specific commodity."""
    if market not in MARKETS:
        raise HTTPException(status_code=400, detail=f"Invalid market: {market}")
    if commodity not in ["gold", "silver", "copper"]:
        raise HTTPException(status_code=400, detail=f"Invalid commodity: {commodity}")

    try:
        result = generate_signal(market, commodity, horizon)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signal error: {str(e)}")
