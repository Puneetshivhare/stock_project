"""
FastAPI application entry point — CORS, router registration, APScheduler.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from backend.config import MARKETS
from backend.data.storage import create_tables
from backend.data.yahoo_ingestor import ingest_all_markets
from backend.data.news_scraper import ingest_news_all_markets
from backend.api.routes_data import router as data_router
from backend.api.routes_predict import router as predict_router
from backend.api.routes_signals import router as signals_router
from backend.api.routes_reports import router as reports_router

# ── Logging ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Scheduler ──────────────────────────────────────────────
scheduler = BackgroundScheduler()


def scheduled_refresh():
    """Background job: refresh data for all markets."""
    logger.info("🔄 Scheduled data refresh started...")
    try:
        ingest_all_markets()
        ingest_news_all_markets()
        logger.info("✅ Scheduled refresh complete")
    except Exception as e:
        logger.error(f"Scheduled refresh error: {e}")


# ── App Lifecycle ──────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting Financial Intelligence Pipeline...")

    # Create database tables
    create_tables()
    logger.info("📊 Database tables ready")

    # Initial data load
    logger.info("📥 Running initial data ingestion (this may take 1-2 minutes)...")
    try:
        ingest_all_markets()
        ingest_news_all_markets()
        logger.info("✅ Initial data load complete")
    except Exception as e:
        logger.error(f"Initial ingestion error: {e}")
        logger.info("⚠️ You can trigger manual refresh via POST /api/data/refresh")

    # Start scheduler — refresh every 6 hours
    scheduler.add_job(scheduled_refresh, "interval", hours=6, id="data_refresh")
    scheduler.start()
    logger.info("⏰ Scheduler started — data refreshes every 6 hours")

    yield

    # Shutdown
    scheduler.shutdown()
    logger.info("🛑 Scheduler stopped. Goodbye!")


# ── FastAPI App ────────────────────────────────────────────
app = FastAPI(
    title="Financial Intelligence Pipeline API",
    description=(
        "Multi-market commodity intelligence system for Gold, Silver, and Copper "
        "across India (MCX), US (COMEX), and China (SHFE). "
        "Provides price data, ML forecasts, buy/sell signals, and LLM-powered analysis."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(data_router)
app.include_router(predict_router)
app.include_router(signals_router)
app.include_router(reports_router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Financial Intelligence Pipeline",
        "markets": list(MARKETS.keys()),
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    """Detailed health check."""
    from backend.data.storage import get_latest_prices
    market_status = {}
    for market_key in MARKETS:
        prices = get_latest_prices(market_key)
        market_status[market_key] = {
            "has_data": len(prices) > 0,
            "commodities_with_data": len(prices),
        }
    return {
        "status": "healthy",
        "markets": market_status,
    }
