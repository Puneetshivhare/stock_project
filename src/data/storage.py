import pandas as pd
import os
import logging

def save_data(df: pd.DataFrame, filename: str, folder: str = "data/raw"):
    """
    Saves a DataFrame to a CSV file.
    
    Args:
        df (pd.DataFrame): Data to save.
        filename (str): Name of the file (e.g., "AAPL_price.csv").
        folder (str): Target folder relative to project root.
    """
    if df.empty:
        logging.warning("DataFrame is empty. Nothing to save.")
        return

    try:
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)
        df.to_csv(filepath, index=False)
        logging.info(f"Data saved to {filepath}")
    except Exception as e:
        logging.error(f"Error saving data to {filepath}: {e}")

def load_data(filename: str, folder: str = "data/raw") -> pd.DataFrame:
    """
    Loads data from a CSV file.
    
    Args:
        filename (str): Filename to load.
        folder (str): Folder path.
        
    Returns:
        pd.DataFrame: Loaded data.
    """
    try:
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            logging.error(f"File not found: {filepath}")
            return pd.DataFrame()
            
        df = pd.read_csv(filepath)
        # Convert Date column to datetime if it exists
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            
        logging.info(f"Data loaded from {filepath}")
        return df
    except Exception as e:
        logging.error(f"Error loading data from {filepath}: {e}")
        return pd.DataFrame()
