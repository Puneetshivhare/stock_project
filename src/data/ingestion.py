import yfinance as yf
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_stock_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetches historical stock price data from Yahoo Finance.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., "AAPL", "RELIANCE.NS").
        period (str): Data period to download (e.g., "1y", "max").
        interval (str): Data interval (e.g., "1d", "1h").
        
    Returns:
        pd.DataFrame: Historical data with columns like Open, High, Low, Close, Volume.
    """
    logging.info(f"Fetching stock data for {ticker} (Period: {period}, Interval: {interval})...")
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        
        if df.empty:
            logging.warning(f"No data found for {ticker}.")
            return pd.DataFrame()
            
        # Reset index to make Date a column
        df.reset_index(inplace=True)
        # Ensure timezone is removed or handled if needed for consistency
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
            
        logging.info(f"Successfully fetched {len(df)} rows for {ticker}.")
        return df
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

def fetch_fundamentals(ticker: str) -> dict:
    """
    Fetches basic fundamental data from Yahoo Finance.
    
    Args:
        ticker (str): Stock ticker symbol.
        
    Returns:
        dict: Dictionary containing fundamental info.
    """
    logging.info(f"Fetching fundamentals for {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        # info contains a lot of data; we can filter or return all
        info = stock.info
        logging.info(f"Successfully fetched fundamentals for {ticker}.")
        return info
    except Exception as e:
        logging.error(f"Error fetching fundamentals for {ticker}: {e}")
        return {}

def fetch_moneycontrol_fundamentals(ticker: str):
    """
    Placeholder for Moneycontrol scraping logic.
    """
    logging.warning("Moneycontrol fetcher not yet implemented.")
    return None
