"""
Buy/sell signal generation — combines Prophet forecasts with technical indicators.
"""

import logging
from typing import Dict, Any, List

from backend.config import MARKETS, COMMODITY_NAMES
from backend.data.storage import get_price_history
from backend.ml.forecaster import forecast_commodity

logger = logging.getLogger(__name__)


def _evaluate_rsi(rsi: float) -> Dict[str, Any]:
    """Evaluate RSI for overbought/oversold conditions."""
    if rsi is None:
        return {"signal": "HOLD", "reason": "RSI data unavailable"}
    if rsi > 70:
        return {"signal": "SELL", "reason": f"RSI={rsi:.1f} — overbought (>70)"}
    elif rsi < 30:
        return {"signal": "BUY", "reason": f"RSI={rsi:.1f} — oversold (<30)"}
    else:
        return {"signal": "HOLD", "reason": f"RSI={rsi:.1f} — neutral zone"}


def _evaluate_macd(macd: float, macd_signal: float, macd_hist: float) -> Dict[str, Any]:
    """Evaluate MACD crossover signals."""
    if macd is None or macd_signal is None:
        return {"signal": "HOLD", "reason": "MACD data unavailable"}
    if macd > macd_signal and macd_hist > 0:
        return {"signal": "BUY", "reason": "MACD bullish crossover (MACD > Signal)"}
    elif macd < macd_signal and macd_hist < 0:
        return {"signal": "SELL", "reason": "MACD bearish crossover (MACD < Signal)"}
    else:
        return {"signal": "HOLD", "reason": "MACD neutral — no clear crossover"}


def _evaluate_sma(close: float, sma_20: float, sma_50: float) -> Dict[str, Any]:
    """Evaluate price position relative to SMAs."""
    if sma_20 is None or sma_50 is None:
        return {"signal": "HOLD", "reason": "SMA data unavailable"}
    if close > sma_20 and sma_20 > sma_50:
        return {"signal": "BUY", "reason": "Price above SMA20 > SMA50 — bullish trend"}
    elif close < sma_20 and sma_20 < sma_50:
        return {"signal": "SELL", "reason": "Price below SMA20 < SMA50 — bearish trend"}
    else:
        return {"signal": "HOLD", "reason": "SMAs mixed — sideways trend"}


def _evaluate_forecast(direction: str, pct_change: float) -> Dict[str, Any]:
    """Evaluate forecast direction signal."""
    if direction == "UP" and pct_change > 1.0:
        return {"signal": "BUY", "reason": f"Model predicts +{pct_change:.1f}% upside"}
    elif direction == "DOWN" and pct_change < -1.0:
        return {"signal": "SELL", "reason": f"Model predicts {pct_change:.1f}% downside"}
    else:
        return {"signal": "HOLD", "reason": f"Model predicts {pct_change:+.1f}% — within noise range"}


def generate_signal(market: str, commodity: str, horizon: int = 7) -> Dict[str, Any]:
    """
    Generate a buy/sell/hold signal for a commodity in a market.

    Returns:
        {
            "market": str,
            "commodity": str,
            "commodity_name": str,
            "currency": str,
            "current_price": float,
            "signal": "BUY" | "SELL" | "HOLD",
            "strength": 0-100,
            "reasons": [...],
            "technical_signals": {...},
            "forecast_summary": {...}
        }
    """
    market_config = MARKETS.get(market)
    if not market_config:
        raise ValueError(f"Unknown market: {market}")

    # Get latest price data
    df = get_price_history(market, commodity, limit=5)
    if df.empty:
        raise ValueError(f"No price data for {market}/{commodity}")

    latest = df.iloc[-1]
    current_price = float(latest["close"])

    # Evaluate technical indicators
    signals = []
    rsi_eval = _evaluate_rsi(latest.get("rsi"))
    macd_eval = _evaluate_macd(latest.get("macd"), latest.get("macd_signal"), latest.get("macd_hist"))
    sma_eval = _evaluate_sma(current_price, latest.get("sma_20"), latest.get("sma_50"))
    signals.extend([rsi_eval, macd_eval, sma_eval])

    # Evaluate forecast
    try:
        forecast = forecast_commodity(market, commodity, horizon, use_cache=True)
        forecast_eval = _evaluate_forecast(forecast["direction"], forecast["pct_change"])
        signals.append(forecast_eval)
        forecast_summary = {
            "direction": forecast["direction"],
            "pct_change": forecast["pct_change"],
            "horizon": horizon,
            "predictions": forecast.get("predictions", []),
        }
    except Exception as e:
        logger.warning(f"Forecast unavailable for signal: {e}")
        forecast_eval = {"signal": "HOLD", "reason": "Forecast unavailable"}
        signals.append(forecast_eval)
        forecast_summary = {"error": str(e)}

    # Tally signals
    buy_count = sum(1 for s in signals if s["signal"] == "BUY")
    sell_count = sum(1 for s in signals if s["signal"] == "SELL")
    total = len(signals)

    if buy_count > sell_count and buy_count >= 2:
        overall_signal = "BUY"
        strength = min(100, int((buy_count / total) * 100) + 10)
    elif sell_count > buy_count and sell_count >= 2:
        overall_signal = "SELL"
        strength = min(100, int((sell_count / total) * 100) + 10)
    else:
        overall_signal = "HOLD"
        strength = max(20, 50 - abs(buy_count - sell_count) * 15)

    reasons = [s["reason"] for s in signals]

    return {
        "market": market,
        "commodity": commodity,
        "commodity_name": COMMODITY_NAMES.get(commodity, commodity.title()),
        "currency": market_config["currency"],
        "symbol": market_config["symbol"],
        "current_price": round(current_price, 2),
        "signal": overall_signal,
        "strength": strength,
        "reasons": reasons,
        "technical_signals": {
            "rsi": rsi_eval,
            "macd": macd_eval,
            "sma": sma_eval,
            "forecast": forecast_eval,
        },
        "forecast_summary": forecast_summary,
    }


def generate_all_signals(market: str, horizon: int = 7) -> Dict[str, Any]:
    """Generate signals for all commodities in a market."""
    results = {}
    for commodity in ["gold", "silver", "copper"]:
        try:
            results[commodity] = generate_signal(market, commodity, horizon)
        except Exception as e:
            logger.error(f"Signal error {market}/{commodity}: {e}")
            results[commodity] = {"error": str(e)}
    return results
