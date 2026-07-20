"""
summary.py
----------
Renders the Power BI-style KPI summary cards row:
Average Sales, Maximum Sales, Minimum Sales, Total Sales,
Growth %, Highest Sales Month, Lowest Sales Month.
"""

import streamlit as st
import pandas as pd

from components.utils import aggregate_monthly, calc_kpis, format_inr


def _kpi_card(icon: str, label: str, value: str, sub: str = "", sub_class: str = "") -> str:
    sub_html = f'<div class="kpi-sub {sub_class}">{sub}</div>' if sub else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>
    """


def render_summary_cards(filtered_df: pd.DataFrame) -> dict:
    """
    Renders the 7-card KPI row and returns the computed KPI dict so
    it can be reused by chart/insight components without recomputation.
    """
    monthly_df = aggregate_monthly(filtered_df)
    kpis = calc_kpis(monthly_df)

    growth_val = kpis["growth_pct"]
    growth_class = "kpi-positive" if growth_val >= 0 else "kpi-negative"
    growth_arrow = "▲" if growth_val >= 0 else "▼"
    growth_display = f"{growth_arrow} {abs(growth_val):.1f}%"

    st.markdown('<p class="section-title">Executive Summary</p>', unsafe_allow_html=True)

    cols = st.columns(7)
    card_defs = [
        ("◆", "Average Sales", format_inr(kpis["average"]), "", ""),
        ("▲", "Maximum Sales", format_inr(kpis["maximum"]), "", ""),
        ("▼", "Minimum Sales", format_inr(kpis["minimum"]), "", ""),
        ("Σ", "Total Sales", format_inr(kpis["total"]), "", ""),
        ("%", "Growth", growth_display, "vs. first month", growth_class),
        ("★", "Highest Month", kpis["highest_month"], "Peak performance", ""),
        ("▽", "Lowest Month", kpis["lowest_month"], "Needs attention", ""),
    ]

    for col, (icon, label, value, sub, sub_class) in zip(cols, card_defs):
        with col:
            st.markdown(_kpi_card(icon, label, value, sub, sub_class), unsafe_allow_html=True)

    return kpis
