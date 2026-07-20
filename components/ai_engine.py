"""
ai_engine.py
------------

Renders the AI Business Consultant section.
"""

import streamlit as st

from components.ai_analysis import analyse_business
from components.ai_writer import generate_report


# =====================================================
# HEALTH COLOR
# =====================================================

def _health_color(score):

    if score >= 85:
        return "#1E8E3E"

    elif score >= 70:
        return "#F9A825"

    return "#D93025"


# =====================================================
# SECTION
# =====================================================

def _section(title, body):

    st.markdown(
        f"""
<div style="
background:white;
padding:20px;
border-radius:14px;
margin-bottom:20px;
box-shadow:0 2px 8px rgba(0,0,0,.08);
border-left:6px solid #0056A6;
">

<h4 style="
margin-top:0;
color:#0A2E5C;
">
{title}
</h4>

<p style="
font-size:15px;
line-height:1.8;
color:#444;
margin-bottom:0;
">
{body}
</p>

</div>
""",
        unsafe_allow_html=True
    )
# =====================================================
# ACTIONS
# =====================================================

def _actions(items):

    html = ""

    for item in items:
        html += f"""
<div class="ai-action">
✅ {item}
</div>
"""

    st.markdown(html, unsafe_allow_html=True)


# =====================================================
# MAIN RENDER
# =====================================================

def render_ai_consultant(filtered_df, monthly_df):

    metrics = analyse_business(filtered_df, monthly_df)

    report = generate_report(metrics)

    score = report["health_score"]

    color = _health_color(score)

    st.markdown("<br>", unsafe_allow_html=True)

    # ====================================================
    # TITLE
    # ====================================================
    # ====================================================
    # HEALTH CARD
    # ====================================================

    st.markdown("## 🤖 AI Business Consultant")
    st.caption("AI-generated business recommendations based on the selected data.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.metric(
            label="Overall Business Health",
            value=f"{score}/100",
            delta=report["rating"]
        )

    with col2:
        st.info(f"📅 Generated on\n\n{report['generated_on']}")
    # ====================================================
    # TWO COLUMNS
    # ====================================================

    left, right = st.columns(2)

    with left:

        _section(
            "📋 Executive Summary",
            report["executive_summary"]
        )

        _section(
            "📈 Sales Analysis",
            report["sales_analysis"]
        )

        _section(
            "💰 Revenue Opportunity",
            report["revenue_opportunity"]
        )

    with right:

        _section(
            "📦 Inventory Recommendation",
            report["inventory_recommendation"]
        )

        _section(
            "⚠ Risk Analysis",
            report["risk_analysis"]
        )

    # ====================================================
    # ACTIONS
    # ====================================================

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <h3 style='color:#0A2E5C;'>
    🎯 Recommended Action Plan
    </h3>
    """, unsafe_allow_html=True)

    _actions(report["action_items"])