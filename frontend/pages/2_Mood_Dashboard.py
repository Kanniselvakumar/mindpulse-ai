from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.ui import apply_branding, render_notifications, render_sidebar_profile
from shared.gateway import bootstrap, get_dashboard


st.set_page_config(page_title="Mood Dashboard", page_icon="\U0001F4CA", layout="wide", initial_sidebar_state="collapsed")

bootstrap()
apply_branding()
profile = render_sidebar_profile()

st.title("Smart Mood Tracking Dashboard")
st.caption("Weekly and monthly signals linked to sleep, attendance, social connection, and exam pressure.")
filter_col, _ = st.columns([1.2, 4])
with filter_col:
    days = st.selectbox("Dashboard window", options=[7, 14, 30, 60], index=2)

dashboard = get_dashboard(profile["user_id"], days=days)
timeline = pd.DataFrame(dashboard["timeline"])
risk_distribution = pd.DataFrame(dashboard["risk_distribution"])

top1, top2, top3, top4 = st.columns(4)
top1.metric("Average Mood", dashboard["metrics"]["average_mood"])
top2.metric("Average Stress", dashboard["metrics"]["average_stress"])
top3.metric("Average Sleep", f"{dashboard['metrics']['average_sleep']} hrs")
top4.metric("High-Risk Days", dashboard["metrics"]["high_risk_days"])

render_notifications(dashboard["notifications"])

if timeline.empty:
    st.info("No dashboard data yet. Complete a check-in first.")
else:
    row1, row2 = st.columns(2)

    with row1:
        trend_df = timeline[["log_date", "mood_score", "stress_score", "sleep_hours"]].melt(
            id_vars="log_date",
            var_name="signal",
            value_name="value",
        )
        fig = px.line(
            trend_df,
            x="log_date",
            y="value",
            color="signal",
            markers=True,
            color_discrete_sequence=["#4F9D9D", "#6C8EF5", "#A8E6CF"],
        )
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with row2:
        scatter = px.scatter(
            timeline,
            x="sleep_hours",
            y="mood_score",
            color="risk_level",
            size="stress_score",
            hover_data=["log_date", "mood_label", "attendance_rate"],
            color_discrete_map={
                "Normal": "#A8E6CF",
                "Stressed": "#FFD166",
                "High Risk": "#FF6B6B",
            },
        )
        scatter.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(scatter, use_container_width=True)

    lower1, lower2 = st.columns(2)
    with lower1:
        if not risk_distribution.empty:
            risk_chart = px.bar(
                risk_distribution,
                x="risk_level",
                y="count",
                color="risk_level",
                color_discrete_map={
                    "Normal": "#A8E6CF",
                    "Stressed": "#FFD166",
                    "High Risk": "#FF6B6B",
                },
            )
            risk_chart.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(risk_chart, use_container_width=True)

    with lower2:
        st.subheader("Insights")
        for insight in dashboard["insights"]:
            st.markdown(f"- {insight}")
        if dashboard["badges"]:
            st.subheader("Badges")
            for badge in dashboard["badges"]:
                st.markdown(f"- {badge}")

    forecast = pd.DataFrame(dashboard["forecast"])
    if not forecast.empty:
        st.subheader("ML-Based Low-Day Forecast")
        st.dataframe(forecast, use_container_width=True)

