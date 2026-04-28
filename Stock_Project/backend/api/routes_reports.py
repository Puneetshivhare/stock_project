"""
Reports API routes — LLM-generated market analysis and commodity deep-dives.
"""

from fastapi import APIRouter, Query, HTTPException

from backend.config import MARKETS, DEFAULT_MARKET
from backend.data.storage import get_latest_prices, get_news, get_price_history
from backend.ml.signals import generate_all_signals
from backend.ml.forecaster import forecast_commodity
from backend.llm.analyzer import generate_daily_summary, generate_prediction_explanation, generate_commodity_analysis
from backend.llm.confidence import score_prediction_confidence

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/daily")
async def daily_report(market: str = Query(DEFAULT_MARKET)):
    """Generate an LLM-powered daily market summary."""
    if market not in MARKETS:
        raise HTTPException(status_code=400, detail=f"Invalid market: {market}")

    latest = get_latest_prices(market)
    news = get_news(market, limit=10)

    try:
        signals = generate_all_signals(market, 7)
    except Exception:
        signals = None

    report = generate_daily_summary(market, latest, news, signals)
    return {
        "market": market,
        "report": report,
        "market_name": MARKETS[market]["name"],
    }


@router.get("/analysis/{commodity}")
async def commodity_report(
    commodity: str,
    market: str = Query(DEFAULT_MARKET),
):
    """Generate a deep analysis for a specific commodity."""
    if market not in MARKETS:
        raise HTTPException(status_code=400, detail=f"Invalid market: {market}")
    if commodity not in ["gold", "silver", "copper"]:
        raise HTTPException(status_code=400, detail=f"Invalid commodity: {commodity}")

    # Get latest data
    df = get_price_history(market, commodity, limit=5)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data for {commodity} in {market}")

    price_data = df.iloc[-1].to_dict()
    news = get_news(market, limit=5)

    analysis = generate_commodity_analysis(market, commodity, price_data, news)
    return {
        "market": market,
        "commodity": commodity,
        "analysis": analysis,
    }


@router.get("/prediction-explain/{commodity}")
async def prediction_explanation(
    commodity: str,
    market: str = Query(DEFAULT_MARKET),
    horizon: int = Query(7),
):
    """Get LLM explanation of a forecast."""
    if market not in MARKETS:
        raise HTTPException(status_code=400, detail=f"Invalid market: {market}")

    try:
        forecast = forecast_commodity(market, commodity, horizon)
        explanation = generate_prediction_explanation(market, commodity, forecast)
        return {
            "market": market,
            "commodity": commodity,
            "forecast": forecast,
            "explanation": explanation,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/confidence/{commodity}")
async def prediction_confidence(
    commodity: str,
    market: str = Query(DEFAULT_MARKET),
    horizon: int = Query(7),
):
    """Get LLM confidence score for a prediction."""
    if market not in MARKETS:
        raise HTTPException(status_code=400, detail=f"Invalid market: {market}")

    try:
        forecast = forecast_commodity(market, commodity, horizon)
        df = get_price_history(market, commodity, limit=1)
        latest = df.iloc[-1].to_dict() if not df.empty else {}

        confidence = score_prediction_confidence(market, commodity, forecast, latest)
        return {
            "market": market,
            "commodity": commodity,
            "confidence": confidence,
            "forecast_summary": {
                "direction": forecast.get("direction"),
                "pct_change": forecast.get("pct_change"),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
