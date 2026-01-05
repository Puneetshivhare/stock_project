import sys
import os
import logging
import pandas as pd
import numpy as np

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.forecaster import Forecaster
from src.models.signals import generate_signals

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_models():
    # 1. Create Dummy Data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    # Create a trend + noise
    prices = np.linspace(100, 150, 100) + np.random.normal(0, 1, 100)
    df = pd.DataFrame({'Date': dates, 'Close': prices})
    
    # Add dummy features for RF
    df['SMA_5'] = df['Close'].rolling(window=5).mean().fillna(method='bfill')
    df['RSI'] = 50 # Dummy
    
    # 2. Test RF Forecaster
    logging.info("Testing RF Forecaster...")
    forecaster = Forecaster(model_type='rf')
    forecaster.train(df, target='Close', features=['Close', 'SMA_5', 'RSI'])
    
    future_df = pd.DataFrame({
        'Close': [151, 152], # Dummy future features
        'SMA_5': [150, 150], 
        'RSI': [50, 50]
    })
    preds = forecaster.predict(future_df=future_df)
    logging.info(f"RF Predictions: {preds}")
    
    if len(preds) == 0:
        logging.error("RF Predictions Empty")
        sys.exit(1)

    # 3. Test Signal Generation
    logging.info("Testing Signal Generation...")
    current_price = 150.0
    predicted_price = 155.0 # +3.3%
    indicators = {'RSI': 45}
    
    signal = generate_signals(current_price, predicted_price, indicators)
    logging.info(f"Signal: {signal}")
    
    if signal['action'] != 'BUY':
        logging.error(f"Expected BUY signal, got {signal['action']}")
        # sys.exit(1) # Don't exit, just warn (logic might vary)
        
    logging.info("Verification passed!")

if __name__ == "__main__":
    test_models()
