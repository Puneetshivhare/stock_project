"""
Centralized configuration — Market registry, tickers, and settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DEFAULT_MARKET = os.getenv("DEFAULT_MARKET", "india")

# ── Forecast Horizons ──────────────────────────────────────
FORECAST_HORIZONS = [1, 7, 30]
DATA_HISTORY_PERIOD = "5y"

# ── Market Registry ────────────────────────────────────────
MARKETS = {
    "india": {
        "name": "India (MCX)",
        "flag": "🇮🇳",
        "currency": "INR",
        "symbol": "₹",
        "fx_ticker": "USDINR=X",
        "commodities": {
            "gold": {"ticker": "GC=F", "unit": "per 10g", "multiplier": 0.32151},
            "silver": {"ticker": "SI=F", "unit": "per kg", "multiplier": 32.1507},
            "copper": {"ticker": "HG=F", "unit": "per kg", "multiplier": 2.20462},
        },
        "macro_tickers": {
            "USD/INR": "USDINR=X",
            "Nifty 50": "^NSEI",
            "Crude Oil": "CL=F",
        },
        "news_sources": ["moneycontrol", "economic_times"],
    },
    "us": {
        "name": "US (COMEX)",
        "flag": "🇺🇸",
        "currency": "USD",
        "symbol": "$",
        "fx_ticker": None,  # Base currency — no conversion
        "commodities": {
            "gold": {"ticker": "GC=F", "unit": "per oz", "multiplier": 1.0},
            "silver": {"ticker": "SI=F", "unit": "per oz", "multiplier": 1.0},
            "copper": {"ticker": "HG=F", "unit": "per lb", "multiplier": 1.0},
        },
        "macro_tickers": {
            "DXY": "DX-Y.NYB",
            "US 10Y": "^TNX",
            "S&P 500": "^GSPC",
            "Crude Oil": "CL=F",
        },
        "news_sources": ["reuters", "cnbc"],
    },
    "china": {
        "name": "China (SHFE)",
        "flag": "🇨🇳",
        "currency": "CNY",
        "symbol": "¥",
        "fx_ticker": "USDCNY=X",
        "commodities": {
            "gold": {"ticker": "GC=F", "unit": "per g", "multiplier": 0.03215},
            "silver": {"ticker": "SI=F", "unit": "per kg", "multiplier": 32.1507},
            "copper": {"ticker": "HG=F", "unit": "per ton", "multiplier": 2204.62},
        },
        "macro_tickers": {
            "USD/CNY": "USDCNY=X",
            "Shanghai Comp": "000001.SS",
            "Crude Oil": "CL=F",
        },
        "news_sources": ["sina_finance", "eastmoney"],
    },
}

# ── Commodity Display Names ────────────────────────────────
COMMODITY_NAMES = {
    "gold": "Gold",
    "silver": "Silver",
    "copper": "Copper",
}

COMMODITY_COLORS = {
    "gold": "#FFD700",
    "silver": "#C0C0C0",
    "copper": "#B87333",
}

# ── Database ────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "market_data.db")

# ── Technical Indicator Settings ───────────────────────────
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD = 2
SMA_SHORT = 20
SMA_LONG = 50
