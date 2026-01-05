import os
import logging
from dotenv import load_dotenv
import pandas as pd

from src.data.ingestion import fetch_stock_data, fetch_fundamentals
from src.features.indicators import add_technical_indicators
from src.features.preprocessing import clean_data
from src.models.forecaster import Forecaster
from src.models.signals import generate_signals
from src.llm.explainer import generate_insight
from src.reporting.generator import save_signal_output, generate_markdown_report

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

def run_pipeline(ticker: str):
    logging.info(f"--- Starting Pipeline for {ticker} ---")
    
    # 1. Data Ingestion
    logging.info("1. Ingestion")
    df = fetch_stock_data(ticker, period="2y", interval="1d")
    if df.empty:
        logging.error("No data fetched. Aborting.")
        return
        
    # 2. Feature Engineering
    logging.info("2. Feature Engineering")
    df = add_technical_indicators(df)
    df = clean_data(df)
    
    # Define features for model
    features = ['Close', 'RSI', 'MACD', 'SMA_20', 'SMA_50']
    # Ensure all features exist
    missing = [f for f in features if f not in df.columns]
    if missing:
        logging.error(f"Missing features: {missing}. Aborting.")
        return

    # 3. Modeling
    logging.info("3. Modeling")
    forecaster = Forecaster(model_type='rf')
    forecaster.train(df, target='Close', features=features)
    
    # Predict next step (naive: use last available row as 'today' to predict 'tomorrow')
    # In real pipeline, we might fetch live data separately or use the last row
    last_row = df.iloc[[-1]][features] # Use double bracket to keep DataFrame
    prediction_series = forecaster.predict(future_df=last_row)
    
    if len(prediction_series) == 0:
        logging.error("Prediction failed.")
        return
        
    predicted_price = prediction_series[0]
    current_price = df.iloc[-1]['Close']
    logging.info(f"Current: {current_price}, Predicted: {predicted_price}")

    # 4. Signal Generation
    logging.info("4. Signal Generation")
    # Get latest indicators
    last_indicators = df.iloc[-1][['RSI', 'MACD']].to_dict()
    signal_data = generate_signals(current_price, predicted_price, indicators=last_indicators)
    logging.info(f"Signal: {signal_data}")

    # 5. LLM Insights
    logging.info("5. LLM Analysis")
    insight = generate_insight(ticker, signal_data, last_indicators)
    
    # 6. Reporting
    logging.info("6. Reporting")
    save_signal_output(signal_data, f"{ticker}_signal.json")
    report_path = generate_markdown_report(ticker, signal_data, insight, f"{ticker}_report.md")
    
    logging.info(f"Pipeline completed. Report at: {report_path}")

def main():
    ticker = "AAPL" # Default for now, can be arg
    run_pipeline(ticker)

if __name__ == "__main__":
    main()
