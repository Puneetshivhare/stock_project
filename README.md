# Automated Financial Intelligence & Trading Insights System

**Project Title:** Automated Financial Intelligence & Trading Insights System

## Objective
Build an automated end-to-end pipeline that ingests market and fundamental financial data, generates ML-based buy/sell/hold signals, and uses LLMs to create human-readable market insights, explanations, and confidence assessments.

## Core Components
* **Automated Data Ingestion**: Market pricing (Yahoo Finance) + Fundamentals.
* **Feature Engineering**: computation of technical indicators (RSI, SMA, MACD, Volatility).
* **ML Modeling**: Time-series forecasting (Prophet, ARIMA, RandomForest).
* **Signal Generation**: Logic-based Buy/Sell/Hold signals derived from forecasts.
* **LLM Analysis**: Automated reporting, interpretation, and confidence scoring.

## Pipeline Overview
1. **Ingest**: Fetch price, fundamentals, indicators.
2. **Process**: Compute features and prepare datasets.
3. **Model**: Train/apply forecasting models.
4. **Signal**: Generate structured signals and model confidence.
5. **Explain**: Use LLM to explain signals, summarize trends, and highlight risks.
6. **Report**: Output JSON and Markdown/HTML dashboard.

## Getting Started

### Prerequisites
- Python 3.10+
- API Key for LLM provider (e.g., OpenAI, Anthropic)

### Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (copy `.env.example` to `.env`).

### Usage
Run the main pipeline:
```bash
python main.py
```
