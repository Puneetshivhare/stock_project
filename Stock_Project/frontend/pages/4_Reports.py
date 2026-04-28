"""
Reports Page — LLM-generated market analysis and commodity deep-dives.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from frontend.utils.api_client import get_daily_report, get_commodity_analysis

st.set_page_config(page_title="Reports", page_icon="📝", layout="wide")

# ── Market ────────────────────────────────────────────────
market = st.session_state.get("market", "india")
MARKET_LABELS = {"india": "🇮🇳 India (MCX)", "us": "🇺🇸 US (COMEX)", "china": "🇨🇳 China (SHFE)"}

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📝 Report Controls")

    selected_market_label = st.selectbox(
        "🌍 Market",
        options=list(MARKET_LABELS.values()),
        index=list(MARKET_LABELS.keys()).index(market),
        key="rpt_market",
    )
    market = [k for k, v in MARKET_LABELS.items() if v == selected_market_label][0]
    st.session_state["market"] = market

# ── Header ────────────────────────────────────────────────
st.markdown(f"# 📝 Market Reports — {selected_market_label}")

# ── Tabs ──────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Daily Summary", "🔍 Commodity Deep Dive", "🌍 Compare Markets"])

# ── Tab 1: Daily Summary ─────────────────────────────────
with tab1:
    st.markdown("### 📊 Daily Market Review")
    st.markdown("*AI-generated comprehensive market analysis*")

    if st.button("📝 Generate Daily Report", use_container_width=True, key="daily_btn"):
        with st.spinner("Generating daily market summary... (this may take 10-20 seconds)"):
            report = get_daily_report(market)
            if report and "report" in report:
                st.markdown(report["report"])
            else:
                st.warning("Could not generate report. Check if Gemini API key is configured.")
    else:
        st.info("Click the button above to generate a fresh daily market summary.")

# ── Tab 2: Commodity Deep Dive ───────────────────────────
with tab2:
    st.markdown("### 🔍 Commodity Analysis")

    commodity = st.selectbox(
        "Select Commodity",
        options=["gold", "silver", "copper"],
        format_func=lambda x: {"gold": "🥇 Gold", "silver": "🥈 Silver", "copper": "🥉 Copper"}[x],
        key="report_commodity",
    )

    if st.button(f"📝 Analyze {commodity.title()}", use_container_width=True, key="analysis_btn"):
        with st.spinner(f"Generating {commodity.title()} analysis..."):
            analysis = get_commodity_analysis(commodity, market)
            if analysis and "analysis" in analysis:
                st.markdown(analysis["analysis"])
            else:
                st.warning("Could not generate analysis. Check API key and data availability.")
    else:
        st.info(f"Select a commodity and click the button to get a detailed AI analysis.")

# ── Tab 3: Compare Markets ───────────────────────────────
with tab3:
    st.markdown("### 🌍 Cross-Market Analysis")
    st.markdown("Compare the same commodity across India, US, and China.")

    compare_commodity = st.selectbox(
        "Commodity to Compare",
        options=["gold", "silver", "copper"],
        format_func=lambda x: x.title(),
        key="compare_report_commodity",
    )

    if st.button("📝 Generate Cross-Market Report", use_container_width=True, key="compare_btn"):
        cols = st.columns(3)
        for i, (mkt_key, mkt_label) in enumerate(MARKET_LABELS.items()):
            with cols[i]:
                st.markdown(f"#### {mkt_label}")
                with st.spinner(f"Analyzing {mkt_label}..."):
                    analysis = get_commodity_analysis(compare_commodity, mkt_key)
                    if analysis and "analysis" in analysis:
                        st.markdown(analysis["analysis"])
                    else:
                        st.info("Data not available for this market yet.")
    else:
        st.info("Generate side-by-side analyses of a commodity across all 3 markets.")

# ── Disclaimer ────────────────────────────────────────────
st.divider()
st.caption(
    "⚠️ **Disclaimer:** These reports are AI-generated for informational purposes only. "
    "They do not constitute financial advice. Always conduct your own research "
    "before making trading decisions."
)
