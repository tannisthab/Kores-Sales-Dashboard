"""
ai_analysis.py
--------------
Business Intelligence Analysis Engine

Produces rich business metrics for the AI Business Consultant.
"""

import numpy as np
import pandas as pd

from components.utils import forecast_next_month


# ==========================================================
# SALES TREND
# ==========================================================

def get_trend(monthly_df):

    if len(monthly_df) < 2:
        return "Stable"

    first = monthly_df.iloc[0]["Sales"]
    last = monthly_df.iloc[-1]["Sales"]

    change = ((last - first) / max(first, 1)) * 100

    if change >= 5:
        return "Upward"

    if change <= -5:
        return "Downward"

    return "Stable"


# ==========================================================
# SALES VOLATILITY
# ==========================================================

def get_volatility(monthly_df):

    mean = monthly_df["Sales"].mean()

    if mean == 0:
        return 0

    return float(monthly_df["Sales"].std() / mean)


# ==========================================================
# BUSINESS RISK
# ==========================================================

def get_risk(monthly_df, forecast_info):

    cv = get_volatility(monthly_df)

    confidence = forecast_info["confidence"]

    if cv < 0.15 and confidence == "High":
        return "Low"

    if cv < 0.35:
        return "Medium"

    return "High"


# ==========================================================
# CATEGORY PERFORMANCE
# ==========================================================

def category_summary(filtered_df):

    category = (
        filtered_df
        .groupby("Category", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Products=("Material descp", "nunique")
        )
        .sort_values("Sales", ascending=False)
        .reset_index(drop=True)
    )

    total = category["Sales"].sum()

    if total > 0:
        category["Contribution"] = (
            category["Sales"] / total * 100
        )
    else:
        category["Contribution"] = 0

    return category


# ==========================================================
# PRODUCT PERFORMANCE
# ==========================================================

def product_summary(filtered_df):

    return (
        filtered_df
        .groupby("Material descp", as_index=False)
        .agg(
            Sales=("Sales", "sum")
        )
        .sort_values("Sales", ascending=False)
        .reset_index(drop=True)
    )


# ==========================================================
# ZERO SALES PRODUCTS
# ==========================================================

def zero_sales_products(product_df):

    return product_df.loc[
        product_df["Sales"] <= 0,
        "Material descp"
    ].tolist()


# ==========================================================
# DECLINING MONTHS
# ==========================================================

def declining_months(monthly_df):

    growth = monthly_df["Sales"].pct_change() * 100

    decline = growth[growth < 0]

    return len(decline)


# ==========================================================
# GROWING MONTHS
# ==========================================================

def growing_months(monthly_df):

    growth = monthly_df["Sales"].pct_change() * 100

    increase = growth[growth > 0]

    return len(increase)


# ==========================================================
# TOP CATEGORY
# ==========================================================

def best_category(category_df):

    if category_df.empty:
        return None

    return category_df.iloc[0]


# ==========================================================
# LOWEST CATEGORY
# ==========================================================

def worst_category(category_df):

    if category_df.empty:
        return None

    return category_df.iloc[-1]


# ==========================================================
# TOP PRODUCT
# ==========================================================

def best_product(product_df):

    if product_df.empty:
        return None

    return product_df.iloc[0]


# ==========================================================
# LOWEST PRODUCT
# ==========================================================

def worst_product(product_df):

    if product_df.empty:
        return None

    return product_df.iloc[-1]
# ==========================================================
# MAIN ANALYSIS
# ==========================================================

def analyse_business(filtered_df, monthly_df):

    forecast_info = forecast_next_month(monthly_df)

    category_df = category_summary(filtered_df)
    product_df = product_summary(filtered_df)

    top_category = best_category(category_df)
    bottom_category = worst_category(category_df)

    top_product = best_product(product_df)
    bottom_product = worst_product(product_df)

    zero_products = zero_sales_products(product_df)

    trend = get_trend(monthly_df)
    volatility = get_volatility(monthly_df)
    risk = get_risk(monthly_df, forecast_info)

    growth = monthly_df["Sales"].pct_change() * 100

    positive_months = growing_months(monthly_df)
    negative_months = declining_months(monthly_df)

    # =====================================================
    # BUSINESS HEALTH SCORE
    # =====================================================

    score = 50

    if trend == "Upward":
        score += 15
    elif trend == "Stable":
        score += 10

    if forecast_info["confidence"] == "High":
        score += 15
    elif forecast_info["confidence"] == "Moderate":
        score += 8

    if positive_months > negative_months:
        score += 10

    if volatility < 0.15:
        score += 10
    elif volatility < 0.30:
        score += 5

    if len(zero_products) == 0:
        score += 10
    elif len(zero_products) < 5:
        score += 5

    score = max(0, min(score, 100))

    # =====================================================
    # BUSINESS RATING
    # =====================================================

    if score >= 90:
        rating = "Excellent"

    elif score >= 80:
        rating = "Very Good"

    elif score >= 70:
        rating = "Good"

    elif score >= 60:
        rating = "Average"

    else:
        rating = "Needs Attention"

    # =====================================================
    # BASIC SALES STATS
    # =====================================================

    highest_month = monthly_df.loc[
        monthly_df["Sales"].idxmax()
    ]

    lowest_month = monthly_df.loc[
        monthly_df["Sales"].idxmin()
    ]

    first_sales = monthly_df.iloc[0]["Sales"]
    last_sales = monthly_df.iloc[-1]["Sales"]

    overall_growth = (
        (last_sales - first_sales)
        /
        max(first_sales, 1)
    ) * 100

    # =====================================================
    # CATEGORY INSIGHTS
    # =====================================================

    if top_category is not None:

        best_category_name = top_category["Category"]
        best_category_sales = float(top_category["Sales"])
        best_category_share = float(top_category["Contribution"])

    else:

        best_category_name = "N/A"
        best_category_sales = 0
        best_category_share = 0

    if bottom_category is not None:

        worst_category_name = bottom_category["Category"]
        worst_category_sales = float(bottom_category["Sales"])

    else:

        worst_category_name = "N/A"
        worst_category_sales = 0

    # =====================================================
    # PRODUCT INSIGHTS
    # =====================================================

    if top_product is not None:

        best_product_name = top_product["Material descp"]
        best_product_sales = float(top_product["Sales"])

    else:

        best_product_name = "N/A"
        best_product_sales = 0

    if bottom_product is not None:

        worst_product_name = bottom_product["Material descp"]
        worst_product_sales = float(bottom_product["Sales"])

    else:

        worst_product_name = "N/A"
        worst_product_sales = 0
    # =====================================================
    # REVENUE OPPORTUNITY
    # =====================================================

    revenue_opportunity = ""

    if best_category_share >= 50:

        revenue_opportunity = (
            f"{best_category_name} contributes "
            f"{best_category_share:.1f}% of total sales. "
            "The business is highly dependent on this category. "
            "Cross-selling complementary products can increase revenue while "
            "reducing dependence on a single category."
        )

    elif best_category_share >= 30:

        revenue_opportunity = (
            f"{best_category_name} is the leading revenue contributor "
            f"({best_category_share:.1f}% share). "
            "Increasing distributor coverage and promotional campaigns for "
            "this category could significantly improve overall sales."
        )

    else:

        revenue_opportunity = (
            "Sales are well distributed across multiple categories. "
            "Rather than focusing on one category, increasing sales of the "
            "top three categories together is likely to generate higher revenue."
        )

    # =====================================================
    # ROOT CAUSE OF MARKET CONDITION
    # =====================================================

    decline_reason = []

    if overall_growth < 0:
        decline_reason.append(
            "overall sales have declined compared with the beginning of the selected period"
        )

    if negative_months > positive_months:
        decline_reason.append(
            "more months recorded negative growth than positive growth"
        )

    if volatility > 0.35:
        decline_reason.append(
            "monthly demand is highly volatile"
        )

    if len(zero_products) > 0:
        decline_reason.append(
            f"{len(zero_products)} products generated zero sales"
        )

    if worst_category_sales == 0:
        decline_reason.append(
            f"the '{worst_category_name}' category produced no revenue"
        )

    if not decline_reason:

        decline_reason.append(
            "sales remain relatively stable with no major warning signals"
        )

    # =====================================================
    # INVENTORY STRATEGY
    # =====================================================

    if trend == "Upward":

        inventory_strategy = (
            "Increase inventory for the highest-selling products while maintaining "
            "adequate safety stock."
        )

    elif trend == "Downward":

        inventory_strategy = (
            "Reduce procurement of slow-moving items and closely monitor stock ageing."
        )

    else:

        inventory_strategy = (
            "Maintain current inventory levels and review replenishment monthly."
        )

    # =====================================================
    # ACTION ITEMS
    # =====================================================

    actions = []

    if trend == "Downward":
        actions.append("Investigate declining sales across recent months.")

    if len(zero_products) > 0:
        actions.append("Review products with zero sales and discontinue or relaunch them.")

    if best_category_share > 50:
        actions.append("Reduce dependency on one category by promoting other categories.")

    if volatility > 0.30:
        actions.append("Improve demand forecasting to reduce sales volatility.")

    actions.append("Increase focus on the best-performing products.")

    actions.append("Review monthly dashboard before procurement decisions.")

    actions = actions[:5]

    # =====================================================
    # METRICS DICTIONARY
    # =====================================================

    metrics = {

        "health_score": score,

        "rating": rating,

        "trend": trend,

        "risk": risk,

        "volatility": round(volatility, 3),

        "overall_growth": round(overall_growth, 2),

        "average_sales": float(monthly_df["Sales"].mean()),

        "total_sales": float(monthly_df["Sales"].sum()),

        "maximum_sales": float(monthly_df["Sales"].max()),

        "minimum_sales": float(monthly_df["Sales"].min()),

        "highest_month": highest_month["MonthLabel"],

        "lowest_month": lowest_month["MonthLabel"],

        "positive_growth_months": positive_months,

        "negative_growth_months": negative_months,

        "forecast_confidence": forecast_info["confidence"],

        "forecast_value": forecast_info["forecast_value"],

        "best_category": best_category_name,

        "best_category_sales": best_category_sales,

        "best_category_share": best_category_share,

        "worst_category": worst_category_name,

        "worst_category_sales": worst_category_sales,

        "best_product": best_product_name,

        "best_product_sales": best_product_sales,

        "worst_product": worst_product_name,

        "worst_product_sales": worst_product_sales,

        "zero_sales_products": zero_products,

        "zero_sales_count": len(zero_products),

        "revenue_opportunity": revenue_opportunity,

        "decline_reason": decline_reason,

        "inventory_strategy": inventory_strategy,

        "action_items": actions,

    }

    return metrics