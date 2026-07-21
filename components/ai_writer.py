"""
ai_writer.py
------------
Converts business metrics into executive-style business reports.
"""

from datetime import datetime


# ==========================================================
# TREND SENTENCE
# ==========================================================

def _trend_sentence(trend):

    if trend == "Upward":
        return (
            "Sales are showing a healthy upward trend with improving business "
            "performance over the selected period."
        )

    elif trend == "Downward":
        return (
            "Sales have been declining over the selected period, indicating "
            "reduced market demand or operational challenges."
        )

    return (
        "Sales remain relatively stable without any major upward or downward movement."
    )


# ==========================================================
# RISK SENTENCE
# ==========================================================

def _risk_sentence(metrics):

    text = (
        f"Business risk is currently assessed as "
        f"{metrics['risk']} with "
        f"{metrics['forecast_confidence']} forecast confidence."
    )

    if metrics["volatility"] > 0.35:
        text += (
            " High month-to-month variation suggests unstable customer demand."
        )

    elif metrics["volatility"] > 0.20:
        text += (
            " Moderate fluctuations should be monitored closely."
        )

    else:
        text += (
            " Sales remain reasonably consistent across months."
        )

    return text


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

def executive_summary(metrics):

    return (

        f"The overall Business Health Score is "
        f"{metrics['health_score']}/100 "
        f"({metrics['rating']}). "

        f"{_trend_sentence(metrics['trend'])} "

        f"Overall sales changed by "
        f"{metrics['overall_growth']:.1f}% during the selected period. "

        f"{metrics['positive_growth_months']} months recorded positive growth, "
        f"while {metrics['negative_growth_months']} months showed a decline. "

        f"{_risk_sentence(metrics)}"
    )


# ==========================================================
# SALES ANALYSIS
# ==========================================================

def sales_analysis(metrics):

    text = (

        f"The highest sales were achieved in "
        f"{metrics['highest_month']}, whereas "
        f"{metrics['lowest_month']} recorded the lowest sales. "

        f"The best-performing category is "
        f"{metrics['best_category']}, contributing "
        f"{metrics['best_category_share']:.1f}% of total revenue. "

        f"The leading product is "
        f"{metrics['best_product']}."
    )

    if metrics["zero_sales_count"] > 0:

        text += (
            f" Additionally, "
            f"{metrics['zero_sales_count']} product(s) generated zero sales "
            f"and should be reviewed."
        )

    return text


# ==========================================================
# INVENTORY RECOMMENDATION
# ==========================================================

def inventory_recommendation(metrics):

    return metrics["inventory_strategy"]


# ==========================================================
# REVENUE OPPORTUNITY
# ==========================================================

def revenue_opportunity(metrics):

    return metrics["revenue_opportunity"]
# ==========================================================
# RISK ANALYSIS
# ==========================================================

def risk_analysis(metrics):

    text = (
        f"Overall business risk is assessed as "
        f"{metrics['risk']}. "
    )

    if metrics["decline_reason"]:

        text += "The primary observations are: "

        for i, reason in enumerate(metrics["decline_reason"], start=1):
            text += f"{i}. {reason}. "

    if metrics["forecast_confidence"] == "Low":

        text += (
            "Since forecast confidence is low, management should closely "
            "monitor market demand before making procurement decisions."
        )

    elif metrics["forecast_confidence"] == "Moderate":

        text += (
            "Forecast reliability is moderate. Monthly review of sales "
            "performance is recommended."
        )

    else:

        text += (
            "Forecast confidence is high, indicating relatively predictable "
            "sales behaviour."
        )

    return text


# ==========================================================
# ACTION ITEMS
# ==========================================================

def action_items(metrics):

    # analyse_business already generates intelligent actions.
    actions = list(metrics["action_items"])

    if metrics["forecast_confidence"] == "Low":
        actions.append(
            "Prepare contingency plans for unexpected demand fluctuations."
        )

    if metrics["overall_growth"] > 10:
        actions.append(
            "Increase production capacity to support future growth."
        )

    if metrics["overall_growth"] < -10:
        actions.append(
            "Review pricing strategy and distributor performance."
        )

    if metrics["zero_sales_count"] > 0:
        actions.append(
            "Analyse zero-selling products for discontinuation or relaunch."
        )

    # Remove duplicates while preserving order
    unique = []
    for item in actions:
        if item not in unique:
            unique.append(item)

    return unique[:6]


# ==========================================================
# GENERATE COMPLETE REPORT
# ==========================================================

def generate_report(metrics):

    return {

        "generated_on": datetime.now().strftime("%d %b %Y"),

        "health_score": metrics["health_score"],

        "rating": metrics["rating"],

        "executive_summary":
            executive_summary(metrics),

        "sales_analysis":
            sales_analysis(metrics),

        "inventory_recommendation":
            inventory_recommendation(metrics),

        "revenue_opportunity":
            revenue_opportunity(metrics),

        "risk_analysis":
            risk_analysis(metrics),

        "action_items":
            action_items(metrics)
    }