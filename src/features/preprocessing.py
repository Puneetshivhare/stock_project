import pandas as pd
import logging

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the DataFrame by handling missing values.
    """
    if df.empty:
        return df
    
    # Forward fill then backward fill
    df_clean = df.ffill().bfill()
    
    # Drop rows that still have NaNs (if any remain)
    initial_len = len(df)
    df_clean.dropna(inplace=True)
    final_len = len(df_clean)
    
    if initial_len != final_len:
        logging.info(f"Dropped {initial_len - final_len} rows during cleaning.")
        
    return df_clean

def prepare_for_model(df: pd.DataFrame, target_col: str = 'Close', lag_days: int = 1) -> pd.DataFrame:
    """
    Prepares data for modeling. Can be extended to create lag features.
    For Prophet, we usually need 'ds' and 'y'.
    """
    # Simply return cleaned df for now, specific model prep can happen in model wrappers
    return df
