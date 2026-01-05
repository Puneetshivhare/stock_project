import logging
import json
from .client import LLMClient
from .prompts import REPORT_PROMPT_TEMPLATE

def generate_insight(ticker: str, signal_data: dict, indicators: dict) -> str:
    """
    Generates a natural language explanation for the signal.
    """
    client = LLMClient()
    
    prompt = REPORT_PROMPT_TEMPLATE.format(
        ticker=ticker,
        current_price=signal_data.get('current_price', 'N/A'),
        predicted_price=signal_data.get('predicted_price', 'N/A'),
        signal=signal_data.get('action', 'UNKNOWN'),
        confidence=signal_data.get('confidence', 0.0),
        indicators=json.dumps(indicators, default=str)
    )
    
    logging.info(f"Generating insight for {ticker}...")
    insight = client.get_completion(prompt)
    return insight
