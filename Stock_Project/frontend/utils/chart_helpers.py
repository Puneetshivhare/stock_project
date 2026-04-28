"""
Plotly chart helper functions — consistent dark theme with commodity accent colors.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Any, Optional

# ── Theme Colors ──────────────────────────────────────────
COLORS = {
    "gold": "#FFD700",
    "silver": "#C0C0C0",
    "copper": "#B87333",
    "bg": "#0E1117",
    "paper": "#1A1D23",
    "grid": "#2D3139",
    "text": "#FAFAFA",
    "green": "#00C853",
    "red": "#FF1744",
    "blue": "#2979FF",
}

LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    paper_bgcolor=COLORS["paper"],
    plot_bgcolor=COLORS["bg"],
    font=dict(family="Inter, sans-serif", color=COLORS["text"]),
    xaxis=dict(gridcolor=COLORS["grid"], showgrid=True),
    yaxis=dict(gridcolor=COLORS["grid"], showgrid=True),
    margin=dict(l=50, r=30, t=50, b=40),
    hovermode="x unified",
)


def create_candlestick_chart(
    data: List[Dict[str, Any]],
    commodity: str = "gold",
    currency_symbol: str = "$",
    show_volume: bool = True,
    show_sma: bool = True,
) -> go.Figure:
    """Create a candlestick chart with optional volume and SMA overlays."""
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])

    rows = 2 if show_volume else 1
    row_heights = [0.75, 0.25] if show_volume else [1]
    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=row_heights,
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df["date"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            increasing_line_color=COLORS["green"],
            decreasing_line_color=COLORS["red"],
            name="Price",
        ),
        row=1, col=1,
    )

    # SMA overlays
    if show_sma and "sma_20" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["date"], y=df["sma_20"],
                line=dict(color=COLORS["blue"], width=1),
                name="SMA 20", opacity=0.7,
            ),
            row=1, col=1,
        )
    if show_sma and "sma_50" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["date"], y=df["sma_50"],
                line=dict(color="#FF9800", width=1),
                name="SMA 50", opacity=0.7,
            ),
            row=1, col=1,
        )

    # Volume bars
    if show_volume and "volume" in df.columns:
        colors = [
            COLORS["green"] if c >= o else COLORS["red"]
            for c, o in zip(df["close"], df["open"])
        ]
        fig.add_trace(
            go.Bar(
                x=df["date"], y=df["volume"],
                marker_color=colors, name="Volume", opacity=0.5,
            ),
            row=2, col=1,
        )

    color = COLORS.get(commodity, COLORS["gold"])
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=f"{commodity.title()} — {currency_symbol} Price",
        xaxis_rangeslider_visible=False,
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def create_rsi_chart(data: List[Dict[str, Any]], commodity: str = "gold") -> go.Figure:
    """Create RSI indicator chart."""
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])

    fig = go.Figure()

    if "rsi" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["rsi"],
            line=dict(color=COLORS.get(commodity, COLORS["gold"]), width=2),
            name="RSI (14)",
        ))

        # Overbought / Oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color=COLORS["red"], opacity=0.5,
                      annotation_text="Overbought (70)")
        fig.add_hline(y=30, line_dash="dash", line_color=COLORS["green"], opacity=0.5,
                      annotation_text="Oversold (30)")
        fig.add_hline(y=50, line_dash="dot", line_color=COLORS["text"], opacity=0.3)

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title="RSI (14)",
        yaxis=dict(range=[0, 100], gridcolor=COLORS["grid"]),
        height=200,
        showlegend=False,
    )

    return fig


def create_macd_chart(data: List[Dict[str, Any]], commodity: str = "gold") -> go.Figure:
    """Create MACD indicator chart."""
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])

    fig = go.Figure()

    if "macd" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["macd"],
            line=dict(color=COLORS["blue"], width=1.5),
            name="MACD",
        ))
    if "macd_signal" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["macd_signal"],
            line=dict(color="#FF9800", width=1.5),
            name="Signal",
        ))
    if "macd_hist" in df.columns:
        colors = [COLORS["green"] if v >= 0 else COLORS["red"] for v in df["macd_hist"]]
        fig.add_trace(go.Bar(
            x=df["date"], y=df["macd_hist"],
            marker_color=colors, name="Histogram", opacity=0.5,
        ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title="MACD (12, 26, 9)",
        height=200,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def create_forecast_chart(
    historical: List[Dict[str, Any]],
    predictions: List[Dict[str, Any]],
    commodity: str = "gold",
    currency_symbol: str = "$",
) -> go.Figure:
    """Create forecast chart with confidence bands."""
    fig = go.Figure()

    # Historical prices (last 60 days)
    hist_df = pd.DataFrame(historical[-60:])
    hist_df["date"] = pd.to_datetime(hist_df["date"])

    fig.add_trace(go.Scatter(
        x=hist_df["date"], y=hist_df["close"],
        line=dict(color=COLORS.get(commodity, COLORS["gold"]), width=2),
        name="Actual Price",
    ))

    # Predictions
    if predictions:
        pred_df = pd.DataFrame(predictions)
        pred_df["date"] = pd.to_datetime(pred_df["date"])

        # Connect last actual point to first prediction
        bridge_date = hist_df["date"].iloc[-1]
        bridge_price = hist_df["close"].iloc[-1]

        dates = pd.concat([pd.Series([bridge_date]), pred_df["date"]])
        predicted = pd.concat([pd.Series([bridge_price]), pred_df["predicted"]])
        lower = pd.concat([pd.Series([bridge_price]), pred_df["lower"]])
        upper = pd.concat([pd.Series([bridge_price]), pred_df["upper"]])

        # Confidence band
        fig.add_trace(go.Scatter(
            x=pd.concat([dates, dates[::-1]]),
            y=pd.concat([upper, lower[::-1]]),
            fill="toself",
            fillcolor="rgba(41, 121, 255, 0.15)",
            line=dict(color="rgba(255,255,255,0)"),
            name="90% Confidence",
            hoverinfo="skip",
        ))

        # Prediction line
        fig.add_trace(go.Scatter(
            x=dates, y=predicted,
            line=dict(color=COLORS["blue"], width=2, dash="dot"),
            name="Forecast",
        ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=f"{commodity.title()} — Forecast ({currency_symbol})",
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def create_signal_gauge(signal: str, strength: int, commodity: str = "gold") -> go.Figure:
    """Create a gauge chart for signal strength."""
    color_map = {"BUY": COLORS["green"], "SELL": COLORS["red"], "HOLD": "#FFC107"}
    bar_color = color_map.get(signal, "#FFC107")

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=strength,
        title={"text": f"{commodity.title()} — {signal}", "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": bar_color},
            "bgcolor": COLORS["bg"],
            "steps": [
                {"range": [0, 33], "color": "rgba(255, 23, 68, 0.2)"},
                {"range": [33, 66], "color": "rgba(255, 193, 7, 0.2)"},
                {"range": [66, 100], "color": "rgba(0, 200, 83, 0.2)"},
            ],
        },
    ))

    fig.update_layout(
        paper_bgcolor=COLORS["paper"],
        font=dict(color=COLORS["text"], family="Inter, sans-serif"),
        height=250,
        margin=dict(l=20, r=20, t=60, b=20),
    )

    return fig
