"""
charts.py
---------
Builds every Plotly figure used in the dashboard:
  1. Sales Trend (smooth line, year filter, peak/low highlights, avg line)
  2. Monthly Sales Comparison (conditional colour bars)
  3. Quarterly Sales (quarter-wise totals)
  4. Month-over-Month Growth %
  5. Forecast (next month, based on trailing 3-month average)

Every function returns a ready-to-render `go.Figure` with a shared
corporate style (white background, minimal margins, Kores blue palette).
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Shared palette / layout helpers
# ---------------------------------------------------------------------------
NAVY = "#0A2E5C"
BLUE = "#0056A6"
ACCENT = "#1E88E5"
LIGHT_BLUE = "#CFE2FA"
GREEN = "#1E8E3E"
RED = "#D93025"
GREY = "#5F6368"
BG = "#FFFFFF"

BASE_LAYOUT = dict(
    plot_bgcolor=BG,
    paper_bgcolor=BG,
    font=dict(family="Segoe UI, Arial", color=NAVY, size=12),
    margin=dict(l=36, r=24, t=18, b=36),
    hoverlabel=dict(bgcolor="white", font_size=12, font_family="Segoe UI"),
    legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1.0,
                font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
)

AXIS_STYLE = dict(
    showgrid=True, gridcolor="#EEF2F7", gridwidth=1,
    zeroline=False, showline=True, linecolor="#D9E2EC",
    tickfont=dict(size=11, color=GREY),
)


def _apply_layout(fig: go.Figure, height: int = 300) -> go.Figure:
    fig.update_layout(**BASE_LAYOUT, height=height)
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)
    return fig


# ---------------------------------------------------------------------------
# 1. Sales Trend
# ---------------------------------------------------------------------------
def sales_trend_chart(monthly_df: pd.DataFrame, selected_year=None) -> go.Figure:
    """Smooth sales trend line with peak/low highlights and an average line."""
    data = monthly_df.copy()
    if selected_year and selected_year != "All Years":
        data = data[data["Year"] == selected_year]
    data = data.sort_values("SortKey").reset_index(drop=True)

    fig = go.Figure()

    if data.empty:
        fig.add_annotation(text="No data available for the selected year",
                            showarrow=False, font=dict(color=GREY))
        return _apply_layout(fig, height=340)

    avg_val = data["Sales"].mean()
    max_idx = data["Sales"].idxmax()
    min_idx = data["Sales"].idxmin()

    fig.add_trace(go.Scatter(
        x=data["MonthLabel"], y=data["Sales"],
        mode="lines+markers",
        line=dict(color=BLUE, width=3, shape="spline", smoothing=1.1),
        marker=dict(size=7, color=BLUE, line=dict(width=1, color="white")),
        name="Monthly Sales",
        hovertemplate="<b>%{x}</b><br>Sales: ₹%{y:,.0f}<extra></extra>",
    ))

    # Average reference line
    fig.add_hline(
        y=avg_val, line_dash="dot", line_color=GREY, line_width=1.4,
        annotation_text=f"Average: ₹{avg_val:,.0f}",
        annotation_position="top left",
        annotation_font=dict(size=11, color=GREY),
    )

    # Peak highlight
    fig.add_trace(go.Scatter(
        x=[data.loc[max_idx, "MonthLabel"]], y=[data.loc[max_idx, "Sales"]],
        mode="markers", marker=dict(size=14, color=GREEN, symbol="circle",
                                     line=dict(width=2, color="white")),
        name="Peak", hoverinfo="skip", showlegend=True,
    ))
    fig.add_annotation(
        x=data.loc[max_idx, "MonthLabel"], y=data.loc[max_idx, "Sales"],
        text=f"Peak ₹{data.loc[max_idx,'Sales']:,.0f}", showarrow=True,
        arrowhead=2, arrowcolor=GREEN, ax=0, ay=-32,
        font=dict(size=11, color=GREEN, family="Segoe UI"),
    )

    # Lowest highlight
    fig.add_trace(go.Scatter(
        x=[data.loc[min_idx, "MonthLabel"]], y=[data.loc[min_idx, "Sales"]],
        mode="markers", marker=dict(size=14, color=RED, symbol="circle",
                                     line=dict(width=2, color="white")),
        name="Lowest", hoverinfo="skip", showlegend=True,
    ))
    fig.add_annotation(
        x=data.loc[min_idx, "MonthLabel"], y=data.loc[min_idx, "Sales"],
        text=f"Low ₹{data.loc[min_idx,'Sales']:,.0f}", showarrow=True,
        arrowhead=2, arrowcolor=RED, ax=0, ay=32,
        font=dict(size=11, color=RED, family="Segoe UI"),
    )

    return _apply_layout(fig, height=340)


# ---------------------------------------------------------------------------
# 2. Monthly Sales Comparison (conditional colour bars)
# ---------------------------------------------------------------------------
def monthly_comparison_chart(monthly_df: pd.DataFrame) -> go.Figure:
    data = monthly_df.sort_values("SortKey").reset_index(drop=True)
    fig = go.Figure()

    if data.empty:
        fig.add_annotation(text="No data available", showarrow=False, font=dict(color=GREY))
        return _apply_layout(fig, height=300)

    max_val = data["Sales"].max()
    min_val = data["Sales"].min()

    colors = [
        GREEN if v == max_val else RED if v == min_val else BLUE
        for v in data["Sales"]
    ]

    fig.add_trace(go.Bar(
        x=data["MonthLabel"], y=data["Sales"],
        marker_color=colors, marker_line_width=0,
        text=[f"₹{v:,.0f}" for v in data["Sales"]],
        textposition="outside", textfont=dict(size=10, color=NAVY),
        hovertemplate="<b>%{x}</b><br>Sales: ₹%{y:,.0f}<extra></extra>",
        showlegend=False,
    ))

    fig.update_yaxes(range=[0, max_val * 1.22])
    return _apply_layout(fig, height=300)


# ---------------------------------------------------------------------------
# 3. Quarterly Sales
# ---------------------------------------------------------------------------
def quarterly_sales_chart(monthly_df: pd.DataFrame) -> go.Figure:
    data = (
        monthly_df.groupby(["Year", "Quarter"], as_index=False)
        .agg(Sales=("Sales", "sum"), SortKey=("SortKey", "min"))
        .sort_values("SortKey")
    )
    data["Label"] = data["Quarter"] + " '" + data["Year"].astype(str).str[-2:]

    fig = go.Figure()
    if data.empty:
        fig.add_annotation(text="No data available", showarrow=False, font=dict(color=GREY))
        return _apply_layout(fig, height=300)

    fig.add_trace(go.Bar(
        x=data["Label"], y=data["Sales"],
        marker_color=NAVY, marker_line_width=0,
        text=[f"₹{v:,.0f}" for v in data["Sales"]],
        textposition="outside", textfont=dict(size=10, color=NAVY),
        hovertemplate="<b>%{x}</b><br>Total Sales: ₹%{y:,.0f}<extra></extra>",
        showlegend=False,
        width=0.55,
    ))
    fig.update_yaxes(range=[0, data["Sales"].max() * 1.25])
    return _apply_layout(fig, height=300)


# ---------------------------------------------------------------------------
# 4. Month-over-Month Growth %
# ---------------------------------------------------------------------------
def mom_growth_chart(monthly_df: pd.DataFrame) -> go.Figure:
    data = monthly_df.sort_values("SortKey").reset_index(drop=True).copy()
    data["MoM_Growth"] = data["Sales"].pct_change() * 100

    plot_data = data.dropna(subset=["MoM_Growth"])

    fig = go.Figure()
    if plot_data.empty:
        fig.add_annotation(text="Not enough months to compute growth",
                            showarrow=False, font=dict(color=GREY))
        return _apply_layout(fig, height=300)

    colors = [GREEN if v >= 0 else RED for v in plot_data["MoM_Growth"]]

    fig.add_trace(go.Bar(
        x=plot_data["MonthLabel"], y=plot_data["MoM_Growth"],
        marker_color=colors, marker_line_width=0,
        text=[f"{v:+.1f}%" for v in plot_data["MoM_Growth"]],
        textposition="outside", textfont=dict(size=10, color=NAVY),
        hovertemplate="<b>%{x}</b><br>MoM Growth: %{y:.1f}%<extra></extra>",
        showlegend=False,
    ))
    fig.add_hline(y=0, line_color="#D9E2EC", line_width=1.4)

    y_pad = max(abs(plot_data["MoM_Growth"].max()), abs(plot_data["MoM_Growth"].min())) * 0.35
    fig.update_yaxes(range=[plot_data["MoM_Growth"].min() - y_pad, plot_data["MoM_Growth"].max() + y_pad])
    return _apply_layout(fig, height=300)


# ---------------------------------------------------------------------------
# 5. Forecast (actuals + trailing average + projected next month)
# ---------------------------------------------------------------------------
def forecast_chart(monthly_df: pd.DataFrame, forecast_info: dict) -> go.Figure:
    data = monthly_df.sort_values("SortKey").reset_index(drop=True)
    fig = go.Figure()

    if data.empty:
        fig.add_annotation(text="No data available", showarrow=False, font=dict(color=GREY))
        return _apply_layout(fig, height=300)

    fig.add_trace(go.Scatter(
        x=data["MonthLabel"], y=data["Sales"],
        mode="lines+markers", name="Actual Sales",
        line=dict(color=BLUE, width=3),
        marker=dict(size=6, color=BLUE),
        hovertemplate="<b>%{x}</b><br>Sales: ₹%{y:,.0f}<extra></extra>",
    ))

    next_label = "Next Month (F)"
    forecast_x = list(data["MonthLabel"]) + [next_label]
    forecast_y = [None] * (len(data) - 1) + [data.iloc[-1]["Sales"], forecast_info["forecast_value"]]

    fig.add_trace(go.Scatter(
        x=forecast_x, y=forecast_y,
        mode="lines+markers", name="Forecast",
        line=dict(color=ACCENT, width=3, dash="dash"),
        marker=dict(size=9, color=ACCENT, symbol="diamond"),
        hovertemplate="<b>%{x}</b><br>Forecast: ₹%{y:,.0f}<extra></extra>",
    ))

    fig.add_annotation(
        x=next_label, y=forecast_info["forecast_value"],
        text=f"₹{forecast_info['forecast_value']:,.0f}",
        showarrow=True, arrowhead=2, arrowcolor=ACCENT, ax=0, ay=-30,
        font=dict(size=11, color=ACCENT, family="Segoe UI"),
    )

    return _apply_layout(fig, height=300)
