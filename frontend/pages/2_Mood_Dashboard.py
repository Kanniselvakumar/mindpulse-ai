from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from frontend.ui import apply_branding, get_logo_data_uri, render_notifications, render_sidebar_profile
from shared.gateway import bootstrap, get_dashboard, get_upcoming_events


st.set_page_config(page_title="Mood Dashboard - MindPulse AI", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

bootstrap()
apply_branding()
profile = render_sidebar_profile()

logo_src = get_logo_data_uri()
logo_img = f'<img src="{logo_src}" style="width: 38px; height: 38px; border-radius: 8px; margin-right: 0.6rem; vertical-align: middle;" alt="Logo"/>' if logo_src else ''
st.markdown(f"<div style='display:flex; align-items:center; margin-bottom: 0.2rem;'>{logo_img}<h1 style='margin:0; font-size: 2rem;'>Smart Mood Tracking Dashboard</h1></div>", unsafe_allow_html=True)
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

tab1, tab2, tab3, tab4 = st.tabs(["📈 Mood Trends", "😴 Sleep & Lifestyle", "📅 Academic Predictor", "🏅 Progress Tracker"])

# ─── Tab 1: Mood Trends (original dashboard) ──────────────────────────────────
with tab1:
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
                title="Mood · Stress · Sleep Over Time",
                color_discrete_sequence=["#14B8A6", "#6366F1", "#2DD4BF"],
            )
            fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with row2:
            scatter = px.scatter(
                timeline,
                x="sleep_hours",
                y="mood_score",
                color="risk_level",
                size="stress_score",
                hover_data=["log_date", "mood_label", "attendance_rate"],
                title="Sleep vs Mood (sized by Stress)",
                color_discrete_map={
                    "Normal": "#10B981",
                    "Stressed": "#F59E0B",
                    "High Risk": "#F43F5E",
                },
            )
            scatter.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(scatter, use_container_width=True)

        lower1, lower2 = st.columns(2)
        with lower1:
            if not risk_distribution.empty:
                risk_chart = px.bar(
                    risk_distribution,
                    x="risk_level",
                    y="count",
                    color="risk_level",
                    title="Risk Level Distribution",
                    color_discrete_map={
                        "Normal": "#10B981",
                        "Stressed": "#F59E0B",
                        "High Risk": "#F43F5E",
                    },
                )
                risk_chart.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
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

# ─── Tab 2: Sleep & Lifestyle Tracker ─────────────────────────────────────────
with tab2:
    st.subheader("😴 Sleep & Lifestyle Tracker")
    if timeline.empty:
        st.info("Complete a few check-ins to unlock your sleep analytics.")
    else:
        avg_sleep = float(timeline["sleep_hours"].mean())
        sleep_debt = max(0.0, 8.0 - avg_sleep)
        recommended = 8.0

        m1, m2, m3 = st.columns(3)
        m1.metric("Average Sleep", f"{avg_sleep:.1f} hrs", delta=f"{avg_sleep - recommended:.1f} hrs vs target")
        m2.metric("Sleep Debt (avg)", f"{sleep_debt:.1f} hrs", delta=None)
        total_debt = max(0.0, (recommended - avg_sleep) * len(timeline))
        m3.metric("Cumulative Debt", f"{total_debt:.0f} hrs over {len(timeline)} days")

        if sleep_debt > 1.5:
            st.warning(f"⚠️ You're averaging {sleep_debt:.1f} hours below the recommended 8 hours. Chronic sleep debt amplifies stress and impacts concentration.")
        elif sleep_debt < 0.5:
            st.success("✅ Your average sleep is close to ideal. Keep maintaining this routine!")

        # Weekly sleep bar chart
        sleep_fig = px.bar(
            timeline,
            x="log_date",
            y="sleep_hours",
            title="Daily Sleep Hours",
            color="sleep_hours",
            color_continuous_scale=["#F43F5E", "#F59E0B", "#10B981"],
            range_color=[4.0, 9.0],
        )
        sleep_fig.add_hline(y=8.0, line_dash="dash", line_color="#6366F1", annotation_text="Target: 8 hrs")
        sleep_fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(sleep_fig, use_container_width=True)

        # Sleep vs Mood correlation
        corr_col1, corr_col2 = st.columns(2)
        with corr_col1:
            wanted_cols = ["sleep_hours", "mood_score", "stress_score", "energy_score"]
            avail_cols = [c for c in wanted_cols if c in timeline.columns]
            corr = timeline[avail_cols].corr()
            sleep_corr = corr["sleep_hours"].drop("sleep_hours")
            corr_fig = go.Figure(go.Bar(
                x=sleep_corr.index.tolist(),
                y=sleep_corr.values.tolist(),
                marker_color=["#10B981" if v > 0 else "#F43F5E" for v in sleep_corr.values],
            ))
            corr_fig.update_layout(title="Sleep Correlation with Wellness Signals", height=300, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(corr_fig, use_container_width=True)

        with corr_col2:
            st.subheader("💡 Sleep Recommendations")
            if avg_sleep < 5.5:
                st.error("🔴 Severely under-slept. Prioritize sleep above all else this week.")
                st.markdown("- Set a fixed bedtime reminder at 10 PM\n- Avoid screens 30 minutes before bed\n- Try a 4-7-8 breathing exercise to fall asleep faster")
            elif avg_sleep < 7.0:
                st.warning("🟡 Mild sleep deficit detected.")
                st.markdown("- Aim to sleep 30 minutes earlier each night\n- Limit caffeine after 3 PM\n- Use the AI companion for an evening wind-down prompt")
            else:
                st.success("🟢 Sleep quality is good! Maintain your current routine.")
                st.markdown("- Keep your consistent sleep/wake schedule\n- Protect your sleep window during exam weeks")

# ─── Tab 3: Academic Calendar Stress Predictor ────────────────────────────────
with tab3:
    st.subheader("📅 Academic Calendar Stress Predictor")

    try:
        events = get_upcoming_events(days_ahead=14)
    except Exception:
        events = []

    if not events:
        st.info("No upcoming academic events in the next 14 days. Enjoy a calm window!")
    else:
        st.caption("Upcoming high-stress academic events have been detected. Here are preemptive coping tips.")

        for event in events:
            event_date_str = event["event_date"]
            days_away = (date.fromisoformat(event_date_str) - date.today()).days
            stress_weight = event.get("stress_weight", 5)

            if stress_weight >= 8:
                color = "🔴"
                severity = "High"
            elif stress_weight >= 5:
                color = "🟡"
                severity = "Medium"
            else:
                color = "🟢"
                severity = "Low"

            with st.expander(f"{color} {event['event_name']} — {days_away} day(s) away ({event_date_str})", expanded=(days_away <= 5)):
                c1, c2 = st.columns(2)
                c1.metric("Stress Weight", f"{stress_weight}/10")
                c2.metric("Days Remaining", days_away)
                st.markdown(f"**Severity:** {severity}")

                if stress_weight >= 8:
                    st.markdown("""
**Preemptive Coping Tips:**
- Begin revision at least 5 days in advance
- Break syllabus into daily achievable chunks
- Sleep 7–8 hours consistently — memory consolidates during sleep
- Use the AI companion for an exam anxiety prompt
- Check in daily during this week to track your stress
                    """)
                elif stress_weight >= 5:
                    st.markdown("""
**Preemptive Coping Tips:**
- Review your progress and prioritise pending work
- Take 5-minute breaks every 45 minutes (Pomodoro)
- Discuss doubts with peers or faculty this week
                    """)
                else:
                    st.markdown("- Regular preparation is sufficient. Keep maintaining your routine.")

        # Timeline visualization
        events_df = pd.DataFrame(events)
        if not events_df.empty:
            events_df["days_away"] = events_df["event_date"].apply(
                lambda d: (date.fromisoformat(d) - date.today()).days
            )
            timeline_fig = px.scatter(
                events_df,
                x="event_date",
                y="stress_weight",
                size="stress_weight",
                color="event_type",
                hover_data=["event_name", "days_away"],
                title="Academic Events by Stress Impact",
                labels={"stress_weight": "Stress Weight", "event_date": "Date"},
            )
            timeline_fig.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(timeline_fig, use_container_width=True)

# ─── Tab 4: Progress & Recovery Tracker ───────────────────────────────────────
with tab4:
    st.subheader("🏅 Student Progress & Recovery Tracker")

    if timeline.empty:
        st.info("Start check-ins to track your wellness journey.")
    else:
        # Streaks
        good_days = int((timeline["mood_score"] >= 4).sum())
        checkin_streak = int(dashboard["metrics"].get("check_in_streak", 0))
        total_checkins = len(timeline)
        recovery_days = int(
            (
                (timeline["mood_score"].shift(1) < 3) &
                (timeline["mood_score"] >= 4)
            ).sum()
        )

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Check-in Streak", f"{checkin_streak} days 🔥")
        p2.metric("Good Mood Days", f"{good_days}/{total_checkins}")
        p3.metric("Recovery Days", f"{recovery_days} ✨")
        p4.metric("Total Check-ins", total_checkins)

        # Milestone celebrations
        if checkin_streak >= 7:
            st.success(f"🎉 Amazing! You've checked in for {checkin_streak} consecutive days. Consistency is the foundation of self-awareness!")
        elif checkin_streak >= 3:
            st.info(f"👍 {checkin_streak}-day check-in streak! Keep going — you're building a great habit.")

        if good_days >= 7:
            st.success(f"🌟 Milestone: You've had {good_days} good mood days in this window. Your strategies are working!")

        if recovery_days >= 2:
            st.info(f"💪 You've bounced back from a low day {recovery_days} times recently. That's remarkable resilience!")

        # Journey line chart
        timeline["mood_7day_avg"] = timeline["mood_score"].rolling(7, min_periods=1).mean()
        journey_fig = px.line(
            timeline,
            x="log_date",
            y=["mood_score", "mood_7day_avg"],
            title="Mood Journey — Daily vs 7-Day Rolling Average",
            color_discrete_map={"mood_score": "#64748B", "mood_7day_avg": "#14B8A6"},
            markers=False,
        )
        journey_fig.add_hrect(y0=4, y1=5, fillcolor="#10B981", opacity=0.1, annotation_text="Good Zone")
        journey_fig.add_hrect(y0=0, y1=2.5, fillcolor="#F43F5E", opacity=0.1, annotation_text="Watch Zone")
        journey_fig.update_layout(height=350, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(journey_fig, use_container_width=True)

        # Risk journey pie
        if not risk_distribution.empty:
            pie_fig = px.pie(
                risk_distribution,
                names="risk_level",
                values="count",
                title="Risk Level Journey Breakdown",
                color="risk_level",
                color_discrete_map={
                    "Normal": "#10B981",
                    "Stressed": "#F59E0B",
                    "High Risk": "#F43F5E",
                },
                hole=0.45,
            )
            pie_fig.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(pie_fig, use_container_width=True)
