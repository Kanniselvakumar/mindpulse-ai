from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import io
import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.ui import (
    apply_branding,
    get_logo_data_uri,
    render_notifications,
    render_sidebar_profile,
)
from shared.gateway import (
    bootstrap,
    get_dashboard,
    get_ml_overview,
    get_resources,
    get_sample_wellness_csv,
)

st.set_page_config(
    page_title="MindPulse AI - Student Wellbeing Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

bootstrap()
apply_branding()
profile = render_sidebar_profile(require_auth=False)
ml_overview = get_ml_overview()

logo_src = get_logo_data_uri()
logo_html = (
    f'<img src="{logo_src}" style="width: 72px; height: 72px; object-fit: contain; border-radius: 16px; margin-bottom: 0.9rem; filter: drop-shadow(0 6px 18px rgba(20, 184, 166, 0.45));" alt="MindPulse Logo"/>'
    if logo_src
    else ""
)

st.markdown(
    f"""
    <div class="hero-panel" style="padding: 2.5rem 2.25rem;">
        {logo_html}
        <span class="brand-kicker">MindPulse AI • Intelligent Mental Health Platform</span>
        <h1 style="font-size: 2.3rem; margin-top: 0.35rem; margin-bottom: 0.65rem;">
            Intelligent Signals for Student Wellbeing & Early Intervention
        </h1>
        <p style="font-size: 1.05rem; line-height: 1.6; max-width: 880px; color: rgba(255, 255, 255, 0.92);">
            MindPulse AI is a full-stack mental health support system built with <strong>Streamlit</strong>,
            <strong>Flask</strong>, <strong>scikit-learn</strong>, and <strong>NLP sentiment engines</strong>.
            It correlates academic pressure, attendance patterns, and sleep debt with daily psychological signals,
            surfacing proactive care before stress progresses into clinical burnout.
        </p>
        <div class="brand-pill-row">
            <span class="brand-pill">🧠 NLP Sentiment Extraction</span>
            <span class="brand-pill">🤖 Dual-Model Supervised ML</span>
            <span class="brand-pill">⚡ Real-Time Streaming Studio</span>
            <span class="brand-pill">🔒 Privacy-First Encrypted Notes</span>
            <span class="brand-pill">📱 Multilingual Support</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── SECTION 1: LIVE PLATFORM & MODEL INDICATORS ─────────────────────────────
st.subheader("📊 Live System Architecture & ML Diagnostics")

label_distribution = ml_overview["dataset"]["label_distribution"]
m1, m2, m3, m4 = st.columns(4)

m1.metric("Training Dataset Records", f"{ml_overview['dataset']['samples']:,} Records")
m2.metric("Active Champion Model", ml_overview["selected_model"])
best_acc = max((m["accuracy"] for m in ml_overview["models_tested"]), default=0.94)
m3.metric("Test Set Accuracy", f"{best_acc * 100:.1f}%")
m4.metric("Extracted Features", f"{ml_overview['dataset']['feature_count']} Multimodal Signals")

# ─── SECTION 2: SYSTEM CAPABILITIES & METHODOLOGY ────────────────────────────
col_left, col_right = st.columns([1.5, 1.1])

with col_left:
    st.markdown("#### 🔬 Core Technical Architecture")

    pillars = [
        (
            "1. Multi-Signal Daily Check-In & Academic Correlator",
            "Students log 8 objective and subjective signals: mood rating (1-5), stress intensity (1-10), energy level, sleep hours, class attendance (%), pending assignments, social connection, and exam pressure.",
        ),
        (
            "2. NLP Sentiment & Emotional Polarity Engine",
            "Reflections and notes are processed through NLTK/TextBlob and VADER compound scoring (-1.0 to +1.0) to capture nuances that numerical ratings alone might miss.",
        ),
        (
            "3. Supervised ML Risk Classification & Triage",
            "A dual-classifier pipeline evaluates Logistic Regression (with StandardScaler) against Random Forest (with balanced class weighting), selecting the champion model via macro-F1 to classify status into Normal, Stressed, and High Risk.",
        ),
        (
            "4. Real-Time Streaming & Simulation Studio",
            "Includes row-by-row playback of custom CSV/JSON datasets, real-time synthetic biometric streams, interactive feature importance analysis, and live test confusion matrices.",
        ),
        (
            "5. Confidential Care Network & Mentor Alerts",
            "Equipped with an anonymous peer support wall, encrypted journal storage, and consent-based alert dispatches via Twilio SMS and Resend Email.",
        ),
    ]

    for title, description in pillars:
        st.markdown(
            f"""
            <div class="wellness-card" style="padding: 1rem 1.25rem; margin-bottom: 0.75rem;">
                <span style="color: #14B8A6; font-weight: 700; font-size: 0.95rem;">{title}</span>
                <p style="margin: 0.35rem 0 0 0; font-size: 0.88rem; color: #CBD5E1; line-height: 1.5;">{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

with col_right:
    st.markdown("#### 🎯 Benchmark Model Performance")
    models_tested = ml_overview.get("models_tested", [])
    if models_tested:
        comp_records = []
        for m in models_tested:
            comp_records.append({
                "Model Architecture": m["name"],
                "Accuracy": f"{m['accuracy'] * 100:.1f}%",
                "Macro-F1": f"{m['macro_f1']:.4f}",
            })
        st.dataframe(pd.DataFrame(comp_records), use_container_width=True, hide_index=True)

    st.markdown("#### 🏷️ Target Class Distribution")
    dist_df = pd.DataFrame(
        list(label_distribution.items()),
        columns=["Risk Level", "Count"],
    )
    fig_pie = px.pie(
        dist_df,
        names="Risk Level",
        values="Count",
        color="Risk Level",
        color_discrete_map={
            "Normal": "#10B981",
            "Stressed": "#F59E0B",
            "High Risk": "#F43F5E",
        },
        hole=0.45,
    )
    fig_pie.update_layout(
        height=240,
        margin=dict(l=10, r=10, t=15, b=10),
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ─── SECTION 3: INTERACTIVE DATA EXPLORATION ─────────────────────────────────
st.markdown("---")
st.subheader("📈 Student Wellness Data & Correlation Insights")

if profile:
    dashboard = get_dashboard(profile["user_id"], days=30)
    timeline_data = dashboard.get("timeline", [])
    user_metrics = dashboard.get("metrics", {})
    latest_entry = dashboard.get("latest_entry") or {}

    pcol1, pcol2, pcol3 = st.columns([1.7, 1.0, 1.0])
    with pcol1:
        st.markdown(f"##### Your Recent Check-In History ({profile.get('name', 'Student')})")
        if timeline_data:
            t_df = pd.DataFrame(timeline_data)
            plot_df = t_df[["log_date", "mood_score", "stress_score"]].melt(
                id_vars="log_date",
                var_name="Signal",
                value_name="Score",
            )
            plot_df["Signal"] = plot_df["Signal"].replace({"mood_score": "Mood (1-5)", "stress_score": "Stress (1-10)"})
            fig_user = px.line(
                plot_df,
                x="log_date",
                y="Score",
                color="Signal",
                markers=True,
                color_discrete_map={"Mood (1-5)": "#14B8A6", "Stress (1-10)": "#F43F5E"},
            )
            fig_user.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_user, use_container_width=True)
        else:
            st.info("No check-ins logged yet. Use the **Check-In** page from the navigation bar to log your first mood entry!")

    with pcol2:
        st.markdown("##### Personal Metrics")
        st.metric("Check-In Streak", f"{user_metrics.get('check_in_streak', 0)} Days")
        st.metric("Average Sleep", f"{user_metrics.get('average_sleep', 0)} hrs")
        st.metric("Average Stress", f"{user_metrics.get('average_stress', 0)}/10")

    with pcol3:
        st.markdown("##### Active Risk Status")
        current_risk = latest_entry.get("risk_level", "Normal")
        risk_color = "#10B981" if current_risk == "Normal" else "#F59E0B" if current_risk == "Stressed" else "#F43F5E"
        st.markdown(
            f"""
            <div class="wellness-card" style="border-left: 4px solid {risk_color};">
                <span style="font-size: 0.85rem; color: #94A3B8;">Current Status</span>
                <h3 style="margin: 0.2rem 0; color: {risk_color};">{current_risk}</h3>
                <span style="font-size: 0.85rem; color: #CBD5E1;">
                    Exam Pressure: {latest_entry.get('exam_pressure', 'N/A')}/10<br/>
                    Attendance: {latest_entry.get('attendance_rate', 'N/A')}%
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    # Guest / Benchmark view showing synthetic population correlation
    sample_csv = get_sample_wellness_csv()
    sample_df = pd.read_csv(io.StringIO(sample_csv))

    dcol1, dcol2 = st.columns([1.5, 1.2])

    with dcol1:
        st.markdown("##### Benchmark Correlation: Sleep Hours vs. Stress Intensity")
        fig_scatter = px.scatter(
            sample_df,
            x="sleep_hours",
            y="stress_score",
            color="risk_level",
            size="assignments_due",
            hover_data=["attendance_rate", "mood_score"],
            color_discrete_map={"Normal": "#10B981", "Stressed": "#F59E0B", "High Risk": "#F43F5E"},
            labels={"sleep_hours": "Sleep Duration (Hours)", "stress_score": "Perceived Stress (1-10)", "risk_level": "Risk Level"},
        )
        fig_scatter.update_layout(height=300, margin=dict(l=10, r=10, t=20, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_scatter, use_container_width=True)

    with dcol2:
        st.markdown("##### Sample Dataset Preview (First 5 Benchmark Records)")
        display_cols = ["mood_score", "stress_score", "sleep_hours", "attendance_rate", "assignments_due", "risk_level"]
        st.dataframe(sample_df[display_cols].head(5), use_container_width=True, hide_index=True)
        st.caption("ℹ️ Sign in using the **🔑 Login / Sign Up** button in the navbar to save your personal check-ins!")

# ─── SECTION 4: WORKSPACE MODULE DIRECTORY ───────────────────────────────────
st.markdown("---")
st.subheader("🚀 Platform Workspace Modules")

cards_data = [
    ("📝 1. Daily Check-In", "pages/1_Daily_Check_In.py", "Log daily emoji mood, sleep hours, attendance, assignments, and encrypted personal journal thoughts."),
    ("📊 2. Mood & Analytics Dashboard", "pages/2_Mood_Dashboard.py", "Inspect multi-day emotional trends, stress forecasts, recovery buffers, and milestone badges."),
    ("💬 3. AI Support Companion", "pages/3_AI_Support_Companion.py", "Engage in empathetic, non-medical dialogue with multilingual support in English, Tamil, Hindi, Telugu, and Kannada."),
    ("🧭 4. Resource Hub", "pages/4_Resource_Hub.py", "Access campus psychological helplines, grounding exercises, guided journaling prompts, and emergency escalation tools."),
    ("🤝 5. Anonymous Peer Support", "pages/5_Peer_Support.py", "Share words of encouragement, read peer notes, and request study-buddy connection requests anonymously."),
    ("🛡️ 6. Counselor Insights Hub", "pages/6_Counselor_Insights.py", "Faculty & counseling view providing de-identified cohort analytics, high-stress clusters, and early trend warnings."),
    ("⚡ 7. Real-Time Dataset Studio", "pages/7_Realtime_Dataset_Studio.py", "Upload custom CSV/JSON datasets, retrain ML models live, and stream simulated biometric signals."),
]

row1 = cards_data[:4]
row2 = cards_data[4:]

cols1 = st.columns(len(row1))
for col, (title, page_url, desc) in zip(cols1, row1):
    with col:
        st.markdown(
            f"""
            <div class="wellness-card" style="height: 175px;">
                <span style="color: #14B8A6; font-weight: 700; font-size: 0.95rem;">{title}</span>
                <p style="margin: 0.4rem 0 0 0; font-size: 0.83rem; color: #CBD5E1; line-height: 1.45;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page_url, label=f"Open {title.split('.')[1].strip()}", use_container_width=True)

cols2 = st.columns(len(row2))
for col, (title, page_url, desc) in zip(cols2, row2):
    with col:
        st.markdown(
            f"""
            <div class="wellness-card" style="height: 175px;">
                <span style="color: #6366F1; font-weight: 700; font-size: 0.95rem;">{title}</span>
                <p style="margin: 0.4rem 0 0 0; font-size: 0.83rem; color: #CBD5E1; line-height: 1.45;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page_url, label=f"Open {title.split('.')[1].strip()}", use_container_width=True)
