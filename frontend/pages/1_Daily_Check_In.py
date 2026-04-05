from __future__ import annotations

import pandas as pd
import streamlit as st

from frontend.ui import apply_branding, render_sidebar_profile
from shared.gateway import bootstrap, submit_check_in


st.set_page_config(page_title="Daily Check-in", page_icon="\U0001F4DD", layout="wide", initial_sidebar_state="collapsed")

bootstrap()
apply_branding()
profile = render_sidebar_profile()

st.title("Daily Wellness Check-in")
st.caption("A fast, 5-second emotional snapshot plus the study and health signals behind it.")

mood_options = {
    "\U0001F604 Thriving": ("Thriving", 5),
    "\U0001F642 Good": ("Focused", 4),
    "\U0001F610 Okay": ("Okay", 3),
    "\U0001F61F Low": ("Anxious", 2),
    "\U0001F622 Struggling": ("Overwhelmed", 1),
}
with st.form("daily_checkin_form"):
    selected = st.radio(
        "How are you feeling right now?",
        options=list(mood_options.keys()),
        horizontal=True,
    )
    mood_label, mood_score = mood_options[selected]

    col1, col2, col3 = st.columns(3)
    stress_score = col1.slider("Stress", 1, 10, 5)
    energy_score = col2.slider("Energy", 1, 10, 6)
    exam_pressure = col3.slider("Exam pressure", 1, 10, 5)

    col4, col5, col6 = st.columns(3)
    sleep_hours = col4.slider("Sleep hours", 0.0, 12.0, 7.0, 0.5)
    attendance_rate = col5.slider("Attendance %", 0, 100, 85)
    assignments_due = col6.slider("Assignments due", 0, 10, 1)

    social_connectedness = st.slider("Social connectedness", 1, 5, 3)
    notes = st.text_area(
        "Optional journal note",
        placeholder="Example: I am feeling nervous about tomorrow's internal exam and low on sleep.",
    )
    submitted = st.form_submit_button("Analyze Check-in", use_container_width=True)

if submitted:
    payload = {
        **profile,
        "mood_label": mood_label,
        "mood_score": mood_score,
        "stress_score": stress_score,
        "energy_score": energy_score,
        "sleep_hours": sleep_hours,
        "attendance_rate": attendance_rate,
        "assignments_due": assignments_due,
        "social_connectedness": social_connectedness,
        "exam_pressure": exam_pressure,
        "notes": notes,
    }
    st.session_state["last_checkin_result"] = submit_check_in(payload)

result = st.session_state.get("last_checkin_result")
if result:
    risk = result["risk"]
    analysis = result["analysis"]
    recommendations = result["recommendations"]
    st.success("Check-in captured and analyzed.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Risk Level", risk["label"])
    m2.metric("Risk Score", risk["risk_score"])
    m3.metric("Sentiment", analysis["sentiment_label"].title())
    m4.metric("Primary Emotion", analysis["emotion"].title())
    st.caption(
        f"ML classifier: {risk['selected_model']} | confidence: {risk['model_confidence']} | data source: {risk['dataset_source']}"
    )

    left, right = st.columns([1.4, 1])
    with left:
        st.subheader("Recommended Next Steps")
        for action in recommendations["priority_actions"]:
            st.markdown(f"- {action}")
        if recommendations["study_hacks"]:
            st.subheader("Study Support")
            for tip in recommendations["study_hacks"]:
                st.markdown(f"- {tip}")
        if recommendations["habit_stack"]:
            st.subheader("Habit Stack")
            for habit in recommendations["habit_stack"]:
                st.markdown(f"- {habit}")

    with right:
        st.subheader("Supportive Extras")
        st.info(f"Badge unlocked: {recommendations['badge']}")
        st.warning(f"Daily challenge: {recommendations['daily_challenge']}")
        for step in recommendations["breathing_exercise"]:
            st.markdown(f"- {step}")

        if result.get("alert"):
            alert = result["alert"]
            st.error(f"High-risk alert flow created for: {alert['contact_name']}")
            delivery = alert["delivery"]
            st.caption(
                f"Email status: {delivery['email']['status']} | SMS status: {delivery['sms']['status']}"
            )
            if delivery["email"]["error"]:
                st.caption(f"Email detail: {delivery['email']['error']}")
            if delivery["sms"]["error"]:
                st.caption(f"SMS detail: {delivery['sms']['error']}")

    forecast = pd.DataFrame(result["dashboard"]["forecast"])
    if not forecast.empty:
        st.subheader("Low-Day Forecast")
        st.dataframe(forecast, use_container_width=True)

