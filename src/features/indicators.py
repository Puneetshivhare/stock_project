import pandas as pd
import ta
import logging

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds technical indicators to the DataFrame.
    
    indicators added:
    - RSI (14)
    - MACD (12, 26, 9)
    - SMA (20, 50)
    - Bollinger Bands (20, 2.0)
    
    Args:
        df (pd.DataFrame): DataFrame with 'Close' column.
        
    Returns:
        pd.DataFrame: DataFrame with added indicator columns.
    """
    if df.empty:
        logging.warning("Empty DataFrame provided to indicators.")
        return df
        
    df = df.copy()
    
    # Ensure 'Close' exists
    if 'Close' not in df.columns:
        logging.error("DataFrame missing 'Close' column.")
        return df

    try:
        logging.info("Computing technical indicators...")

        # RSI
        df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()

        # MACD
        macd = ta.trend.MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Diff'] = macd.macd_diff()

        # SMA
        df['SMA_20'] = ta.trend.SMAIndicator(close=df['Close'], window=20).sma_indicator()
        df['SMA_50'] = ta.trend.SMAIndicator(close=df['Close'], window=50).sma_indicator()

        # Bollinger Bands
        bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['BB_High'] = bb.bollinger_hband()
        df['BB_Low'] = bb.bollinger_lband()
        
        # VWAP (if Volume is available)
        if 'Volume' in df.columns and 'High' in df.columns and 'Low' in df.columns:
             vwap = ta.volume.VolumeWeightedAveragePrice(
                 high=df['High'], low=df['Low'], close=df['Close'], volume=df['Volume']
             )
             df['VWAP'] = vwap.volume_weighted_average_price()

        logging.info("Technical indicators computed successfully.")
        return df
    except Exception as e:
        logging.error(f"Error computing indicators: {e}")
        return df
