"""
Financial Intelligence Pipeline — Streamlit Entry Point
Multi-page app with sidebar market switcher.
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# ── Page Config ────────────────────────────────────────────
st.set_page_config(
    page_title="Commodity Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0E1117 0%, #1A1D23 50%, #0E1117 100%);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1D23 0%, #13151A 100%);
        border-right: 1px solid rgba(255, 215, 0, 0.1);
    }

    /* Market switcher highlight */
    .market-header {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(192, 192, 192, 0.05));
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px;
        transition: transform 0.2s;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 215, 0, 0.3);
    }

    /* Gold accent */
    .gold-accent { color: #FFD700; }
    .silver-accent { color: #C0C0C0; }
    .copper-accent { color: #B87333; }

    /* Signal badges */
    .signal-buy {
        background: rgba(0, 200, 83, 0.15);
        color: #00C853;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    .signal-sell {
        background: rgba(255, 23, 68, 0.15);
        color: #FF1744;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    .signal-hold {
        background: rgba(255, 193, 7, 0.15);
        color: #FFC107;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #1A1D23; }
    ::-webkit-scrollbar-thumb { background: #FFD700; border-radius: 3px; }

    /* Header */
    .main-header {
        text-align: center;
        padding: 10px 0;
        margin-bottom: 20px;
    }
    .main-header h1 {
        background: linear-gradient(135deg, #FFD700, #FFA000, #C0C0C0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: 700;
    }

    /* Hide streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Market Configuration ───────────────────────────────────
MARKET_OPTIONS = {
    "🇮🇳 India (MCX)": "india",
    "🇺🇸 US (COMEX)": "us",
    "🇨🇳 China (SHFE)": "china",
}

MARKET_INFO = {
    "india": {"flag": "🇮🇳", "currency": "INR", "symbol": "₹"},
    "us": {"flag": "🇺🇸", "currency": "USD", "symbol": "$"},
    "china": {"flag": "🇨🇳", "currency": "CNY", "symbol": "¥"},
}

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="market-header">
        <h2 style="margin:0; color: #FFD700;">📊 Commodity Intel</h2>
        <p style="margin:0; color: #888; font-size: 0.85rem;">Multi-Market Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # Market Switcher
    st.markdown("#### 🌍 Select Market")
    selected_market_label = st.selectbox(
        "Market",
        options=list(MARKET_OPTIONS.keys()),
        index=0,
        label_visibility="collapsed",
    )
    selected_market = MARKET_OPTIONS[selected_market_label]
    st.session_state["market"] = selected_market

    market_info = MARKET_INFO[selected_market]
    st.markdown(
        f"**Active:** {market_info['flag']} {market_info['currency']} ({market_info['symbol']})"
    )

    st.divider()

    # Navigation info
    st.markdown("""
    **Pages:**
    - 📈 **Dashboard** — Prices & Charts
    - 🔮 **Predictions** — ML Forecasts
    - 🎯 **Signals** — Buy/Sell/Hold
    - 📝 **Reports** — LLM Analysis
    """)

    st.divider()
    st.caption("Built with FastAPI + Prophet + Gemini")


# ── Main Page ──────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>⚡ Commodity Intelligence Pipeline</h1>
    <p style="color: #888;">Gold · Silver · Copper — India · US · China</p>
</div>
""", unsafe_allow_html=True)

st.info(
    f"📍 **Active Market: {selected_market_label}** — "
    f"Select a page from the sidebar to explore prices, predictions, signals, and reports."
)

# Quick overview
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    ### 🥇 Gold
    The traditional safe-haven asset. Track live prices,
    forecasts, and trading signals.
    """)
with col2:
    st.markdown("""
    ### 🥈 Silver
    Industrial and precious metal with high volatility.
    ML-powered predictions available.
    """)
with col3:
    st.markdown("""
    ### 🥉 Copper
    Key industrial metal and economic indicator.
    Cross-market analysis supported.
    """)

st.divider()

st.markdown("""
### 🚀 Getting Started
1. **Select your market** from the sidebar (India, US, or China)
2. Navigate to **Dashboard** for live prices and technical charts
3. Check **Predictions** for 1-day, 7-day, and 30-day forecasts
4. Review **Signals** for buy/sell/hold recommendations
5. Read **Reports** for AI-generated market analysis
""")
