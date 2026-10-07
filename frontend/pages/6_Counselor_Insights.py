from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.ui import apply_branding, get_logo_data_uri, render_sidebar_profile
from shared.gateway import (
    bootstrap,
    get_admin_overview,
    get_appointments,
    get_cohort_overview,
    update_appointment_status,
)


st.set_page_config(page_title="Counselor Insights - MindPulse AI", page_icon="🛡", layout="wide", initial_sidebar_state="collapsed")

bootstrap()
apply_branding()
profile = render_sidebar_profile()

logo_src = get_logo_data_uri()
logo_img = f'<img src="{logo_src}" style="width: 38px; height: 38px; border-radius: 8px; margin-right: 0.6rem; vertical-align: middle;" alt="Logo"/>' if logo_src else ''

if profile["role"] not in {"counselor", "admin"}:
    st.markdown(f"<div style='display:flex; align-items:center; margin-bottom: 0.2rem;'>{logo_img}<h1 style='margin:0; font-size: 2rem;'>Counselor Dashboard</h1></div>", unsafe_allow_html=True)
    st.error("This page is restricted to counselor or admin accounts.")
    st.caption("Use the seeded demo counselor login: counselor@studentwellness.local / Counselor@123")
    st.stop()

st.markdown(f"<div style='display:flex; align-items:center; margin-bottom: 0.2rem;'>{logo_img}<h1 style='margin:0; font-size: 2rem;'>Counselor Dashboard</h1></div>", unsafe_allow_html=True)
st.caption("Aggregate-only wellness analytics. No individual journals or private notes are exposed here.")

st.info("⚡ **Looking to train models on custom student datasets or view real-time data streaming?** Navigate to the **[Realtime & Datasets Studio](pages/7_Realtime_Dataset_Studio.py)** from the top navigation bar!")

filter_col, _ = st.columns([1.2, 4])

with filter_col:
    days = st.selectbox("Aggregate window", options=[14, 30, 60], index=1)

tab1, tab2, tab3 = st.tabs(["📊 Aggregate Analytics", "🗺️ Cohort Heatmaps", "📅 Appointment Manager"])

# ─── Tab 1: Original Aggregate Analytics ──────────────────────────────────────
with tab1:
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
                title="Campus Risk Distribution",
                color_discrete_map={
                    "Normal": "#10B981",
                    "Stressed": "#F59E0B",
                    "High Risk": "#F43F5E",
                },
                hole=0.45,
            )
            fig.update_layout(height=340, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)

    with row2:
        if not course_df.empty:
            bar = px.bar(course_df, x="course", y="count", color="course", height=340, title="Students per Course")
            bar.update_layout(margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
            st.plotly_chart(bar, use_container_width=True)

    if not timeline_df.empty:
        st.subheader("Wellness Trend Line")
        trend = px.line(
            timeline_df,
            x="log_date",
            y=["average_mood", "average_stress"],
            markers=True,
            title="Campus-Wide Mood vs Stress Over Time",
            color_discrete_sequence=["#14B8A6", "#6366F1"],
        )
        trend.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(trend, use_container_width=True)

# ─── Tab 2: Cohort Heatmaps ────────────────────────────────────────────────────
with tab2:
    st.subheader("🗺️ Group & Cohort Stress Analytics")
    st.caption("Identify department-wide or batch-wide stress patterns. No individual data is shown.")

    cohort = get_cohort_overview(days)
    st.info(cohort["privacy_note"])

    dept_df = pd.DataFrame(cohort["department_heatmap"])
    year_df = pd.DataFrame(cohort["year_heatmap"])

    h1, h2 = st.columns(2)
    with h1:
        if not dept_df.empty:
            dept_fig = px.bar(
                dept_df,
                x="department",
                y="avg_stress",
                color="avg_stress",
                color_continuous_scale=["#10B981", "#F59E0B", "#F43F5E"],
                range_color=[2, 8],
                hover_data=["avg_mood", "high_risk_count", "student_count"],
                title="Average Stress by Department",
                labels={"avg_stress": "Avg Stress", "department": "Department"},
            )
            dept_fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(dept_fig, use_container_width=True)
        else:
            st.info("No department data available yet.")

    with h2:
        if not year_df.empty:
            year_fig = px.bar(
                year_df,
                x="year",
                y="avg_stress",
                color="avg_stress",
                color_continuous_scale=["#10B981", "#F59E0B", "#F43F5E"],
                range_color=[2, 8],
                hover_data=["avg_mood", "high_risk_count"],
                title="Average Stress by Academic Year",
                labels={"avg_stress": "Avg Stress", "year": "Year"},
            )
            year_fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(year_fig, use_container_width=True)
        else:
            st.info("No year-wise data available yet.")

    if not dept_df.empty:
        st.subheader("Department Overview Table")
        display_df = dept_df.rename(columns={
            "department": "Department",
            "avg_stress": "Avg Stress",
            "avg_mood": "Avg Mood",
            "high_risk_count": "High Risk Count",
            "student_count": "Students",
        })
        st.dataframe(display_df, use_container_width=True)

    # Systemic alerts
    if not dept_df.empty:
        high_stress_depts = dept_df[dept_df["avg_stress"] > 6]
        if not high_stress_depts.empty:
            st.warning(
                f"⚠️ **Systemic Alert**: Departments with elevated average stress (>6): "
                f"{', '.join(high_stress_depts['department'].tolist())}. "
                "Consider scheduling a department-wide wellness intervention."
            )

# ─── Tab 3: Appointment Manager ────────────────────────────────────────────────
with tab3:
    st.subheader("📅 Student Appointment Requests")
    st.caption("Review, confirm, or cancel session requests from students.")

    appointments = get_appointments(profile["user_id"], role="counselor")

    if not appointments:
        st.info("No appointment requests found.")
    else:
        status_colors = {"pending": "🟡", "confirmed": "🟢", "completed": "✅", "cancelled": "🔴"}

        # Group by status
        pending = [a for a in appointments if a.get("status") == "pending"]
        others = [a for a in appointments if a.get("status") != "pending"]

        if pending:
            st.markdown(f"**{len(pending)} Pending Request(s)**")
            for appt in pending:
                appt_id = appt["id"]
                with st.expander(f"🟡 {appt['slot_time']} — Student: {appt['student_id']}", expanded=True):
                    st.write(f"**Reason:** {appt.get('reason', 'Not specified')}")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("✅ Confirm", key=f"confirm_{appt_id}"):
                            update_appointment_status(appt_id, "confirmed", notes="Confirmed by counselor.")
                            st.success("Appointment confirmed.")
                            st.rerun()

                    with col2:
                        if st.button("🏁 Complete", key=f"complete_{appt_id}"):
                            update_appointment_status(appt_id, "completed", notes="Session completed.")
                            st.success("Marked as completed.")
                            st.rerun()

                    with col3:
                        if st.button("❌ Cancel", key=f"cancel_{appt_id}"):
                            update_appointment_status(appt_id, "cancelled", notes="Cancelled by counselor.")
                            st.warning("Appointment cancelled.")
                            st.rerun()

        if others:
            st.divider()
            st.markdown("**Past / Resolved Appointments**")
            for appt in others:
                icon = status_colors.get(appt.get("status"), "⚪")
                with st.expander(f"{icon} {appt['slot_time']} — {appt.get('status', '').title()}"):
                    st.write(f"**Student ID:** {appt['student_id']}")
                    st.write(f"**Reason:** {appt.get('reason', 'Not specified')}")
                    if appt.get("notes"):
                        st.write(f"**Notes:** {appt['notes']}")
