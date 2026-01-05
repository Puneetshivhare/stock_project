import sys
import os
import logging
import pandas as pd

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.features.indicators import add_technical_indicators
from src.features.preprocessing import clean_data

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_features():
    # Create sample data
    data = {
        'Date': pd.date_range(start='2023-01-01', periods=100, freq='D'),
        'Open': [100 + i for i in range(100)],
        'High': [105 + i for i in range(100)],
        'Low': [95 + i for i in range(100)],
        'Close': [102 + i for i in range(100)],
        'Volume': [1000 for _ in range(100)]
    }
    df = pd.DataFrame(data)
    
    logging.info("Testing Technical Indicators...")
    df_indicators = add_technical_indicators(df)
    
    if 'RSI' not in df_indicators.columns:
        logging.error("RSI not found in columns!")
        sys.exit(1)
        
    logging.info(f"Columns after indicators: {df_indicators.columns.tolist()}")
    
    # Check if NaN values exist (indicators introduce NaNs at start)
    logging.info("Checking NaNs before cleaning...")
    print(df_indicators.head(20)) # First 14 for RSI should be NaN
    
    logging.info("Testing Cleaning...")
    df_clean = clean_data(df_indicators)
    
    if df_clean.isnull().sum().sum() > 0:
        logging.error("NaNs found after cleaning!")
        sys.exit(1)
        
    logging.info(f"Shape after cleaning: {df_clean.shape}")
    print(df_clean.head())
    
    logging.info("Feature verification passed!")

if __name__ == "__main__":
    test_features()
