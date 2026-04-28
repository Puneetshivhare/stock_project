"""
SQLite storage layer — market-aware tables for price data and news.
"""

import sqlite3
import os
import pandas as pd
from typing import Optional, List, Dict, Any

from backend.config import DB_PATH


def _get_connection() -> sqlite3.Connection:
    """Get SQLite connection, creating the DB directory if needed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """Create all required tables if they don't exist."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market TEXT NOT NULL,
            commodity TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            currency TEXT,
            rsi REAL,
            macd REAL,
            macd_signal REAL,
            macd_hist REAL,
            bb_upper REAL,
            bb_middle REAL,
            bb_lower REAL,
            sma_20 REAL,
            sma_50 REAL,
            ema_12 REAL,
            ema_26 REAL,
            UNIQUE(market, commodity, date)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market TEXT NOT NULL,
            title TEXT NOT NULL,
            source TEXT,
            date TEXT,
            url TEXT,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prediction_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market TEXT NOT NULL,
            commodity TEXT NOT NULL,
            horizon INTEGER NOT NULL,
            predictions_json TEXT,
            model_metrics_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(market, commodity, horizon)
        )
    """)

    conn.commit()
    conn.close()


def upsert_price_data(market: str, commodity: str, df: pd.DataFrame):
    """Insert or update price data from a DataFrame."""
    conn = _get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO price_data
                (market, commodity, date, open, high, low, close, volume, currency,
                 rsi, macd, macd_signal, macd_hist,
                 bb_upper, bb_middle, bb_lower, sma_20, sma_50, ema_12, ema_26)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(market, commodity, date) DO UPDATE SET
                open=excluded.open, high=excluded.high,
                low=excluded.low, close=excluded.close,
                volume=excluded.volume, currency=excluded.currency,
                rsi=excluded.rsi, macd=excluded.macd,
                macd_signal=excluded.macd_signal, macd_hist=excluded.macd_hist,
                bb_upper=excluded.bb_upper, bb_middle=excluded.bb_middle,
                bb_lower=excluded.bb_lower, sma_20=excluded.sma_20,
                sma_50=excluded.sma_50, ema_12=excluded.ema_12, ema_26=excluded.ema_26
        """, (
            market, commodity,
            str(row.get("date", "")),
            row.get("open"), row.get("high"), row.get("low"), row.get("close"),
            row.get("volume"), row.get("currency", "USD"),
            row.get("rsi"), row.get("macd"), row.get("macd_signal"), row.get("macd_hist"),
            row.get("bb_upper"), row.get("bb_middle"), row.get("bb_lower"),
            row.get("sma_20"), row.get("sma_50"), row.get("ema_12"), row.get("ema_26"),
        ))

    conn.commit()
    conn.close()


def get_price_history(
    market: str,
    commodity: str,
    limit: int = 500,
) -> pd.DataFrame:
    """Retrieve price history as a DataFrame."""
    conn = _get_connection()
    query = """
        SELECT * FROM price_data
        WHERE market = ? AND commodity = ?
        ORDER BY date DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(market, commodity, limit))
    conn.close()

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
    return df


def get_latest_prices(market: str) -> List[Dict[str, Any]]:
    """Get the latest price row for each commodity in a market."""
    conn = _get_connection()
    cursor = conn.cursor()

    results = []
    for commodity in ["gold", "silver", "copper"]:
        cursor.execute("""
            SELECT * FROM price_data
            WHERE market = ? AND commodity = ?
            ORDER BY date DESC LIMIT 1
        """, (market, commodity))
        row = cursor.fetchone()
        if row:
            results.append(dict(row))

    conn.close()
    return results


def save_news(market: str, articles: List[Dict[str, Any]]):
    """Save news articles to cache."""
    conn = _get_connection()
    cursor = conn.cursor()

    for article in articles:
        cursor.execute("""
            INSERT INTO news_cache (market, title, source, date, url, summary)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            market,
            article.get("title", ""),
            article.get("source", ""),
            article.get("date", ""),
            article.get("url", ""),
            article.get("summary", ""),
        ))

    conn.commit()
    conn.close()


def get_news(market: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get cached news for a market."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM news_cache
        WHERE market = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (market, limit))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def save_prediction_cache(
    market: str, commodity: str, horizon: int,
    predictions_json: str, metrics_json: str,
):
    """Cache prediction results."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO prediction_cache
            (market, commodity, horizon, predictions_json, model_metrics_json)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(market, commodity, horizon) DO UPDATE SET
            predictions_json=excluded.predictions_json,
            model_metrics_json=excluded.model_metrics_json,
            created_at=CURRENT_TIMESTAMP
    """, (market, commodity, horizon, predictions_json, metrics_json))
    conn.commit()
    conn.close()


def get_prediction_cache(
    market: str, commodity: str, horizon: int, max_age_hours: int = 24,
) -> Optional[Dict[str, Any]]:
    """Get cached prediction if it's less than max_age_hours old."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM prediction_cache
        WHERE market = ? AND commodity = ? AND horizon = ?
          AND created_at > datetime('now', ?)
        ORDER BY created_at DESC LIMIT 1
    """, (market, commodity, horizon, f"-{max_age_hours} hours"))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def clear_old_news(days: int = 7):
    """Remove news older than N days."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM news_cache
        WHERE created_at < datetime('now', ?)
    """, (f"-{days} days",))
    conn.commit()
    conn.close()
