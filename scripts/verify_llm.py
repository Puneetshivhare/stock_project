import sys
import os
import logging

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm.explainer import generate_insight

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_llm():
    logging.info("Testing LLM Insight Generation...")
    
    ticker = "AAPL"
    signal_data = {
        'action': 'BUY',
        'confidence': 0.8,
        'predicted_price': 155.0,
        'current_price': 150.0
    }
    indicators = {'RSI': 35, 'MACD': 1.5}
    
    insight = generate_insight(ticker, signal_data, indicators)
    
    logging.info("Result:")
    print(insight)
    
    if not insight:
        logging.error("Insight is empty.")
        sys.exit(1)
        
    logging.info("Verification passed!")

if __name__ == "__main__":
    test_llm()
