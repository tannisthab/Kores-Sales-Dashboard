"""
ai_analysis.py
--------------
Business Intelligence Analysis Engine

This module analyses the filtered dashboard data and returns
business metrics used by ai_writer.py.
"""

import pandas as pd
import numpy as np

from components.utils import forecast_next_month



# ==========================================================
# SALES TREND
# ==========================================================

def get_trend(monthly_df):

    first = monthly_df.iloc[0]["Sales"]
    last = monthly_df.iloc[-1]["Sales"]

    change = ((last-first)/max(first,1))*100

    if change > 5:
        return "Upward"

    elif change < -5:
        return "Downward"

    return "Stable"


# ==========================================================
# BUSINESS RISK
# ==========================================================

def get_risk(monthly_df, forecast_info):

    cv = monthly_df["Sales"].std()/max(monthly_df["Sales"].mean(),1)

    confidence = forecast_info["confidence"]

    if cv < 0.20 and confidence == "High":
        return "Low"

    elif cv < 0.40:
        return "Medium"

    return "High"


# ==========================================================
# BEST CATEGORY
# ==========================================================

def get_best_category(filtered_df):

    category_sales = (
        filtered_df
        .groupby("Category")["Sales"]
        .sum()
    )

    if category_sales.empty:
        return "N/A"

    return category_sales.idxmax()


# ==========================================================
# BEST PRODUCT
# ==========================================================

def get_best_product(filtered_df):

    product_sales = (
        filtered_df
        .groupby("Material descp")["Sales"]
        .sum()
    )

    if product_sales.empty:
        return "N/A"

    return product_sales.idxmax()


# ==========================================================
# MAIN ANALYSIS
# ==========================================================

def analyse_business(filtered_df, monthly_df):

    forecast_info = forecast_next_month(monthly_df)

    # Temporary Business Health Score

    growth = monthly_df["Sales"].pct_change() * 100

    positive = int((growth > 0).sum())

    negative = int((growth < 0).sum())

    score = 70

    if forecast_info["confidence"] == "High":
        score += 10
    elif forecast_info["confidence"] == "Moderate":
        score += 5

    if positive > negative:
        score += 10

    if monthly_df["Sales"].std() / monthly_df["Sales"].mean() < 0.20:
        score += 10

    score = min(score, 100)

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

    health_score = score

    growth = monthly_df["Sales"].pct_change()*100

    overall_growth = (
        (
            monthly_df.iloc[-1]["Sales"]
            -
            monthly_df.iloc[0]["Sales"]
        )
        /
        max(monthly_df.iloc[0]["Sales"],1)
    )*100

    highest = monthly_df.loc[
        monthly_df["Sales"].idxmax()
    ]

    lowest = monthly_df.loc[
        monthly_df["Sales"].idxmin()
    ]

    positive = int((growth>0).sum())

    negative = int((growth<0).sum())

    metrics = {

        "health_score": health_score,

        "rating": rating,

        "overall_growth": round(overall_growth,2),

        "average_sales": round(
            monthly_df["Sales"].mean(),
            2
        ),

        "total_sales": round(
            monthly_df["Sales"].sum(),
            2
        ),

        "maximum_sales": round(
            monthly_df["Sales"].max(),
            2
        ),

        "minimum_sales": round(
            monthly_df["Sales"].min(),
            2
        ),

        "highest_month":
            highest["MonthLabel"],

        "lowest_month":
            lowest["MonthLabel"],

        "positive_growth_months":
            positive,

        "negative_growth_months":
            negative,

        "trend":
            get_trend(monthly_df),

        "risk":
            get_risk(
                monthly_df,
                forecast_info
            ),

        "forecast_confidence":
            forecast_info["confidence"],

        "forecast_value":
            forecast_info["forecast_value"],

        "best_category":
            get_best_category(filtered_df),

        "best_product":
            get_best_product(filtered_df),

        "volatility":
            round(monthly_df["Sales"].std(),2)

    }

    return metrics