from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.ui import apply_branding, render_notifications, render_sidebar_profile
from shared.gateway import bootstrap, get_dashboard, get_ml_overview, get_resources


st.set_page_config(
    page_title="MindPulse AI",
    page_icon="\U0001F9E0",
    layout="wide",
    initial_sidebar_state="collapsed",
)

bootstrap()
apply_branding()
profile = render_sidebar_profile()
dashboard = get_dashboard(profile["user_id"], days=30)
latest = dashboard.get("latest_entry") or {}
resource_pack = get_resources(profile["campus"], latest.get("risk_level", "Normal"))
ml_overview = get_ml_overview()

st.markdown(
    """
    <div class="hero-panel">
        <span class="brand-kicker">MindPulse AI</span>
        <h1>Calm signals for student wellbeing.</h1>
        <p>
            Track mood, connect academic pressure to wellbeing, and surface support before stress
            grows into burnout.
        </p>
        <div class="brand-pill-row">
            <span class="brand-pill">NLP Journal Signals</span>
            <span class="brand-pill">ML Risk Detection</span>
            <span class="brand-pill">Privacy-First Support</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Mood", dashboard["metrics"]["average_mood"])
col2.metric("Avg Stress", dashboard["metrics"]["average_stress"])
col3.metric("Sleep Avg", f"{dashboard['metrics']['average_sleep']} hrs")
col4.metric("Check-in Streak", dashboard["metrics"]["check_in_streak"])

left, right = st.columns([1.7, 1.1])

with left:
    st.subheader("Mood and Stress Timeline")
    timeline = pd.DataFrame(dashboard["timeline"])
    if not timeline.empty:
        plot_df = timeline[["log_date", "mood_score", "stress_score"]].melt(
            id_vars="log_date",
            var_name="signal",
            value_name="score",
        )
        fig = px.line(
            plot_df,
            x="log_date",
            y="score",
            color="signal",
            markers=True,
            color_discrete_sequence=["#4F9D9D", "#6C8EF5"],
        )
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No check-ins yet. Add your first one from the Daily Check-in page.")

    st.subheader("Judge-Friendly Highlights")
    for item in [
        "MindPulse AI combines NLP with supervised ML for student risk detection using real scikit-learn classifiers.",
        "Privacy-first design with local SQLite storage, encrypted journal notes, and anonymized admin insights.",
        "Academic stress mapping with attendance, sleep, deadlines, and exam pressure in one dashboard.",
        "Render-ready deployment with Streamlit UI and Flask API in the same project.",
    ]:
        st.markdown(f'<div class="wellness-card">{item}</div>', unsafe_allow_html=True)

with right:
    st.subheader("Wellness Snapshot")
    if latest:
        st.markdown(
            f"""
            <div class="wellness-card">
                <strong>Latest mood:</strong> {latest['mood_label']}<br/>
                <strong>Risk level:</strong> {latest['risk_level']}<br/>
                <strong>Exam pressure:</strong> {latest['exam_pressure']}/10<br/>
                <strong>Attendance:</strong> {latest['attendance_rate']}%
            </div>
            """,
            unsafe_allow_html=True,
        )
    render_notifications(dashboard["notifications"])

    st.subheader("Immediate Support")
    if resource_pack.get("emergency_note"):
        st.error(resource_pack["emergency_note"])
    for tool in resource_pack["coping_tools"]:
        st.markdown(f"- {tool}")

st.subheader("Project Modules")
module_cards = [
    ("Daily Check-in", "Emoji mood capture, sleep, attendance, deadlines, and encrypted journaling."),
    ("Smart Dashboard", "Weekly trends, low-day forecasting, badges, and academic stress insights."),
    ("AI Companion", "Supportive chat responses, grounding prompts, and multilingual coping guidance."),
    ("Resource Hub", "Support resources, helplines, crisis escalation, and mood-aware journal prompts."),
    ("Peer Support", "Anonymous encouragement wall and study-buddy matching suggestions."),
    ("Counselor Insights", "Aggregate-only view for mentors with privacy-preserving analytics."),
]
for start in range(0, len(module_cards), 3):
    row_cards = module_cards[start:start + 3]
    row_columns = st.columns(len(row_cards))
    for column, (title, description) in zip(row_columns, row_cards):
        with column:
            st.markdown(
                f"""
                <div class="wellness-card">
                    <strong>{title}</strong><br/>
                    {description}
                </div>
                """,
                unsafe_allow_html=True,
            )

st.subheader("ML Credibility")
label_distribution = ml_overview["dataset"]["label_distribution"]
st.markdown(
    f"""
    <div class="wellness-card">
        <strong>Selected classifier:</strong> {ml_overview['selected_model']}<br/>
        <strong>Training data:</strong> {ml_overview['dataset']['source']} ({ml_overview['dataset']['samples']} records)<br/>
        <strong>Labels:</strong> Normal ({label_distribution.get('Normal', 0)}),
        Stressed ({label_distribution.get('Stressed', 0)}),
        High Risk ({label_distribution.get('High Risk', 0)})<br/>
        <strong>Forecasting:</strong> {ml_overview['forecast_model']}
    </div>
    """,
    unsafe_allow_html=True,
)
for item in ml_overview["models_tested"]:
    st.markdown(f"- {item['name']}: accuracy {item['accuracy']} | macro F1 {item['macro_f1']}")
