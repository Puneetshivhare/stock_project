"""
Streamlit API client — HTTP client for calling the FastAPI backend.
"""

import httpx
import streamlit as st
from typing import Dict, Any, List, Optional
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def _get(endpoint: str, params: dict = None) -> Dict[str, Any]:
    """Make a GET request to the backend."""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        resp = httpx.get(url, params=params, timeout=120.0)
        resp.raise_for_status()
        return resp.json()
    except httpx.ConnectError:
        st.error("⚠️ Cannot connect to backend. Is FastAPI running on port 8000?")
        return {}
    except Exception as e:
        st.error(f"API Error: {e}")
        return {}


def _post(endpoint: str, params: dict = None) -> Dict[str, Any]:
    """Make a POST request to the backend."""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        resp = httpx.post(url, params=params, timeout=120.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return {}


# ── Data Endpoints ─────────────────────────────────────────

def get_markets() -> Dict[str, Any]:
    return _get("/api/data/markets")


def get_latest_prices(market: str) -> Dict[str, Any]:
    return _get("/api/data/latest", {"market": market})


def get_price_history(commodity: str, market: str, limit: int = 200) -> Dict[str, Any]:
    return _get(f"/api/data/prices/{commodity}", {"market": market, "limit": limit})


def refresh_data(market: str) -> Dict[str, Any]:
    return _post("/api/data/refresh", {"market": market})


def get_news(market: str, limit: int = 15) -> Dict[str, Any]:
    return _get("/api/data/news", {"market": market, "limit": limit})


# ── Prediction Endpoints ──────────────────────────────────

def get_prediction(commodity: str, market: str, horizon: int = 7) -> Dict[str, Any]:
    return _get(f"/api/predict/{commodity}", {"market": market, "horizon": horizon})


def get_all_predictions(market: str, horizon: int = 7) -> Dict[str, Any]:
    return _get("/api/predict/all/forecasts", {"market": market, "horizon": horizon})


# ── Signal Endpoints ──────────────────────────────────────

def get_signal(commodity: str, market: str, horizon: int = 7) -> Dict[str, Any]:
    return _get(f"/api/signals/{commodity}", {"market": market, "horizon": horizon})


def get_all_signals(market: str, horizon: int = 7) -> Dict[str, Any]:
    return _get("/api/signals/all", {"market": market, "horizon": horizon})


# ── Report Endpoints ──────────────────────────────────────

def get_daily_report(market: str) -> Dict[str, Any]:
    return _get("/api/reports/daily", {"market": market})


def get_commodity_analysis(commodity: str, market: str) -> Dict[str, Any]:
    return _get(f"/api/reports/analysis/{commodity}", {"market": market})


def get_prediction_explanation(commodity: str, market: str, horizon: int = 7) -> Dict[str, Any]:
    return _get(f"/api/reports/prediction-explain/{commodity}", {"market": market, "horizon": horizon})


def get_confidence(commodity: str, market: str, horizon: int = 7) -> Dict[str, Any]:
    return _get(f"/api/reports/confidence/{commodity}", {"market": market, "horizon": horizon})
