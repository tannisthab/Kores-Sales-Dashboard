"""
ai_writer.py
------------
Converts business metrics into executive-style business reports.

Input:
    metrics (dict)

Output:
    Dictionary containing all narrative sections for the dashboard.
"""

from datetime import datetime


# ==========================================================
# Helper Functions
# ==========================================================

def _trend_sentence(trend: str) -> str:
    if trend == "Upward":
        return (
            "Sales momentum has remained consistently positive throughout the "
            "analysis period, indicating healthy customer demand and improving "
            "business performance."
        )

    elif trend == "Downward":
        return (
            "Sales have shown a declining pattern over the analysed period, "
            "suggesting reduced demand or changing market conditions that "
            "require management attention."
        )

    return (
        "Sales have remained relatively stable with only minor month-to-month "
        "variations."
    )


def _risk_sentence(risk: str) -> str:
    if risk == "Low":
        return (
            "Current business risk is considered low based on the consistency "
            "of sales and forecast confidence."
        )

    elif risk == "Medium":
        return (
            "Moderate business risk exists due to fluctuations in recent sales. "
            "Close monitoring is recommended."
        )

    return (
        "Business risk is relatively high because of unstable sales trends and "
        "forecast uncertainty."
    )


# ==========================================================
# Executive Summary
# ==========================================================

def executive_summary(metrics: dict):

    return (
        f"Business Health Score is {metrics['health_score']}/100 "
        f"({metrics['rating']}). "
        f"{_trend_sentence(metrics['trend'])} "
        f"Overall sales growth stands at "
        f"{metrics['overall_growth']:.1f}% with "
        f"{metrics['positive_growth_months']} positive growth months. "
        f"{_risk_sentence(metrics['risk'])}"
    )


# ==========================================================
# Sales Analysis
# ==========================================================

def sales_analysis(metrics: dict):

    return (
        f"The highest sales were recorded during "
        f"{metrics['highest_month']}, while "
        f"{metrics['lowest_month']} experienced the weakest performance. "
        f"The overall sales trend is {metrics['trend'].lower()}, "
        f"supported by an average monthly sales value of "
        f"₹{metrics['average_sales']:,.0f}."
    )


# ==========================================================
# Inventory Recommendation
# ==========================================================

def inventory_recommendation(metrics: dict):

    if metrics["trend"] == "Upward":

        return (
            "Increase inventory levels for high-performing products. "
            "Recent demand indicates continued sales momentum, and maintaining "
            "additional safety stock may help prevent stock shortages."
        )

    elif metrics["trend"] == "Downward":

        return (
            "Maintain conservative inventory levels until demand stabilises. "
            "Avoid overstocking products with declining sales."
        )

    return (
        "Maintain current inventory levels while closely monitoring "
        "monthly demand fluctuations."
    )


# ==========================================================
# Revenue Opportunity
# ==========================================================

def revenue_opportunity(metrics: dict):

    return (
        f"The '{metrics['best_category']}' category currently delivers the "
        f"strongest sales performance. Additional marketing campaigns, "
        f"cross-selling initiatives, or promotional activities focused on "
        f"this category may generate further revenue growth."
    )


# ==========================================================
# Risk Analysis
# ==========================================================

def risk_analysis(metrics: dict):

    return (
        f"Business risk is currently classified as "
        f"{metrics['risk']}. "
        f"Forecast confidence is "
        f"{metrics['forecast_confidence']}. "
        f"Management should continue monitoring demand patterns and "
        f"inventory movement to minimise operational risk."
    )


# ==========================================================
# Action Items
# ==========================================================

def action_items(metrics: dict):

    actions = []

    if metrics["trend"] == "Upward":
        actions.append("Increase inventory for high-demand products.")

    if metrics["overall_growth"] < 0:
        actions.append("Investigate reasons for declining sales.")

    if metrics["risk"] != "Low":
        actions.append("Review pricing and promotional strategy.")

    actions.extend([
        "Monitor monthly sales performance.",
        "Review forecast before procurement decisions.",
        "Focus marketing efforts on the best-performing category."
    ])

    return actions[:5]


# ==========================================================
# Generate Complete Report
# ==========================================================

def generate_report(metrics: dict):

    return {

        "generated_on": datetime.now().strftime("%d %b %Y"),

        "health_score": metrics["health_score"],

        "rating": metrics["rating"],

        "executive_summary": executive_summary(metrics),

        "sales_analysis": sales_analysis(metrics),

        "inventory_recommendation": inventory_recommendation(metrics),

        "revenue_opportunity": revenue_opportunity(metrics),

        "risk_analysis": risk_analysis(metrics),

        "action_items": action_items(metrics)
    }