"""
Predictions Page — ML forecasts with confidence intervals and LLM explanations.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from frontend.utils.api_client import (
    get_prediction, get_price_history, get_prediction_explanation
)
from frontend.utils.chart_helpers import create_forecast_chart

st.set_page_config(page_title="Predictions", page_icon="🔮", layout="wide")

# ── Market ────────────────────────────────────────────────
market = st.session_state.get("market", "india")
MARKET_LABELS = {"india": "🇮🇳 India (MCX)", "us": "🇺🇸 US (COMEX)", "china": "🇨🇳 China (SHFE)"}

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔮 Prediction Controls")

    selected_market_label = st.selectbox(
        "🌍 Market",
        options=list(MARKET_LABELS.values()),
        index=list(MARKET_LABELS.keys()).index(market),
        key="pred_market",
    )
    market = [k for k, v in MARKET_LABELS.items() if v == selected_market_label][0]
    st.session_state["market"] = market

    commodity = st.selectbox(
        "🪙 Commodity",
        options=["gold", "silver", "copper"],
        format_func=lambda x: {"gold": "🥇 Gold", "silver": "🥈 Silver", "copper": "🥉 Copper"}[x],
        key="pred_commodity",
    )

    horizon = st.radio(
        "📅 Forecast Horizon",
        options=[1, 7, 30],
        format_func=lambda x: {1: "1 Day", 7: "7 Days", 30: "30 Days"}[x],
        index=1,
        horizontal=True,
    )

# ── Header ────────────────────────────────────────────────
st.markdown(f"# 🔮 Predictions — {selected_market_label}")
st.markdown(f"**{commodity.title()}** | **{horizon}-Day Forecast**")

# ── Fetch Prediction ──────────────────────────────────────
with st.spinner(f"Generating {horizon}-day forecast for {commodity.title()}..."):
    prediction = get_prediction(commodity, market, horizon)

if prediction and "predictions" in prediction:
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    currency_sym = prediction.get("currency", "USD")
    symbol_map = {"INR": "₹", "USD": "$", "CNY": "¥"}
    sym = symbol_map.get(currency_sym, "$")

    current = prediction.get("current_price", 0)
    direction = prediction.get("direction", "FLAT")
    pct_change = prediction.get("pct_change", 0)
    metrics = prediction.get("model_metrics", {})

    with col1:
        st.metric("Current Price", f"{sym}{current:,.2f}")
    with col2:
        direction_icon = "🟢" if direction == "UP" else ("🔴" if direction == "DOWN" else "🟡")
        st.metric("Direction", f"{direction_icon} {direction}")
    with col3:
        st.metric("Predicted Change", f"{pct_change:+.2f}%",
                   delta=f"{pct_change:+.2f}%")
    with col4:
        mape = metrics.get("mape", "N/A")
        st.metric("Model MAPE", f"{mape}%")

    st.divider()

    # Forecast Chart
    st.markdown("### 📊 Forecast Chart")
    history = get_price_history(commodity, market, 120)
    hist_data = history.get("data", [])

    if hist_data:
        fig = create_forecast_chart(
            hist_data,
            prediction.get("predictions", []),
            commodity, sym,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Prediction Table
    st.markdown("### 📋 Prediction Details")
    predictions_list = prediction.get("predictions", [])
    if predictions_list:
        import pandas as pd
        pred_df = pd.DataFrame(predictions_list)
        pred_df.columns = ["Date", f"Predicted ({sym})", f"Lower Bound ({sym})", f"Upper Bound ({sym})"]
        st.dataframe(pred_df, use_container_width=True, hide_index=True)

    # Model Metrics
    st.markdown("### 📐 Model Accuracy")
    m_cols = st.columns(3)
    with m_cols[0]:
        st.metric("MAE", f"{sym}{metrics.get('mae', 'N/A')}")
    with m_cols[1]:
        st.metric("RMSE", f"{sym}{metrics.get('rmse', 'N/A')}")
    with m_cols[2]:
        st.metric("MAPE", f"{metrics.get('mape', 'N/A')}%")

    # LLM Explanation
    st.divider()
    st.markdown("### 🤖 AI Analysis")
    if st.button("Generate AI Explanation", use_container_width=True):
        with st.spinner("Generating AI analysis..."):
            explanation = get_prediction_explanation(commodity, market, horizon)
            if explanation and "explanation" in explanation:
                st.markdown(explanation["explanation"])
            else:
                st.warning("Could not generate explanation. Check if Gemini API key is configured.")

elif prediction and "error" in prediction:
    st.error(f"Prediction error: {prediction['error']}")
    st.info("Try refreshing data from the Dashboard page first.")
else:
    st.warning("No prediction data available. Make sure the backend has ingested data.")
    st.info("Go to the Dashboard page and click 'Refresh Data'.")
