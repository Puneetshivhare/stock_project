"""
LLM-based confidence scoring — uses Gemini to evaluate prediction quality.
"""

import json
import logging
from typing import Dict, Any

from backend.config import MARKETS, COMMODITY_NAMES
from backend.llm.gemini_client import generate_text

logger = logging.getLogger(__name__)


def score_prediction_confidence(
    market: str,
    commodity: str,
    forecast_data: Dict[str, Any],
    latest_price_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Use LLM to score the confidence of a prediction.

    Returns:
        {
            "confidence_score": 0-100,
            "confidence_level": "HIGH" | "MEDIUM" | "LOW",
            "positive_factors": [...],
            "risk_factors": [...],
            "summary": str
        }
    """
    market_config = MARKETS.get(market, {})
    name = COMMODITY_NAMES.get(commodity, commodity.title())
    symbol = market_config.get("symbol", "$")

    direction = forecast_data.get("direction", "FLAT")
    pct_change = forecast_data.get("pct_change", 0)
    horizon = forecast_data.get("horizon", 7)
    metrics = forecast_data.get("model_metrics", {})
    current_price = forecast_data.get("current_price", 0)

    # Technical indicator context
    rsi = latest_price_data.get("rsi", "N/A")
    macd = latest_price_data.get("macd", "N/A")

    prompt = f"""You are a risk analyst evaluating the confidence of a machine learning prediction.

Prediction Details:
- Asset: {name} in {market_config.get('name', market)}
- Current Price: {symbol}{current_price:,.2f}
- Predicted Direction: {direction} ({pct_change:+.1f}%)
- Horizon: {horizon} days
- Model MAPE: {metrics.get('mape', 'N/A')}%
- Model RMSE: {symbol}{metrics.get('rmse', 'N/A')}

Technical Context:
- RSI: {rsi}
- MACD: {macd}

Respond in this EXACT JSON format and nothing else:
{{
    "confidence_score": <number 0-100>,
    "confidence_level": "<HIGH|MEDIUM|LOW>",
    "positive_factors": ["<factor1>", "<factor2>"],
    "risk_factors": ["<risk1>", "<risk2>"],
    "summary": "<1-2 sentence summary>"
}}

Score based on: model accuracy metrics, magnitude of prediction, technical indicator alignment,
and general market volatility for {name}. Be realistic — commodity predictions beyond 7 days have high uncertainty."""

    try:
        response = generate_text(prompt, max_tokens=512)

        # Try to parse JSON from response
        # Handle case where response has markdown code blocks
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[-1]
            clean = clean.rsplit("```", 1)[0]

        result = json.loads(clean)
        return result
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Could not parse confidence response: {e}")
        # Return a reasonable default
        return {
            "confidence_score": 50,
            "confidence_level": "MEDIUM",
            "positive_factors": ["Model has historical data support"],
            "risk_factors": ["Commodity markets are inherently volatile"],
            "summary": f"Moderate confidence in {direction} prediction for {name}. "
                       f"Model MAPE of {metrics.get('mape', 'N/A')}% suggests reasonable accuracy.",
        }
