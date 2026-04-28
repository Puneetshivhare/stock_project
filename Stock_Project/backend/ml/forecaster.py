"""
Prophet-based time-series forecaster — per (market, commodity) pair
with 1d, 7d, 30d horizons. Results are cached for 24 hours.
"""

import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from prophet import Prophet

from backend.config import MARKETS, COMMODITY_NAMES, FORECAST_HORIZONS
from backend.data.storage import get_price_history, save_prediction_cache, get_prediction_cache

logger = logging.getLogger(__name__)


def _prepare_prophet_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare data in Prophet format: columns 'ds' (date) and 'y' (close)."""
    prophet_df = pd.DataFrame()
    prophet_df["ds"] = pd.to_datetime(df["date"])
    prophet_df["y"] = df["close"].astype(float)

    # Remove NaN/inf
    prophet_df = prophet_df.replace([np.inf, -np.inf], np.nan).dropna()
    return prophet_df


def _build_model(prophet_df: pd.DataFrame) -> Prophet:
    """Build and fit a Prophet model."""
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        changepoint_prior_scale=0.1,
        seasonality_prior_scale=10.0,
        interval_width=0.90,
    )
    model.fit(prophet_df)
    return model


def _calculate_metrics(actual: pd.Series, predicted: pd.Series) -> Dict[str, float]:
    """Calculate forecast accuracy metrics."""
    mask = ~(actual.isna() | predicted.isna())
    actual = actual[mask]
    predicted = predicted[mask]

    if len(actual) == 0:
        return {"mae": 0, "rmse": 0, "mape": 0}

    mae = float(np.mean(np.abs(actual - predicted)))
    rmse = float(np.sqrt(np.mean((actual - predicted) ** 2)))
    mape = float(np.mean(np.abs((actual - predicted) / actual)) * 100) if (actual != 0).all() else 0

    return {"mae": round(mae, 2), "rmse": round(rmse, 2), "mape": round(mape, 2)}


def forecast_commodity(
    market: str,
    commodity: str,
    horizon: int = 7,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """
    Generate price forecast for a commodity in a specific market.

    Args:
        market: 'india', 'us', or 'china'
        commodity: 'gold', 'silver', or 'copper'
        horizon: forecast days (1, 7, or 30)
        use_cache: whether to use cached results

    Returns:
        {
            "market": str,
            "commodity": str,
            "currency": str,
            "horizon": int,
            "current_price": float,
            "predictions": [{"date": str, "predicted": float, "lower": float, "upper": float}],
            "direction": "UP" | "DOWN" | "FLAT",
            "pct_change": float,
            "model_metrics": {"mae": float, "rmse": float, "mape": float},
        }
    """
    market_config = MARKETS.get(market)
    if not market_config:
        raise ValueError(f"Unknown market: {market}")

    # Check cache first
    if use_cache:
        cached = get_prediction_cache(market, commodity, horizon)
        if cached:
            logger.info(f"Using cached prediction for {market}/{commodity}/{horizon}d")
            return {
                "market": market,
                "commodity": commodity,
                "currency": market_config["currency"],
                "horizon": horizon,
                **json.loads(cached["predictions_json"]),
                "model_metrics": json.loads(cached["model_metrics_json"]),
                "cached": True,
            }

    # Fetch historical data
    df = get_price_history(market, commodity, limit=1000)
    if df.empty or len(df) < 60:
        raise ValueError(f"Not enough data for {market}/{commodity}. Need at least 60 rows, got {len(df)}")

    # Prepare and fit
    prophet_df = _prepare_prophet_data(df)
    model = _build_model(prophet_df)

    # Make future dataframe and predict
    future = model.make_future_dataframe(periods=horizon, freq="B")  # Business days
    forecast = model.predict(future)

    # Extract predictions for the forecast horizon
    future_mask = forecast["ds"] > prophet_df["ds"].max()
    future_forecast = forecast[future_mask].head(horizon)

    predictions = []
    for _, row in future_forecast.iterrows():
        predictions.append({
            "date": row["ds"].strftime("%Y-%m-%d"),
            "predicted": round(float(row["yhat"]), 2),
            "lower": round(float(row["yhat_lower"]), 2),
            "upper": round(float(row["yhat_upper"]), 2),
        })

    # Current price and direction
    current_price = float(df["close"].iloc[-1])
    if predictions:
        final_predicted = predictions[-1]["predicted"]
        pct_change = round(((final_predicted - current_price) / current_price) * 100, 2)
        direction = "UP" if pct_change > 0.5 else ("DOWN" if pct_change < -0.5 else "FLAT")
    else:
        pct_change = 0.0
        direction = "FLAT"

    # Calculate metrics on in-sample fit
    in_sample = forecast[~future_mask]
    metrics = _calculate_metrics(prophet_df["y"], in_sample["yhat"].iloc[:len(prophet_df)])

    result_data = {
        "current_price": round(current_price, 2),
        "predictions": predictions,
        "direction": direction,
        "pct_change": pct_change,
    }

    # Cache the result
    try:
        save_prediction_cache(
            market, commodity, horizon,
            json.dumps(result_data),
            json.dumps(metrics),
        )
    except Exception as e:
        logger.warning(f"Could not cache prediction: {e}")

    return {
        "market": market,
        "commodity": commodity,
        "currency": market_config["currency"],
        "horizon": horizon,
        **result_data,
        "model_metrics": metrics,
        "cached": False,
    }


def forecast_all_commodities(market: str, horizon: int = 7) -> Dict[str, Any]:
    """Forecast all three commodities for a market."""
    results = {}
    for commodity in ["gold", "silver", "copper"]:
        try:
            results[commodity] = forecast_commodity(market, commodity, horizon)
        except Exception as e:
            logger.error(f"Forecast error {market}/{commodity}: {e}")
            results[commodity] = {"error": str(e)}
    return results
