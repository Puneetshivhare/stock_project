import pandas as pd
import numpy as np
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# Try importing prophet, handle failure gracefully
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logging.warning("Prophet not installed or import failed. Prophet model will not be available.")

class Forecaster:
    def __init__(self, model_type: str = 'rf'):
        self.model_type = model_type
        self.model = None
        
    def train(self, df: pd.DataFrame, target: str = 'Close', features: list = None):
        """
        Trains the model.
        """
        if self.model_type == 'rf':
            self._train_rf(df, target, features)
        elif self.model_type == 'prophet':
            self._train_prophet(df)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
            
    def predict(self, horizon: int = 7, future_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Generates predictions.
        """
        if self.model_type == 'rf':
            return self._predict_rf(future_df)
        elif self.model_type == 'prophet':
            return self._predict_prophet(horizon)
        else:
            return pd.DataFrame()

    def _train_rf(self, df: pd.DataFrame, target: str, features: list):
        if not features:
            logging.error("Features list required for RF.")
            return

        X = df[features]
        y = df[target]
        
        # Simple shift for next day prediction (very basic)
        # In reality, we'd predict return or use a multi-step approach
        # Here we shift target back by 1 to predict 'next day close' using 'today features'
        y = y.shift(-1)
        X = X[:-1]
        y = y.dropna()
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        preds = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        logging.info(f"RF Model Trained. MAE: {mae:.4f}")
        
    def _predict_rf(self, future_df: pd.DataFrame):
        if not self.model:
            logging.error("Model not trained.")
            return pd.Series()
        return self.model.predict(future_df)

    def _train_prophet(self, df: pd.DataFrame):
        if not PROPHET_AVAILABLE:
            logging.error("Prophet not available.")
            return
            
        # Prophet requires 'ds' and 'y'
        if 'Date' in df.columns:
            df_prophet = df.rename(columns={'Date': 'ds', 'Close': 'y'})
        else:
            # Assuming index is date
            df_prophet = df.reset_index().rename(columns={'index': 'ds', 'Close': 'y'})
            
        self.model = Prophet()
        self.model.fit(df_prophet)
        logging.info("Prophet Model Trained.")

    def _predict_prophet(self, horizon: int):
        if not self.model:
            return pd.DataFrame()
            
        future = self.model.make_future_dataframe(periods=horizon)
        forecast = self.model.predict(future)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(horizon)
