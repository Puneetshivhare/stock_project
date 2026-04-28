"""
Signals Page — Buy/Sell/Hold recommendations with gauges and reasoning.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from frontend.utils.api_client import get_all_signals, get_confidence
from frontend.utils.chart_helpers import create_signal_gauge

st.set_page_config(page_title="Signals", page_icon="🎯", layout="wide")

# ── Market ────────────────────────────────────────────────
market = st.session_state.get("market", "india")
MARKET_LABELS = {"india": "🇮🇳 India (MCX)", "us": "🇺🇸 US (COMEX)", "china": "🇨🇳 China (SHFE)"}

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 Signal Controls")

    selected_market_label = st.selectbox(
        "🌍 Market",
        options=list(MARKET_LABELS.values()),
        index=list(MARKET_LABELS.keys()).index(market),
        key="sig_market",
    )
    market = [k for k, v in MARKET_LABELS.items() if v == selected_market_label][0]
    st.session_state["market"] = market

    horizon = st.radio(
        "📅 Signal Horizon",
        options=[1, 7, 30],
        format_func=lambda x: {1: "1 Day", 7: "7 Days", 30: "30 Days"}[x],
        index=1,
        horizontal=True,
        key="sig_horizon",
    )

# ── Header ────────────────────────────────────────────────
st.markdown(f"# 🎯 Trading Signals — {selected_market_label}")
st.markdown(f"**{horizon}-Day Signal Horizon**")

# ── Fetch All Signals ─────────────────────────────────────
with st.spinner("Calculating signals..."):
    result = get_all_signals(market, horizon)

signals = result.get("signals", {})

if signals:
    # Signal Gauges
    cols = st.columns(3)
    commodity_order = ["gold", "silver", "copper"]

    for i, commodity in enumerate(commodity_order):
        sig_data = signals.get(commodity, {})
        if "error" in sig_data:
            with cols[i]:
                st.error(f"{commodity.title()}: {sig_data['error']}")
            continue

        signal = sig_data.get("signal", "HOLD")
        strength = sig_data.get("strength", 50)
        current_price = sig_data.get("current_price", 0)
        sym = sig_data.get("symbol", "$")

        with cols[i]:
            # Signal gauge
            fig = create_signal_gauge(signal, strength, commodity)
            st.plotly_chart(fig, use_container_width=True)

            # Price
            st.markdown(f"**Price:** {sym}{current_price:,.2f}")

    st.divider()

    # Detailed Signal Breakdown
    st.markdown("### 📋 Signal Breakdown")

    for commodity in commodity_order:
        sig_data = signals.get(commodity, {})
        if "error" in sig_data:
            continue

        signal = sig_data.get("signal", "HOLD")
        signal_class = f"signal-{signal.lower()}"
        name = sig_data.get("commodity_name", commodity.title())
        icon = {"gold": "🥇", "silver": "🥈", "copper": "🥉"}.get(commodity, "💰")

        with st.expander(f"{icon} {name} — {signal}", expanded=True):
            # Technical signals
            tech = sig_data.get("technical_signals", {})

            t_cols = st.columns(4)
            tech_items = [
                ("RSI", tech.get("rsi", {})),
                ("MACD", tech.get("macd", {})),
                ("SMA", tech.get("sma", {})),
                ("Forecast", tech.get("forecast", {})),
            ]

            for col, (label, item) in zip(t_cols, tech_items):
                with col:
                    sig_val = item.get("signal", "HOLD")
                    color = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(sig_val, "⚪")
                    st.markdown(f"**{label}:** {color} {sig_val}")
                    st.caption(item.get("reason", ""))

            # Reasons summary
            reasons = sig_data.get("reasons", [])
            if reasons:
                st.markdown("**All Factors:**")
                for reason in reasons:
                    st.markdown(f"- {reason}")

    # Cross-Market Comparison (if desired)
    st.divider()
    st.markdown("### 🌍 Cross-Market Signal Comparison")
    st.info("Compare the same commodity across India, US, and China markets.")

    compare_commodity = st.selectbox(
        "Select Commodity to Compare",
        options=["gold", "silver", "copper"],
        format_func=lambda x: x.title(),
        key="compare_commodity",
    )

    compare_cols = st.columns(3)
    for i, (mkt_key, mkt_label) in enumerate(MARKET_LABELS.items()):
        with compare_cols[i]:
            st.markdown(f"**{mkt_label}**")
            if mkt_key == market and compare_commodity in signals:
                sig = signals[compare_commodity]
                signal_val = sig.get("signal", "N/A")
                color = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal_val, "⚪")
                st.markdown(f"Signal: {color} **{signal_val}** (Strength: {sig.get('strength', 'N/A')})")
            else:
                try:
                    other_result = get_all_signals(mkt_key, horizon)
                    other_sig = other_result.get("signals", {}).get(compare_commodity, {})
                    if "signal" in other_sig:
                        color = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(other_sig["signal"], "⚪")
                        st.markdown(f"Signal: {color} **{other_sig['signal']}** (Strength: {other_sig.get('strength', 'N/A')})")
                    else:
                        st.markdown("Signal: ⚪ N/A")
                except Exception:
                    st.markdown("Signal: ⚪ N/A")

    # LLM Confidence
    st.divider()
    st.markdown("### 🤖 AI Confidence Score")
    confidence_commodity = st.selectbox(
        "Select Commodity",
        options=["gold", "silver", "copper"],
        format_func=lambda x: x.title(),
        key="confidence_commodity",
    )

    if st.button("Get AI Confidence Score", use_container_width=True):
        with st.spinner("Calculating confidence..."):
            conf = get_confidence(confidence_commodity, market, horizon)
            if conf and "confidence" in conf:
                c = conf["confidence"]
                score = c.get("confidence_score", 50)
                level = c.get("confidence_level", "MEDIUM")

                level_color = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(level, "⚪")

                st.markdown(f"### {level_color} Confidence: **{score}/100** ({level})")

                if c.get("positive_factors"):
                    st.markdown("**✅ Positive Factors:**")
                    for f in c["positive_factors"]:
                        st.markdown(f"- {f}")

                if c.get("risk_factors"):
                    st.markdown("**⚠️ Risk Factors:**")
                    for f in c["risk_factors"]:
                        st.markdown(f"- {f}")

                if c.get("summary"):
                    st.info(c["summary"])
            else:
                st.warning("Could not get confidence score. Check Gemini API key.")

else:
    st.warning("No signal data available. Make sure data is ingested from the Dashboard.")
