from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.ui import apply_branding, render_sidebar_profile
from shared.gateway import bootstrap, get_admin_overview


st.set_page_config(page_title="Counselor Insights", page_icon="\U0001F6E1", layout="wide", initial_sidebar_state="collapsed")

bootstrap()
apply_branding()
profile = render_sidebar_profile()

if profile["role"] not in {"counselor", "admin"}:
    st.title("Counselor Dashboard")
    st.error("This page is restricted to counselor or admin accounts.")
    st.caption("Use the seeded demo counselor login: counselor@studentwellness.local / Counselor@123")
    st.stop()

st.title("Counselor Dashboard")
st.caption("Aggregate-only wellness analytics. No individual journals or private notes are exposed here.")
filter_col, _ = st.columns([1.2, 4])
with filter_col:
    days = st.selectbox("Aggregate window", options=[14, 30, 60], index=1)

overview = get_admin_overview(days)
st.info(overview["privacy_note"])

metrics = overview["overall_metrics"]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Students", metrics["active_students"])
col2.metric("Average Mood", metrics["average_mood"])
col3.metric("Average Stress", metrics["average_stress"])
col4.metric("High-Risk Students", metrics["high_risk_students"])

risk_df = pd.DataFrame(overview["risk_distribution"])
course_df = pd.DataFrame(overview["course_distribution"])
timeline_df = pd.DataFrame(overview["timeline"])

row1, row2 = st.columns(2)
with row1:
    if not risk_df.empty:
        fig = px.pie(
            risk_df,
            names="risk_level",
            values="count",
            color="risk_level",
            color_discrete_map={
                "Normal": "#A8E6CF",
                "Stressed": "#FFD166",
                "High Risk": "#FF6B6B",
            },
        )
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

with row2:
    if not course_df.empty:
        bar = px.bar(course_df, x="course", y="count", color="course", height=340)
        bar.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(bar, use_container_width=True)

if not timeline_df.empty:
    st.subheader("Wellness Trend Line")
    trend = px.line(
        timeline_df,
        x="log_date",
        y=["average_mood", "average_stress"],
        markers=True,
        color_discrete_sequence=["#4F9D9D", "#6C8EF5"],
    )
    trend.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(trend, use_container_width=True)

