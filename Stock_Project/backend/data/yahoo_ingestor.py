"""
Yahoo Finance data ingestor — fetches OHLCV for Gold, Silver, Copper
with FX conversion for India (INR) and China (CNY) markets.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import ta
from typing import Optional
import logging

from backend.config import MARKETS, DATA_HISTORY_PERIOD, COMMODITY_NAMES
from backend.data.storage import upsert_price_data

logger = logging.getLogger(__name__)


def _fetch_ticker_data(ticker: str, period: str = DATA_HISTORY_PERIOD) -> pd.DataFrame:
    """Fetch OHLCV data from Yahoo Finance."""
    try:
        data = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        if data.empty:
            logger.warning(f"No data returned for {ticker}")
            return pd.DataFrame()

        # Handle MultiIndex columns (yfinance sometimes returns these)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = data.reset_index()
        data.columns = [c.lower() for c in data.columns]
        return data
    except Exception as e:
        logger.error(f"Error fetching {ticker}: {e}")
        return pd.DataFrame()


def _fetch_fx_rate(fx_ticker: str, period: str = DATA_HISTORY_PERIOD) -> pd.DataFrame:
    """Fetch FX exchange rate series."""
    try:
        fx_data = yf.download(fx_ticker, period=period, progress=False, auto_adjust=True)
        if isinstance(fx_data.columns, pd.MultiIndex):
            fx_data.columns = fx_data.columns.get_level_values(0)
        fx_data = fx_data.reset_index()
        fx_data.columns = [c.lower() for c in fx_data.columns]
        return fx_data[["date", "close"]].rename(columns={"close": "fx_rate"})
    except Exception as e:
        logger.error(f"Error fetching FX rate {fx_ticker}: {e}")
        return pd.DataFrame()


def _add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add RSI, MACD, Bollinger Bands, SMA, EMA to the DataFrame."""
    if len(df) < 30:
        return df

    close = df["close"]

    # RSI
    df["rsi"] = ta.momentum.RSIIndicator(close, window=14).rsi()

    # MACD
    macd_indicator = ta.trend.MACD(close, window_slow=26, window_fast=12, window_sign=9)
    df["macd"] = macd_indicator.macd()
    df["macd_signal"] = macd_indicator.macd_signal()
    df["macd_hist"] = macd_indicator.macd_diff()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_middle"] = bb.bollinger_mavg()
    df["bb_lower"] = bb.bollinger_lband()

    # SMAs
    df["sma_20"] = ta.trend.SMAIndicator(close, window=20).sma_indicator()
    df["sma_50"] = ta.trend.SMAIndicator(close, window=50).sma_indicator()

    # EMAs
    df["ema_12"] = ta.trend.EMAIndicator(close, window=12).ema_indicator()
    df["ema_26"] = ta.trend.EMAIndicator(close, window=26).ema_indicator()

    return df


def ingest_market_data(market: str, period: str = DATA_HISTORY_PERIOD) -> dict:
    """
    Ingest data for all commodities in a specific market.
    Returns summary of what was ingested.
    """
    market_config = MARKETS.get(market)
    if not market_config:
        raise ValueError(f"Unknown market: {market}")

    fx_data = None
    fx_ticker = market_config.get("fx_ticker")

    # Fetch FX rate if needed (non-USD markets)
    if fx_ticker:
        logger.info(f"Fetching FX rate: {fx_ticker}")
        fx_data = _fetch_fx_rate(fx_ticker, period)
        if fx_data.empty:
            logger.warning(f"Could not fetch FX rate {fx_ticker}, using fallback rate")

    summary = {}

    for commodity_key, commodity_cfg in market_config["commodities"].items():
        ticker = commodity_cfg["ticker"]
        multiplier = commodity_cfg.get("multiplier", 1.0)

        logger.info(f"Fetching {commodity_key} ({ticker}) for {market}")

        # Fetch raw USD data
        df = _fetch_ticker_data(ticker, period)
        if df.empty:
            summary[commodity_key] = {"status": "error", "rows": 0}
            continue

        # Convert prices to local currency if FX data available
        if fx_data is not None and not fx_data.empty:
            # Merge FX rate by date
            df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
            fx_data["date"] = pd.to_datetime(fx_data["date"]).dt.tz_localize(None)
            df = df.merge(fx_data, on="date", how="left")
            df["fx_rate"] = df["fx_rate"].ffill().bfill()

            # Apply FX conversion × unit multiplier
            for col in ["open", "high", "low", "close"]:
                df[col] = df[col] * df["fx_rate"] * multiplier

            df = df.drop(columns=["fx_rate"], errors="ignore")
        else:
            # USD market or FX unavailable — just apply multiplier
            for col in ["open", "high", "low", "close"]:
                df[col] = df[col] * multiplier

        # Add technical indicators (calculated on converted prices)
        df = _add_technical_indicators(df)

        # Add metadata
        df["currency"] = market_config["currency"]
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")

        # Save to DB
        upsert_price_data(market, commodity_key, df)

        # Also save as CSV cache
        try:
            import os
            csv_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "data"
            )
            os.makedirs(csv_dir, exist_ok=True)
            csv_path = os.path.join(csv_dir, f"{market}_{commodity_key}_history.csv")
            df.to_csv(csv_path, index=False)
        except Exception as e:
            logger.warning(f"Could not save CSV for {commodity_key}: {e}")

        summary[commodity_key] = {"status": "ok", "rows": len(df)}
        logger.info(f"  ✅ {COMMODITY_NAMES.get(commodity_key, commodity_key)}: {len(df)} rows ingested")

    return summary


def ingest_all_markets(period: str = DATA_HISTORY_PERIOD) -> dict:
    """Ingest data for all configured markets."""
    results = {}
    for market_key in MARKETS:
        try:
            results[market_key] = ingest_market_data(market_key, period)
        except Exception as e:
            logger.error(f"Error ingesting {market_key}: {e}")
            results[market_key] = {"error": str(e)}
    return results
