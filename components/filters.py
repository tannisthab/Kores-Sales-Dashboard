"""
filters.py
----------
Renders the left-hand fixed product filter panel:
  - Category selector
  - Material Description selector (wide, full text visible)
  - An info box echoing the current selection

Returns the filtered DataFrame plus the selected values so other
components (summary, charts, insights) can reuse them.
"""

import streamlit as st
import pandas as pd


def render_filters(df: pd.DataFrame):
    """
    Renders the product filter panel and returns:
        (filtered_df, selected_category, selected_material)
    """
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.markdown('<p class="filter-panel-title">Product Filter</p>', unsafe_allow_html=True)

    categories = sorted(df["Category"].dropna().unique().tolist())
    category_options = ["All Categories"] + categories

    selected_category = st.selectbox(
        "Category",
        options=category_options,
        index=0,
        key="filter_category",
    )

    if selected_category != "All Categories":
        material_pool = df[df["Category"] == selected_category]
    else:
        material_pool = df

    materials = sorted(material_pool["Material descp"].dropna().unique().tolist())
    material_options = ["All Materials"] + materials

    selected_material = st.selectbox(
        "Material Description",
        options=material_options,
        index=0,
        key="filter_material",
        help="Full material description is shown below the dropdown.",
    )

    # Apply filters
    filtered_df = df.copy()
    if selected_category != "All Categories":
        filtered_df = filtered_df[filtered_df["Category"] == selected_category]
    if selected_material != "All Materials":
        filtered_df = filtered_df[filtered_df["Material descp"] == selected_material]

    # Selection summary box (full text always visible, wraps naturally)
    display_category = selected_category if selected_category != "All Categories" else "All Categories"
    display_material = selected_material if selected_material != "All Materials" else "All Materials"

    st.markdown(
        f"""
        <div class="filter-info-box">
            <p class="filter-info-label">Category</p>
            <p class="filter-info-value">{display_category}</p>
            <p class="filter-info-label">Material Description</p>
            <p class="filter-info-value">{display_material}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    return filtered_df, selected_category, selected_material