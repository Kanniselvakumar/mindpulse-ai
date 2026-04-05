from __future__ import annotations

import streamlit as st

from frontend.ui import apply_branding, render_notifications, render_sidebar_profile
from shared.gateway import bootstrap, get_dashboard, get_resources


st.set_page_config(page_title="Resource Hub", page_icon="\U0001F9ED", layout="wide", initial_sidebar_state="collapsed")

bootstrap()
apply_branding()
profile = render_sidebar_profile()
dashboard = get_dashboard(profile["user_id"], days=14)
latest = dashboard.get("latest_entry") or {}
resource_pack = get_resources(profile["campus"], latest.get("risk_level", "Normal"))

st.title("Resource Hub")
st.caption("Student-friendly support options, coping tools, and crisis escalation guidance.")

render_notifications(dashboard["notifications"])

if resource_pack.get("emergency_note"):
    st.error(resource_pack["emergency_note"])

left, right = st.columns(2)
with left:
    st.subheader("Support Contacts")
    for resource in resource_pack["campus_resources"]:
        st.markdown(
            f"""
            <div class="wellness-card">
                <strong>{resource['name']}</strong><br/>
                {resource['type']}<br/>
                Contact: {resource['contact']}<br/>
                Hours: {resource['hours']}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("National Helplines")
    for helpline in resource_pack["helplines"]:
        st.markdown(f"- {helpline['name']}: {helpline['contact']} ({helpline['note']})")

with right:
    st.subheader("Coping Tools")
    for tool in resource_pack["coping_tools"]:
        st.markdown(f"- {tool}")

    st.subheader("Smart Journaling Prompts")
    for prompt in resource_pack["journal_prompts"]:
        st.markdown(f"- {prompt}")

    st.subheader("Mood Music Recommendation")
    st.info(resource_pack["playlist_hint"])

