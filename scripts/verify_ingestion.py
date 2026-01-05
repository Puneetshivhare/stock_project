import sys
import os
import logging

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.ingestion import fetch_stock_data, fetch_fundamentals
from src.data.storage import save_data, load_data

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_ingestion():
    ticker = "AAPL"
    
    # 1. Fetch Data
    logging.info(f"Testing ingestion for {ticker}...")
    df = fetch_stock_data(ticker, period="1mo", interval="1d")
    
    if df.empty:
        logging.error("Fetched DataFrame is empty!")
        sys.exit(1)
    
    print("Head of fetched data:")
    print(df.head())
    
    # 2. Save Data
    logging.info("Testing storage (save)...")
    save_data(df, f"{ticker}_test.csv")
    
    # 3. Load Data
    logging.info("Testing storage (load)...")
    df_loaded = load_data(f"{ticker}_test.csv")
    
    if df_loaded.empty:
        logging.error("Loaded DataFrame is empty!")
        sys.exit(1)
        
    print("Head of loaded data:")
    print(df_loaded.head())
    
    # 4. Fetch Fundamentals
    logging.info("Testing fundamentals fetch...")
    fund = fetch_fundamentals(ticker)
    print(f"Fundamentals keys: {list(fund.keys())[:5]}")
    
    logging.info("Verification passed!")

if __name__ == "__main__":
    test_ingestion()
