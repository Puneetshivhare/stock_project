"""
LLM-based market analyzer — generates qualitative reports using Gemini.
Market-aware prompts produce localized analysis for India, US, and China.
"""

import logging
from typing import Dict, Any, List, Optional

from backend.config import MARKETS, COMMODITY_NAMES
from backend.llm.gemini_client import generate_text

logger = logging.getLogger(__name__)


def generate_daily_summary(
    market: str,
    latest_prices: List[Dict[str, Any]],
    news: List[Dict[str, Any]],
    signals: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate a daily market summary using LLM."""
    market_config = MARKETS.get(market, {})
    market_name = market_config.get("name", market)
    currency = market_config.get("currency", "USD")
    symbol = market_config.get("symbol", "$")

    # Format price data
    price_text = ""
    for p in latest_prices:
        commodity = p.get("commodity", "unknown")
        name = COMMODITY_NAMES.get(commodity, commodity.title())
        close = p.get("close", 0)
        rsi = p.get("rsi", "N/A")
        price_text += f"- {name}: {symbol}{close:,.2f} {currency} (RSI: {rsi})\n"

    # Format news
    news_text = ""
    for n in news[:5]:
        news_text += f"- {n.get('title', 'N/A')} ({n.get('source', 'N/A')})\n"

    # Format signals if available
    signal_text = ""
    if signals:
        for commodity, sig in signals.items():
            if isinstance(sig, dict) and "signal" in sig:
                signal_text += f"- {COMMODITY_NAMES.get(commodity, commodity)}: {sig['signal']} (Strength: {sig.get('strength', 'N/A')})\n"

    prompt = f"""You are a senior commodity market analyst specializing in the {market_name} market.

Generate a professional daily market review for commodity metals (Gold, Silver, Copper) in the {market_name} market.
All prices are in {currency} ({symbol}).

## Current Prices:
{price_text if price_text else "Data loading..."}

## Recent News Headlines:
{news_text if news_text else "No news available at this time."}

## Model Signals:
{signal_text if signal_text else "Signals being calculated..."}

## Instructions:
1. Start with a brief market overview (2-3 sentences)
2. Analyze each commodity individually (Gold, Silver, Copper)
3. Highlight key technical levels and trends
4. Mention any relevant macro factors for {market_name}
5. End with a brief outlook for the next trading session
6. Use {symbol} for all prices
7. Keep the tone professional but accessible
8. Format using markdown with headers

Generate the analysis now:"""

    return generate_text(prompt, max_tokens=2048)


def generate_prediction_explanation(
    market: str,
    commodity: str,
    forecast_data: Dict[str, Any],
) -> str:
    """Generate an LLM explanation of why the model predicts a certain direction."""
    market_config = MARKETS.get(market, {})
    currency = market_config.get("currency", "USD")
    symbol = market_config.get("symbol", "$")
    name = COMMODITY_NAMES.get(commodity, commodity.title())

    direction = forecast_data.get("direction", "FLAT")
    pct_change = forecast_data.get("pct_change", 0)
    current = forecast_data.get("current_price", 0)
    horizon = forecast_data.get("horizon", 7)
    predictions = forecast_data.get("predictions", [])

    pred_text = ""
    for p in predictions[:5]:
        pred_text += f"  - {p['date']}: {symbol}{p['predicted']:,.2f} (range: {symbol}{p['lower']:,.2f} — {symbol}{p['upper']:,.2f})\n"

    prompt = f"""You are a quantitative analyst explaining a machine learning forecast.

Explain in plain language why our model predicts {name} in the {market_config.get('name', market)} market
will move {direction} by {pct_change:+.1f}% over the next {horizon} days.

Current price: {symbol}{current:,.2f} {currency}
Forecast direction: {direction}
Predicted change: {pct_change:+.1f}%
Key predictions:
{pred_text}

Provide:
1. A brief summary of the prediction (2 sentences)
2. Key factors that likely drive this prediction (technical patterns, seasonality, momentum)
3. Risk factors and caveats
4. A confidence assessment (how much should the user trust this prediction)

Keep it under 250 words. Use {symbol} for prices. Be honest about model limitations."""

    return generate_text(prompt, max_tokens=1024)


def generate_commodity_analysis(
    market: str,
    commodity: str,
    price_data: Dict[str, Any],
    news: List[Dict[str, Any]],
) -> str:
    """Generate a deep dive analysis for a specific commodity."""
    market_config = MARKETS.get(market, {})
    symbol = market_config.get("symbol", "$")
    currency = market_config.get("currency", "USD")
    name = COMMODITY_NAMES.get(commodity, commodity.title())

    prompt = f"""You are a senior {name} market specialist for the {market_config.get('name', market)} market.

Generate a detailed analysis of {name} based on the following data:

Price: {symbol}{price_data.get('close', 'N/A')} {currency}
RSI: {price_data.get('rsi', 'N/A')}
MACD: {price_data.get('macd', 'N/A')} / Signal: {price_data.get('macd_signal', 'N/A')}
SMA20: {symbol}{price_data.get('sma_20', 'N/A')}
SMA50: {symbol}{price_data.get('sma_50', 'N/A')}
Bollinger Bands: {symbol}{price_data.get('bb_lower', 'N/A')} — {symbol}{price_data.get('bb_upper', 'N/A')}

Recent news:
{chr(10).join(f"- {n.get('title', '')}" for n in news[:3])}

Provide:
1. **Technical Analysis** — key support/resistance levels, trend direction, indicator readings
2. **Fundamental Factors** — what's driving {name} in the {market_config.get('name', market)} market
3. **Key Risks** — potential downside catalysts
4. **Short-term Outlook** — 1-week expectation
5. **Trading Consideration** — what traders should watch for

Keep it professional, data-driven, and under 300 words. Use {symbol} for all prices."""

    return generate_text(prompt, max_tokens=1536)
