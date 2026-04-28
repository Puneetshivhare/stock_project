"""
Data API routes — prices, latest, refresh, news, markets.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from backend.config import MARKETS, DEFAULT_MARKET
from backend.data.storage import get_price_history, get_latest_prices, get_news
from backend.data.yahoo_ingestor import ingest_market_data
from backend.data.news_scraper import ingest_news_for_market

router = APIRouter(prefix="/api/data", tags=["Data"])


@router.get("/markets")
async def list_markets():
    """List all available markets."""
    return {
        key: {
            "name": cfg["name"],
            "flag": cfg["flag"],
            "currency": cfg["currency"],
            "symbol": cfg["symbol"],
            "commodities": list(cfg["commodities"].keys()),
        }
        for key, cfg in MARKETS.items()
    }


@router.get("/latest")
async def latest_prices(market: str = Query(DEFAULT_MARKET)):
    """Get latest prices for all commodities in a market."""
    if market not in MARKETS:
        raise HTTPException(status_code=400, detail=f"Invalid market: {market}")
    prices = get_latest_prices(market)
    return {
        "market": market,
        "market_name": MARKETS[market]["name"],
        "currency": MARKETS[market]["currency"],
        "symbol": MARKETS[market]["symbol"],
        "prices": prices,
    }


@router.get("/prices/{commodity}")
async def price_history(
    commodity: str,
    market: str = Query(DEFAULT_MARKET),
    limit: int = Query(200, ge=1, le=2000),
):
    """Get historical OHLCV + indicators for a commodity."""
    if market not in MARKETS:
        raise HTTPException(status_code=400, detail=f"Invalid market: {market}")
    if commodity not in ["gold", "silver", "copper"]:
        raise HTTPException(status_code=400, detail=f"Invalid commodity: {commodity}")

    df = get_price_history(market, commodity, limit)
    if df.empty:
        return {"market": market, "commodity": commodity, "data": [], "count": 0}

    records = df.to_dict(orient="records")
    # Convert dates to string for JSON
    for r in records:
        if hasattr(r.get("date"), "strftime"):
            r["date"] = r["date"].strftime("%Y-%m-%d")

    return {
        "market": market,
        "commodity": commodity,
        "currency": MARKETS[market]["currency"],
        "symbol": MARKETS[market]["symbol"],
        "data": records,
        "count": len(records),
    }


@router.post("/refresh")
async def refresh_data(market: str = Query(DEFAULT_MARKET)):
    """Trigger manual data refresh for a market."""
    if market not in MARKETS:
        raise HTTPException(status_code=400, detail=f"Invalid market: {market}")

    try:
        price_summary = ingest_market_data(market)
        news_count = ingest_news_for_market(market)
        return {
            "status": "ok",
            "market": market,
            "prices": price_summary,
            "news_articles": news_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news")
async def get_market_news(
    market: str = Query(DEFAULT_MARKET),
    limit: int = Query(15, ge=1, le=50),
):
    """Get cached news for a market."""
    if market not in MARKETS:
        raise HTTPException(status_code=400, detail=f"Invalid market: {market}")
    articles = get_news(market, limit)
    return {
        "market": market,
        "articles": articles,
        "count": len(articles),
    }
