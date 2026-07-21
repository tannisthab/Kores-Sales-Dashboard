"""
charts.py
---------
Builds every Plotly figure used in the dashboard.

1. Sales Trend
2. Monthly Comparison
3. Quarterly Sales
4. Month-over-Month Growth
5. Forecast
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------------------------------------------------------------
# COLORS
# ---------------------------------------------------------------------

NAVY = "#0A2E5C"
BLUE = "#0056A6"
ACCENT = "#1E88E5"
LIGHT_BLUE = "#CFE2FA"
GREEN = "#1E8E3E"
RED = "#D93025"
GREY = "#5F6368"
BG = "#FFFFFF"

# ---------------------------------------------------------------------
# NUMBER FORMATTING
# ---------------------------------------------------------------------

def format_lakh(value):
    """
    95000      -> 0.95L
    1250000    -> 12.5L
    23500000   -> 2.35Cr
    """

    value = float(value)

    if abs(value) >= 10000000:
        return f"₹{value/10000000:.2f} Cr"

    return f"₹{value/100000:.2f} L"


# ---------------------------------------------------------------------
# AXIS FORMATTING
# ---------------------------------------------------------------------

def y_axis_format(fig):
    """
    Since charts use values divided by 100000,
    show axis in Lakhs.
    """

    fig.update_yaxes(
        ticksuffix=" L",
        separatethousands=True
    )

    return fig


# ---------------------------------------------------------------------
# BASE LAYOUT
# ---------------------------------------------------------------------

BASE_LAYOUT = dict(

    plot_bgcolor=BG,

    paper_bgcolor=BG,

    font=dict(
        family="Segoe UI",
        size=12,
        color=NAVY,
    ),

    margin=dict(
        l=35,
        r=25,
        t=20,
        b=35,
    ),

    hoverlabel=dict(
        bgcolor="white",
        font_size=12,
        font_family="Segoe UI",
    ),

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.01,
        xanchor="right",
        x=1,
        font=dict(size=11),
        bgcolor="rgba(0,0,0,0)",
    ),
)

AXIS_STYLE = dict(

    showgrid=True,

    gridcolor="#EEF2F7",

    gridwidth=1,

    zeroline=False,

    showline=True,

    linecolor="#D9E2EC",

    tickfont=dict(
        size=11,
        color=GREY,
    ),
)


def _apply_layout(fig: go.Figure, height=320):

    fig.update_layout(
        **BASE_LAYOUT,
        height=height,
    )

    fig.update_xaxes(**AXIS_STYLE)

    fig.update_yaxes(**AXIS_STYLE)

    return fig
# ---------------------------------------------------------------------------
# 1. Sales Trend
# ---------------------------------------------------------------------------
def sales_trend_chart(monthly_df: pd.DataFrame, selected_year=None) -> go.Figure:
    """
    Smooth sales trend line with year filter.
    Displays values in Lakhs while hover shows full amount.
    """

    data = monthly_df.copy()

    if selected_year and selected_year != "All Years":
        data = data[data["Year"] == selected_year]

    data = data.sort_values("SortKey").reset_index(drop=True)

    fig = go.Figure()

    if data.empty:
        fig.add_annotation(
            text="No data available",
            showarrow=False,
            font=dict(color=GREY)
        )
        return _apply_layout(fig, height=340)

    avg_val = data["Sales"].mean()

    max_idx = data["Sales"].idxmax()
    min_idx = data["Sales"].idxmin()

    # -----------------------------
    # Main Trend
    # -----------------------------
    fig.add_trace(
        go.Scatter(
            x=data["MonthLabel"],
            y=data["Sales"] / 100000,
            mode="lines+markers",
            line=dict(
                color=BLUE,
                width=3,
                shape="spline",
                smoothing=1.1,
            ),
            marker=dict(
                size=8,
                color=BLUE,
                line=dict(width=1, color="white"),
            ),
            customdata=data["Sales"],
            hovertemplate=
            "<b>%{x}</b><br>"
            "Sales : ₹%{customdata:,.0f}"
            "<extra></extra>",
            name="Sales",
        )
    )

    # -----------------------------
    # Average Line
    # -----------------------------
    fig.add_hline(
        y=avg_val / 100000,
        line_dash="dot",
        line_color=GREY,
        annotation_text=f"Average : {format_lakh(avg_val)}",
        annotation_position="top left",
    )

    # -----------------------------
    # Peak Marker
    # -----------------------------
    fig.add_trace(
        go.Scatter(
            x=[data.loc[max_idx, "MonthLabel"]],
            y=[data.loc[max_idx, "Sales"] / 100000],
            mode="markers",
            marker=dict(
                size=15,
                color=GREEN,
                line=dict(width=2, color="white"),
            ),
            customdata=[data.loc[max_idx, "Sales"]],
            hovertemplate=
            "<b>Highest Sales</b><br>"
            "₹%{customdata:,.0f}"
            "<extra></extra>",
            name="Peak",
        )
    )

    fig.add_annotation(
        x=data.loc[max_idx, "MonthLabel"],
        y=data.loc[max_idx, "Sales"] / 100000,
        text=format_lakh(data.loc[max_idx, "Sales"]),
        showarrow=True,
        arrowcolor=GREEN,
        arrowhead=2,
        ax=0,
        ay=-30,
        font=dict(color=GREEN),
    )

    # -----------------------------
    # Lowest Marker
    # -----------------------------
    fig.add_trace(
        go.Scatter(
            x=[data.loc[min_idx, "MonthLabel"]],
            y=[data.loc[min_idx, "Sales"] / 100000],
            mode="markers",
            marker=dict(
                size=15,
                color=RED,
                line=dict(width=2, color="white"),
            ),
            customdata=[data.loc[min_idx, "Sales"]],
            hovertemplate=
            "<b>Lowest Sales</b><br>"
            "₹%{customdata:,.0f}"
            "<extra></extra>",
            name="Lowest",
        )
    )

    fig.add_annotation(
        x=data.loc[min_idx, "MonthLabel"],
        y=data.loc[min_idx, "Sales"] / 100000,
        text=format_lakh(data.loc[min_idx, "Sales"]),
        showarrow=True,
        arrowcolor=RED,
        arrowhead=2,
        ax=0,
        ay=30,
        font=dict(color=RED),
    )

    fig.update_yaxes(title="Sales (Lakhs)")
    fig = y_axis_format(fig)

    return _apply_layout(fig, height=340)
# ---------------------------------------------------------------------------
# 2. Monthly Sales Comparison
# ---------------------------------------------------------------------------
def monthly_comparison_chart(monthly_df: pd.DataFrame) -> go.Figure:
    """
    Monthly Sales Comparison
    Displays values in Lakhs while hover shows full amount.
    Highest month -> Green
    Lowest month -> Red
    Others -> Blue
    """

    data = monthly_df.sort_values("SortKey").reset_index(drop=True)

    fig = go.Figure()

    if data.empty:
        fig.add_annotation(
            text="No data available",
            showarrow=False,
            font=dict(color=GREY)
        )
        return _apply_layout(fig, height=320)

    max_sales = data["Sales"].max()
    min_sales = data["Sales"].min()

    colors = []

    for val in data["Sales"]:
        if val == max_sales:
            colors.append(GREEN)
        elif val == min_sales:
            colors.append(RED)
        else:
            colors.append(BLUE)

    fig.add_trace(
        go.Bar(
            x=data["MonthLabel"],
            y=data["Sales"] / 100000,

            marker=dict(
                color=colors,
                line=dict(width=0)
            ),

            customdata=data["Sales"],

            text=[format_lakh(v) for v in data["Sales"]],
            textposition="outside",
            textfont=dict(
                size=10,
                color=NAVY
            ),

            hovertemplate=
            "<b>%{x}</b><br>"
            "Sales : ₹%{customdata:,.0f}"
            "<extra></extra>",

            showlegend=False,
        )
    )

    fig.update_yaxes(
        title="Sales (Lakhs)",
        range=[
            0,
            (max_sales / 100000) * 1.20
        ]
    )

    fig.update_xaxes(title="Month")

    fig = y_axis_format(fig)

    return _apply_layout(fig, height=320)
# ---------------------------------------------------------------------------
# 3. Quarterly Sales
# ---------------------------------------------------------------------------
def quarterly_sales_chart(monthly_df: pd.DataFrame) -> go.Figure:
    """
    Quarterly Sales Performance
    Displays values in Lakhs while hover shows full ₹ amount.
    """

    data = (
        monthly_df
        .groupby(["Year", "Quarter"], as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            SortKey=("SortKey", "min")
        )
        .sort_values("SortKey")
        .reset_index(drop=True)
    )

    fig = go.Figure()

    if data.empty:
        fig.add_annotation(
            text="No data available",
            showarrow=False,
            font=dict(color=GREY)
        )
        return _apply_layout(fig, height=320)

    # Quarter Labels
    data["QuarterLabel"] = (
        data["Quarter"] +
        " '" +
        data["Year"].astype(str).str[-2:]
    )

    fig.add_trace(
        go.Bar(
            x=data["QuarterLabel"],
            y=data["Sales"] / 100000,

            marker=dict(
                color=NAVY,
                line=dict(width=0)
            ),

            width=0.55,

            customdata=data["Sales"],

            text=[format_lakh(v) for v in data["Sales"]],
            textposition="outside",

            textfont=dict(
                size=10,
                color=NAVY
            ),

            hovertemplate=
            "<b>%{x}</b><br>"
            "Quarter Sales : ₹%{customdata:,.0f}"
            "<extra></extra>",

            showlegend=False,
        )
    )

    ymax = (data["Sales"].max() / 100000) * 1.25

    fig.update_yaxes(
        title="Sales (Lakhs)",
        range=[0, ymax]
    )

    fig.update_xaxes(
        title="Quarter"
    )

    fig = y_axis_format(fig)

    return _apply_layout(fig, height=320)
# ---------------------------------------------------------------------------
# 4. Month-over-Month Growth %
# ---------------------------------------------------------------------------
def mom_growth_chart(monthly_df: pd.DataFrame) -> go.Figure:
    """
    Month-over-Month Growth (%)
    Positive = Green
    Negative = Red
    """

    data = monthly_df.sort_values("SortKey").reset_index(drop=True).copy()

    data["MoM_Growth"] = data["Sales"].pct_change() * 100

    data = data.dropna(subset=["MoM_Growth"])

    fig = go.Figure()

    if data.empty:
        fig.add_annotation(
            text="Not enough data to calculate growth",
            showarrow=False,
            font=dict(color=GREY)
        )
        return _apply_layout(fig, height=320)

    colors = [
        GREEN if x >= 0 else RED
        for x in data["MoM_Growth"]
    ]

    fig.add_trace(
        go.Bar(
            x=data["MonthLabel"],
            y=data["MoM_Growth"],

            marker=dict(
                color=colors,
                line=dict(width=0)
            ),

            text=[
                f"{v:+.1f}%"
                for v in data["MoM_Growth"]
            ],

            textposition="outside",

            textfont=dict(
                size=10,
                color=NAVY
            ),

            hovertemplate=
            "<b>%{x}</b><br>"
            "Growth : %{y:.2f}%"
            "<extra></extra>",

            showlegend=False,
        )
    )

    fig.add_hline(
        y=0,
        line_color="#D9E2EC",
        line_width=1.5,
    )

    ymax = data["MoM_Growth"].max()
    ymin = data["MoM_Growth"].min()

    padding = max(abs(ymax), abs(ymin)) * 0.30

    fig.update_yaxes(
        title="Growth (%)",
        range=[
            ymin - padding,
            ymax + padding,
        ]
    )

    fig.update_xaxes(
        title="Month"
    )

    return _apply_layout(fig, height=320)
# ---------------------------------------------------------------------------
# 5. Forecast (Actual + Predicted)
# ---------------------------------------------------------------------------
def forecast_chart(monthly_df: pd.DataFrame, forecast_info: dict) -> go.Figure:
    """
    Forecast chart.

    • Displays values in Lakhs / Crores
    • Hover shows full ₹ value
    """

    data = monthly_df.sort_values("SortKey").reset_index(drop=True)

    fig = go.Figure()

    if data.empty:
        fig.add_annotation(
            text="No data available",
            showarrow=False,
            font=dict(color=GREY),
        )
        return _apply_layout(fig, height=320)

    # ----------------------------------------------------
    # Actual Sales
    # ----------------------------------------------------
    fig.add_trace(
        go.Scatter(
            x=data["MonthLabel"],
            y=data["Sales"] / 100000,

            mode="lines+markers",

            line=dict(
                color=BLUE,
                width=3
            ),

            marker=dict(
                size=7,
                color=BLUE
            ),

            name="Actual Sales",

            customdata=data["Sales"],

            hovertemplate=
            "<b>%{x}</b><br>"
            "Sales : ₹%{customdata:,.0f}"
            "<extra></extra>",
        )
    )

    # ----------------------------------------------------
    # Forecast Line
    # ----------------------------------------------------
    next_month = "Next Month"

    x_values = list(data["MonthLabel"]) + [next_month]

    y_values = (
        [None] * (len(data) - 1)
        + [
            data.iloc[-1]["Sales"] / 100000,
            forecast_info["forecast_value"] / 100000,
        ]
    )

    custom_values = (
        [None] * (len(data) - 1)
        + [
            data.iloc[-1]["Sales"],
            forecast_info["forecast_value"],
        ]
    )

    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,

            mode="lines+markers",

            line=dict(
                color=ACCENT,
                width=3,
                dash="dash",
            ),

            marker=dict(
                size=9,
                color=ACCENT,
                symbol="diamond",
            ),

            name="Forecast",

            customdata=custom_values,

            hovertemplate=
            "<b>%{x}</b><br>"
            "Forecast : ₹%{customdata:,.0f}"
            "<extra></extra>",
        )
    )

    # ----------------------------------------------------
    # Forecast Annotation
    # ----------------------------------------------------
    fig.add_annotation(
        x=next_month,
        y=forecast_info["forecast_value"] / 100000,

        text=format_lakh(forecast_info["forecast_value"]),

        showarrow=True,
        arrowhead=2,
        arrowcolor=ACCENT,

        ax=0,
        ay=-30,

        font=dict(
            size=11,
            color=ACCENT,
            family="Segoe UI",
        ),
    )

    # ----------------------------------------------------
    # Axis
    # ----------------------------------------------------
    fig.update_yaxes(
        title="Sales (Lakhs)"
    )

    fig.update_xaxes(
        title="Month"
    )

    fig = y_axis_format(fig)

    return _apply_layout(fig, height=320)