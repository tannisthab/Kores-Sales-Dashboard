"""
utils.py
--------
Shared helper functions used across the Kores dashboard:
  - Loading & cleaning the Excel dataset
  - Deriving Year from the "Aug'24" style Month strings
  - Building chronological ordering of months
  - KPI calculations
  - Simple 3-month moving average forecast

All functions are pure / reusable and take a DataFrame as input,
so they can be unit-tested independently of Streamlit.
"""

import pandas as pd
import numpy as np
import re
import streamlit as st

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

MONTH_NAME = {v: k.capitalize() for k, v in MONTH_MAP.items()}


def _parse_month_token(token: str):
    """
    Parses a month token like "Aug'24" or "Aug-24" or "Aug24"
    into (month_number, full_year, sort_key).
    """
    token = str(token).strip()
    match = re.match(r"([A-Za-z]{3,})[\s'\-]?(\d{2,4})", token)
    if not match:
        return None, None, None

    mon_str = match.group(1)[:3].lower()
    yr_str = match.group(2)

    month_num = MONTH_MAP.get(mon_str)
    if month_num is None:
        return None, None, None

    year_num = int(yr_str)
    if year_num < 100:
        year_num += 2000

    sort_key = year_num * 100 + month_num
    return month_num, year_num, sort_key


@st.cache_data(show_spinner=False)
def load_data(file) -> pd.DataFrame:
    """
    Loads uploaded Excel file (sheet 'Data 1'), cleans column names,
    and derives Year / MonthNum / MonthLabel / SortKey / Quarter columns
    from the raw Month text (e.g. "Aug'24").
    """

    df = pd.read_excel(file, sheet_name="Data 1")

    # Normalise column names (strip whitespace)
    df.columns = [str(c).strip() for c in df.columns]

    required_cols = [
        "Category",
        "Material descp",
        "Month",
        "Sales QTY",
        "Growth Qty"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected column(s) in Excel file: {missing}")

    df = df.dropna(subset=["Month"]).copy()

    parsed = df["Month"].apply(_parse_month_token)
    df["MonthNum"] = parsed.apply(lambda x: x[0])
    df["Year"] = parsed.apply(lambda x: x[1])
    df["SortKey"] = parsed.apply(lambda x: x[2])

    df = df.dropna(subset=["Year", "MonthNum", "SortKey"]).copy()
    df["Year"] = df["Year"].astype(int)
    df["MonthNum"] = df["MonthNum"].astype(int)
    df["SortKey"] = df["SortKey"].astype(int)

    df["MonthLabel"] = df["Month"].astype(str).str.strip()
    df["MonthShort"] = df["MonthNum"].map(MONTH_NAME)
    df["Quarter"] = df["MonthNum"].apply(lambda m: f"Q{((m - 1) // 3) + 1}")

    df["Sales"] = pd.to_numeric(df["Sales QTY"], errors="coerce").fillna(0)
    df["QTY"] = pd.to_numeric(df["Growth Qty"], errors="coerce").fillna(0)

    df["Category"] = df["Category"].astype(str).str.strip()
    df["Material descp"] = df["Material descp"].astype(str).str.strip()

    df = df.sort_values("SortKey").reset_index(drop=True)
    return df


def get_month_order(df: pd.DataFrame) -> list:
    """Returns the unique MonthLabel values sorted chronologically."""
    order = (
        df[["MonthLabel", "SortKey"]]
        .drop_duplicates()
        .sort_values("SortKey")["MonthLabel"]
        .tolist()
    )
    return order


def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates Sales & QTY by MonthLabel, preserving chronological order."""
    grouped = (
        df.groupby(["MonthLabel", "SortKey", "MonthShort", "Year", "Quarter"], as_index=False)
        .agg(Sales=("Sales", "sum"), QTY=("QTY", "sum"))
        .sort_values("SortKey")
        .reset_index(drop=True)
    )
    return grouped


def calc_kpis(monthly_df: pd.DataFrame) -> dict:
    """
    Calculates the KPI set required for the summary cards:
    Average, Max, Min, Total, Growth %, Highest month, Lowest month.
    """
    if monthly_df.empty:
        return {
            "average": 0, "maximum": 0, "minimum": 0, "total": 0,
            "growth_pct": 0, "highest_month": "N/A", "lowest_month": "N/A",
        }

    total = monthly_df["Sales"].sum()
    average = monthly_df["Sales"].mean()
    maximum = monthly_df["Sales"].max()
    minimum = monthly_df["Sales"].min()

    highest_row = monthly_df.loc[monthly_df["Sales"].idxmax()]
    lowest_row = monthly_df.loc[monthly_df["Sales"].idxmin()]

    first_val = monthly_df.iloc[0]["Sales"]
    last_val = monthly_df.iloc[-1]["Sales"]
    growth_pct = ((last_val - first_val) / first_val * 100) if first_val else 0

    return {
        "average": average,
        "maximum": maximum,
        "minimum": minimum,
        "total": total,
        "growth_pct": growth_pct,
        "highest_month": highest_row["MonthLabel"],
        "lowest_month": lowest_row["MonthLabel"],
    }


def forecast_next_month(monthly_df: pd.DataFrame) -> dict:
    """
    Forecasts next month's sales using the average of the previous
    3 months. Also derives a simple confidence measure (based on the
    coefficient of variation of those 3 months) and a business
    recommendation string.
    """
    if monthly_df.empty or len(monthly_df) < 1:
        return {
            "forecast_value": 0, "confidence": "Low", "confidence_pct": 0,
            "recommendation": "Insufficient data to generate a forecast.",
            "basis_months": [],
        }

    n = min(3, len(monthly_df))
    last_n = monthly_df.tail(n)
    values = last_n["Sales"].values
    forecast_value = float(np.mean(values))

    std = float(np.std(values)) if len(values) > 1 else 0.0
    mean_val = float(np.mean(values)) if np.mean(values) != 0 else 1.0
    cv = std / mean_val

    if cv < 0.10:
        confidence, confidence_pct = "High", 90
    elif cv < 0.25:
        confidence, confidence_pct = "Moderate", 70
    else:
        confidence, confidence_pct = "Low", 45

    last_actual = float(monthly_df.iloc[-1]["Sales"])
    if forecast_value > last_actual * 1.05:
        recommendation = (
            "Sales are projected to rise next month. Ensure adequate stock "
            "and production capacity to meet anticipated demand."
        )
    elif forecast_value < last_actual * 0.95:
        recommendation = (
            "A slowdown is projected next month. Consider targeted promotions "
            "or channel incentives to sustain momentum."
        )
    else:
        recommendation = (
            "Sales are expected to remain stable next month. Maintain current "
            "operational and inventory plans."
        )

    return {
        "forecast_value": forecast_value,
        "confidence": confidence,
        "confidence_pct": confidence_pct,
        "recommendation": recommendation,
        "basis_months": last_n["MonthLabel"].tolist(),
    }


def format_inr(value) -> str:
    """Formats a number in Indian-style currency notation, e.g. 12,34,567."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return str(value)

    is_negative = value < 0
    value = abs(value)
    s = f"{value:,.0f}"
    # Convert standard comma grouping to Indian digit grouping
    parts = s.split(",")
    if len(parts) > 1:
        last3 = parts[-1]
        rest = "".join(parts[:-1])
        rest_digits = rest
        groups = []
        while len(rest_digits) > 2:
            groups.insert(0, rest_digits[-2:])
            rest_digits = rest_digits[:-2]
        if rest_digits:
            groups.insert(0, rest_digits)
        s = ",".join(groups + [last3])

    return f"{'-' if is_negative else ''}₹{s}"

def format_inr_short(value) -> str:
    """
    Formats numbers in Indian business style.

    Examples:
    125000      -> ₹1.25 L
    131274025   -> ₹13.13 Cr
    """

    try:
        value = float(value)
    except (TypeError, ValueError):
        return str(value)

    negative = value < 0
    value = abs(value)

    if value >= 10000000:          # 1 Crore
        text = f"₹{value/10000000:.2f} Cr"
    elif value >= 100000:          # 1 Lakh
        text = f"₹{value/100000:.2f} L"
    elif value >= 1000:
        text = f"₹{value/1000:.2f} K"
    else:
        text = f"₹{value:.0f}"

    return f"-{text}" if negative else text
def format_lakh(value):
    """Returns values like 12.3 L or 2.45 Cr"""
    value = float(value)

    if abs(value) >= 10000000:      # 1 Crore
        return f"{value/10000000:.2f} Cr"

    elif abs(value) >= 100000:      # 1 Lakh
        return f"{value/100000:.2f} L"

    elif abs(value) >= 1000:
        return f"{value/1000:.1f} K"

    return f"{value:.0f}"


def lakhs(value):
    """Numeric value in lakhs."""
    return value / 100000