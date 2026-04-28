"""
Dashboard Page — Live prices, candlestick charts, technical indicators, news.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from frontend.utils.api_client import get_latest_prices, get_price_history, get_news, refresh_data
from frontend.utils.chart_helpers import create_candlestick_chart, create_rsi_chart, create_macd_chart

st.set_page_config(page_title="Dashboard", page_icon="📈", layout="wide")

# ── Get Market from Session ────────────────────────────────
market = st.session_state.get("market", "india")

MARKET_LABELS = {"india": "🇮🇳 India (MCX)", "us": "🇺🇸 US (COMEX)", "china": "🇨🇳 China (SHFE)"}

# ── Sidebar Controls ──────────────────────────────────────
with st.sidebar:
    st.markdown("### 📈 Dashboard Controls")

    selected_market_label = st.selectbox(
        "🌍 Market",
        options=list(MARKET_LABELS.values()),
        index=list(MARKET_LABELS.keys()).index(market),
    )
    market = [k for k, v in MARKET_LABELS.items() if v == selected_market_label][0]
    st.session_state["market"] = market

    commodity = st.selectbox(
        "🪙 Commodity",
        options=["gold", "silver", "copper"],
        format_func=lambda x: {"gold": "🥇 Gold", "silver": "🥈 Silver", "copper": "🥉 Copper"}[x],
    )

    timeframe = st.selectbox(
        "📅 Timeframe",
        options=[60, 120, 250, 500, 1000],
        format_func=lambda x: {60: "3 Months", 120: "6 Months", 250: "1 Year", 500: "2 Years", 1000: "5 Years"}[x],
        index=2,
    )

    show_volume = st.checkbox("Show Volume", value=True)
    show_sma = st.checkbox("Show SMA (20/50)", value=True)

    if st.button("🔄 Refresh Data", use_container_width=True):
        with st.spinner("Refreshing..."):
            result = refresh_data(market)
            if result:
                st.success("Data refreshed!")
            else:
                st.error("Refresh failed")

# ── Header ────────────────────────────────────────────────
st.markdown(f"# 📈 Dashboard — {selected_market_label}")

# ── Price Metrics ─────────────────────────────────────────
latest = get_latest_prices(market)
prices = latest.get("prices", [])
symbol = latest.get("symbol", "$")

if prices:
    cols = st.columns(len(prices))
    commodity_icons = {"gold": "🥇", "silver": "🥈", "copper": "🥉"}

    for i, price in enumerate(prices):
        with cols[i]:
            name = price.get("commodity", "").title()
            close = price.get("close", 0)
            icon = commodity_icons.get(price.get("commodity"), "💰")

            st.metric(
                label=f"{icon} {name}",
                value=f"{symbol}{close:,.2f}",
                delta=f"RSI: {price.get('rsi', 'N/A'):.1f}" if price.get('rsi') else "N/A",
            )
else:
    st.warning("⚠️ No price data available. Click 'Refresh Data' in the sidebar.")

# ── Candlestick Chart ─────────────────────────────────────
st.markdown(f"### {'🥇' if commodity == 'gold' else '🥈' if commodity == 'silver' else '🥉'} {commodity.title()} Price Chart")

history = get_price_history(commodity, market, timeframe)
data = history.get("data", [])

if data:
    fig = create_candlestick_chart(
        data, commodity, symbol,
        show_volume=show_volume, show_sma=show_sma,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Technical Indicator Panels
    col1, col2 = st.columns(2)
    with col1:
        rsi_fig = create_rsi_chart(data, commodity)
        st.plotly_chart(rsi_fig, use_container_width=True)
    with col2:
        macd_fig = create_macd_chart(data, commodity)
        st.plotly_chart(macd_fig, use_container_width=True)

    # Key Stats
    st.markdown("### 📊 Key Statistics")
    last = data[-1] if data else {}
    stat_cols = st.columns(6)
    stats = [
        ("Close", f"{symbol}{last.get('close', 0):,.2f}"),
        ("High", f"{symbol}{last.get('high', 0):,.2f}"),
        ("Low", f"{symbol}{last.get('low', 0):,.2f}"),
        ("RSI", f"{last.get('rsi', 'N/A'):.1f}" if last.get('rsi') else "N/A"),
        ("MACD", f"{last.get('macd', 'N/A'):.2f}" if last.get('macd') else "N/A"),
        ("Volume", f"{last.get('volume', 0):,.0f}"),
    ]
    for col, (label, value) in zip(stat_cols, stats):
        with col:
            st.metric(label, value)
else:
    st.warning("No historical data. Please refresh data from the sidebar.")

# ── News Feed ─────────────────────────────────────────────
st.markdown("### 📰 Latest News")
news_data = get_news(market, limit=10)
articles = news_data.get("articles", [])

if articles:
    for article in articles[:8]:
        title = article.get("title", "Untitled")
        source = article.get("source", "")
        url = article.get("url", "")
        date = article.get("date", "")

        if url:
            st.markdown(f"- [{title}]({url}) — *{source}* ({date})")
        else:
            st.markdown(f"- **{title}** — *{source}* ({date})")
else:
    st.info("No news articles available. Data will load on next refresh.")
