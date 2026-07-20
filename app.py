"""
------
KORES INDIA LTD. — Sales Trend Analysis Dashboard
Main Streamlit entry point. Wires together all modular components:
header, filters, summary KPIs, charts and insights.

Run with:
    streamlit run app.py
"""

import os
import streamlit as st

from components.utils import load_data, aggregate_monthly, forecast_next_month
from components.header import render_header
from components.filters import render_filters
from components.summary import render_summary_cards
from components import charts
from components import insights
from components.ai_engine import render_ai_consultant

# ---------------------------------------------------------------------------
# Page configuration (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Kores India Ltd. | Sales Trend Analysis Dashboard",
    page_icon="assets/kores_logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "SalesData.xlsx")
LOGO_PATH = os.path.join(BASE_DIR, "assets", "kores_logo.png")
CSS_PATH = os.path.join(BASE_DIR, "styles", "style.css")


def load_css(path: str) -> None:
    """Injects the external stylesheet into the Streamlit app."""
    with open(path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_chart_row(chart_title: str, chart_subtitle: str, figure, insight_render_fn, key: str):
    """
    Renders one dashboard row: chart on the left (wide), business
    insights panel on the right (narrow) — as required by the spec.
    """
    left, right = st.columns([2.4, 1], gap="medium")
    with left:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-title">{chart_title}</div>', unsafe_allow_html=True)
        if chart_subtitle:
            st.markdown(f'<div class="chart-subtitle">{chart_subtitle}</div>', unsafe_allow_html=True)
        st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False}, key=key)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        insight_render_fn()


def main():
    load_css(CSS_PATH)
    render_header(LOGO_PATH)

    if not os.path.exists(DATA_PATH):
        st.error(
            "SalesData.xlsx was not found in the /data folder. "
            "Please place the file at data/SalesData.xlsx and reload."
        )
        st.stop()

    try:
        df = load_data(DATA_PATH)
    except Exception as e:
        st.error(f"Could not load the dataset: {e}")
        st.stop()

    # ============================================================
    # POWER BI STYLE LAYOUT
    # ============================================================

    st.markdown(
        """
        <div class="dashboard-wrapper">
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns(
        [1.05, 4.15],
        gap="large"
    )

    # ===========================
    # LEFT FILTER PANEL
    # ===========================

    with left_col:

        st.markdown(
            """
            <div class="left-panel">
            """,
            unsafe_allow_html=True,
        )

        filtered_df, sel_category, sel_material = render_filters(df)

        st.markdown(
            """
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ===========================
    # RIGHT CONTENT
    # ===========================

    with right_col:
        if filtered_df.empty:
            st.warning("No records match the selected filters. Please adjust your selection.")
            st.stop()

        monthly_df = aggregate_monthly(filtered_df)

        # ---- KPI Summary Cards ----
        render_summary_cards(filtered_df)
        st.markdown('<hr class="kores-divider"/>', unsafe_allow_html=True)

        st.markdown('<p class="section-title">Detailed Analysis</p>', unsafe_allow_html=True)

        # ---- Chart 1: Sales Trend (with year selector) ----
        years = sorted(monthly_df["Year"].unique().tolist())
        year_options = ["All Years"] + years

        year_filter_col, _ = st.columns([1, 3])
        with year_filter_col:
            selected_year = st.radio(
                "Select Year for Trend Chart",
                options=year_options,
                horizontal=True,
                key="trend_year_selector",
            )

        trend_fig = charts.sales_trend_chart(monthly_df, selected_year)
        render_chart_row(
            "Sales Trend Analysis",
            "Monthly sales trajectory with peak, lowest and average benchmarks",
            trend_fig,
            lambda: insights.render_trend_insights(monthly_df, selected_year),
            key="chart_trend",
        )

        # ---- Chart 2: Monthly Sales Comparison ----
        comparison_fig = charts.monthly_comparison_chart(monthly_df)
        render_chart_row(
            "Monthly Sales Comparison",
            "Highest month in green, lowest in red, all others in corporate blue",
            comparison_fig,
            lambda: insights.render_monthly_comparison_insights(monthly_df),
            key="chart_comparison",
        )

        # ---- Chart 3: Quarterly Sales ----
        quarterly_fig = charts.quarterly_sales_chart(monthly_df)
        render_chart_row(
            "Quarterly Sales Performance",
            "Total sales aggregated by quarter",
            quarterly_fig,
            lambda: insights.render_quarterly_insights(monthly_df),
            key="chart_quarterly",
        )

        # ---- Chart 4: MoM Growth % ----
        growth_fig = charts.mom_growth_chart(monthly_df)
        render_chart_row(
            "Month-over-Month Growth %",
            "Percentage change in sales versus the preceding month",
            growth_fig,
            lambda: insights.render_mom_growth_insights(monthly_df),
            key="chart_growth",
        )

        # ---- Chart 5: Forecast ----
        forecast_info = forecast_next_month(monthly_df)
        forecast_fig = charts.forecast_chart(monthly_df, forecast_info)

        forecast_left, forecast_right = st.columns([2.4, 1], gap="medium")
        with forecast_left:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Next Month Sales Forecast</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="chart-subtitle">Projected using the trailing 3-month average</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(forecast_fig, use_container_width=True,
                             config={"displayModeBar": False}, key="chart_forecast")

            fc_col1, fc_col2 = st.columns(2)
            with fc_col1:
                st.markdown(
                    f"""
                    <div class="forecast-box">
                        <div class="forecast-label">Forecasted Sales — Next Month</div>
                        <div class="forecast-value">₹{forecast_info['forecast_value']:,.0f}</div>
                        <span class="forecast-tag">{forecast_info['confidence']} Confidence</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with fc_col2:
                st.markdown(
                    f"""
                    <div class="forecast-box" style="background:linear-gradient(135deg,#1E88E5 0%,#0056A6 100%);">
                        <div class="forecast-label">Recommendation</div>
                        <div style="font-size:13.5px;font-weight:600;margin-top:8px;line-height:1.5;">
                            {forecast_info['recommendation']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
        with forecast_right:
            insights.render_forecast_insights(monthly_df, forecast_info)

    # =====================================================
    # END OF RIGHT COLUMN
    # =====================================================

    st.markdown('<hr class="kores-divider"/>', unsafe_allow_html=True)

    # Full-width AI Consultant
    render_ai_consultant(filtered_df, monthly_df)

    st.markdown(
        """
        </div>
        """,
        unsafe_allow_html=True,
    )



if __name__ == "__main__":
    main()



