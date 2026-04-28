"""
Feature engineering — technical indicators and derived features for ML models.
"""

import pandas as pd
import numpy as np
from typing import Optional


def add_lag_features(df: pd.DataFrame, column: str = "close", lags: list = None) -> pd.DataFrame:
    """Add lagged values of a column."""
    if lags is None:
        lags = [1, 2, 3, 5, 7, 14, 21]

    for lag in lags:
        df[f"{column}_lag_{lag}"] = df[column].shift(lag)

    return df


def add_rolling_features(df: pd.DataFrame, column: str = "close") -> pd.DataFrame:
    """Add rolling statistics."""
    windows = [5, 10, 20, 50]

    for w in windows:
        df[f"rolling_mean_{w}"] = df[column].rolling(window=w).mean()
        df[f"rolling_std_{w}"] = df[column].rolling(window=w).std()

    # Price change features
    df["pct_change_1d"] = df[column].pct_change(1)
    df["pct_change_5d"] = df[column].pct_change(5)
    df["pct_change_20d"] = df[column].pct_change(20)

    # Volatility
    df["volatility_10d"] = df[column].pct_change().rolling(10).std()
    df["volatility_20d"] = df[column].pct_change().rolling(20).std()

    return df


def add_price_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """Add price pattern features."""
    # Day of week (0=Monday, 4=Friday)
    if "date" in df.columns:
        dates = pd.to_datetime(df["date"])
        df["day_of_week"] = dates.dt.dayofweek
        df["month"] = dates.dt.month
        df["quarter"] = dates.dt.quarter

    # Price position relative to moving averages
    if "sma_20" in df.columns and "close" in df.columns:
        df["price_vs_sma20"] = (df["close"] - df["sma_20"]) / df["sma_20"]
    if "sma_50" in df.columns and "close" in df.columns:
        df["price_vs_sma50"] = (df["close"] - df["sma_50"]) / df["sma_50"]

    # Bollinger Band position
    if all(col in df.columns for col in ["bb_upper", "bb_lower", "close"]):
        bb_range = df["bb_upper"] - df["bb_lower"]
        bb_range = bb_range.replace(0, np.nan)
        df["bb_position"] = (df["close"] - df["bb_lower"]) / bb_range

    return df


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full feature engineering pipeline.
    Expects a DataFrame with: date, open, high, low, close, volume,
    and optionally: rsi, macd, macd_signal, bb_upper, bb_lower, sma_20, sma_50
    """
    df = df.copy()
    df = add_lag_features(df)
    df = add_rolling_features(df)
    df = add_price_patterns(df)
    return df
