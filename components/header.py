"""
header.py
---------
Renders the corporate header bar: Kores logo, company name and the
dashboard title. Uses base64-embedded image so it renders reliably
inside a styled flex container.
"""

import base64
import os
import streamlit as st


def _get_base64_image(image_path: str) -> str:
    """Reads an image file from disk and returns a base64 string."""
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def render_header(logo_path: str = "assets/kores_logo.png") -> None:
    """
    Renders the fixed corporate header:
      [Logo]  KORES INDIA LTD.
              Sales Trend Analysis Dashboard
    """
    logo_b64 = _get_base64_image(logo_path)

    if logo_b64:
        logo_html = (
            f'<img src="data:image/png;base64,{logo_b64}" '
            f'style="height:52px;width:52px;border-radius:50%;'
            f'background:#FFFFFF;padding:3px;box-shadow:0 1px 4px rgba(0,0,0,0.2);" />'
        )
    else:
        logo_html = (
            '<div style="height:52px;width:52px;border-radius:50%;'
            'background:#FFFFFF;display:flex;align-items:center;justify-content:center;'
            'font-weight:800;color:#0A2E5C;font-size:20px;">K</div>'
        )

    st.markdown(
        f"""
        <div class="kores-header">
            {logo_html}
            <div>
                <p class="kores-header-title">KORES INDIA LTD.</p>
                <p class="kores-header-subtitle">Sales Trend Analysis Dashboard</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
