"""
insights.py
-----------
Generates and renders the "Business Insights" panel that sits beside
every chart. Each function returns narrative, data-grounded text
(not just raw numbers) explaining what the chart means and what
action it suggests.
"""

import streamlit as st
import pandas as pd
import numpy as np

from components.utils import format_inr


def _render_panel(title: str, rows: list, note: str, recommendation: str = "") -> None:
    """Common renderer for an insight card: title, key/value rows, narrative note, recommendation."""
    rows_html = "".join(
        f'<div class="insight-row"><span class="insight-row-label">{label}</span>'
        f'<span class="insight-row-value">{value}</span></div>'
        for label, value in rows
    )
    reco_html = f'<div class="insight-reco">Recommendation: {recommendation}</div>' if recommendation else ""

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">Business Insights</div>
            {rows_html}
            <div class="insight-note">{note}</div>
            {reco_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# 1. Sales Trend Insights
# ---------------------------------------------------------------------------
def render_trend_insights(monthly_df: pd.DataFrame, selected_year=None) -> None:
    data = monthly_df.copy()
    if selected_year and selected_year != "All Years":
        data = data[data["Year"] == selected_year]
    data = data.sort_values("SortKey")

    if data.empty:
        _render_panel("Sales Trend", [], "No data available for the selected year.")
        return

    avg_val = data["Sales"].mean()
    max_row = data.loc[data["Sales"].idxmax()]
    min_row = data.loc[data["Sales"].idxmin()]
    first_val, last_val = data.iloc[0]["Sales"], data.iloc[-1]["Sales"]
    direction = "an upward" if last_val > first_val else "a downward" if last_val < first_val else "a flat"

    rows = [
        ("Peak Month", f"{max_row['MonthLabel']} ({format_inr(max_row['Sales'])})"),
        ("Lowest Month", f"{min_row['MonthLabel']} ({format_inr(min_row['Sales'])})"),
        ("Average Sales", format_inr(avg_val)),
    ]
    note = (
        f"Sales followed {direction} trajectory across the selected period, with "
        f"{max_row['MonthLabel']} recording the strongest performance and "
        f"{min_row['MonthLabel']} the weakest. The average line indicates the "
        f"typical monthly run-rate against which future months can be benchmarked."
    )
    reco = (
        "Investigate the drivers behind the peak month (promotions, seasonality, "
        "new orders) and replicate them; review the low month for stock-outs, "
        "pricing, or demand gaps."
    )
    _render_panel("Sales Trend", rows, note, reco)


# ---------------------------------------------------------------------------
# 2. Monthly Comparison Insights
# ---------------------------------------------------------------------------
def render_monthly_comparison_insights(monthly_df: pd.DataFrame) -> None:
    data = monthly_df.sort_values("SortKey")
    if data.empty:
        _render_panel("Monthly Comparison", [], "No data available.")
        return

    max_row = data.loc[data["Sales"].idxmax()]
    min_row = data.loc[data["Sales"].idxmin()]
    spread = max_row["Sales"] - min_row["Sales"]
    spread_pct = (spread / min_row["Sales"] * 100) if min_row["Sales"] else 0

    rows = [
        ("Best Month", f"{max_row['MonthLabel']} ({format_inr(max_row['Sales'])})"),
        ("Weakest Month", f"{min_row['MonthLabel']} ({format_inr(min_row['Sales'])})"),
        ("Spread", f"{spread_pct:.1f}% variance"),
    ]
    note = (
        f"The gap between the best and weakest month is {format_inr(spread)}, "
        f"a {spread_pct:.1f}% swing. Such variability suggests sales are influenced "
        f"by seasonal or order-driven fluctuations rather than a flat run-rate."
    )
    reco = (
        "Use the strongest month as a benchmark for sales targets and align "
        "inventory planning to avoid shortfalls in weaker months."
    )
    _render_panel("Monthly Comparison", rows, note, reco)


# ---------------------------------------------------------------------------
# 3. Quarterly Insights
# ---------------------------------------------------------------------------
def render_quarterly_insights(monthly_df: pd.DataFrame) -> None:
    q_data = (
        monthly_df.groupby(["Year", "Quarter"], as_index=False)
        .agg(Sales=("Sales", "sum"), SortKey=("SortKey", "min"))
        .sort_values("SortKey")
    )
    if q_data.empty:
        _render_panel("Quarterly Performance", [], "No data available.")
        return

    best_q = q_data.loc[q_data["Sales"].idxmax()]
    worst_q = q_data.loc[q_data["Sales"].idxmin()]

    rows = [
        ("Best Quarter", f"{best_q['Quarter']} '{str(best_q['Year'])[-2:]} ({format_inr(best_q['Sales'])})"),
        ("Weakest Quarter", f"{worst_q['Quarter']} '{str(worst_q['Year'])[-2:]} ({format_inr(worst_q['Sales'])})"),
        ("Quarters Tracked", f"{len(q_data)}"),
    ]
    note = (
        f"Quarterly aggregation smooths month-to-month noise and highlights "
        f"sustained demand cycles. {best_q['Quarter']} stands out as the strongest "
        f"period, while {worst_q['Quarter']} trails behind, useful for planning "
        f"quarterly procurement and staffing."
    )
    reco = (
        "Align quarterly budgets and inventory build-up ahead of historically "
        "strong quarters, and plan cost controls during softer quarters."
    )
    _render_panel("Quarterly Performance", rows, note, reco)


# ---------------------------------------------------------------------------
# 4. MoM Growth Insights
# ---------------------------------------------------------------------------
def render_mom_growth_insights(monthly_df: pd.DataFrame) -> None:
    data = monthly_df.sort_values("SortKey").copy()
    data["MoM_Growth"] = data["Sales"].pct_change() * 100
    plot_data = data.dropna(subset=["MoM_Growth"])

    if plot_data.empty:
        _render_panel("Month-over-Month Growth", [], "At least two months of data are needed to compute growth.")
        return

    best_row = plot_data.loc[plot_data["MoM_Growth"].idxmax()]
    worst_row = plot_data.loc[plot_data["MoM_Growth"].idxmin()]
    avg_growth = plot_data["MoM_Growth"].mean()
    positive_months = int((plot_data["MoM_Growth"] >= 0).sum())
    total_months = len(plot_data)

    rows = [
        ("Best Growth", f"{best_row['MonthLabel']} ({best_row['MoM_Growth']:+.1f}%)"),
        ("Steepest Decline", f"{worst_row['MonthLabel']} ({worst_row['MoM_Growth']:+.1f}%)"),
        ("Avg. MoM Growth", f"{avg_growth:+.1f}%"),
        ("Growth Months", f"{positive_months} of {total_months}"),
    ]
    note = (
        f"Sales grew month-over-month in {positive_months} of {total_months} months. "
        f"The sharpest acceleration occurred in {best_row['MonthLabel']}, while "
        f"{worst_row['MonthLabel']} saw the steepest pull-back, useful signals for "
        f"identifying momentum versus one-off dips."
    )
    reco = (
        "Treat consecutive negative-growth months as an early warning signal for "
        "demand softening and trigger a review of pricing, stock, or market conditions."
    )
    _render_panel("Month-over-Month Growth", rows, note, reco)


# ---------------------------------------------------------------------------
# 5. Forecast Insights
# ---------------------------------------------------------------------------
def render_forecast_insights(monthly_df: pd.DataFrame, forecast_info: dict) -> None:
    basis = ", ".join(forecast_info.get("basis_months", [])) or "N/A"
    rows = [
        ("Forecast Basis", basis),
        ("Confidence", f"{forecast_info['confidence']} ({forecast_info['confidence_pct']}%)"),
    ]
    note = (
        f"The forecast is calculated as the average sales of the trailing "
        f"{len(forecast_info.get('basis_months', []))} months ({basis}). "
        f"Confidence is derived from how consistent those months were: tighter "
        f"clustering yields higher confidence, wider swings lower it."
    )
    _render_panel("Forecast Outlook", rows, note, forecast_info["recommendation"])
