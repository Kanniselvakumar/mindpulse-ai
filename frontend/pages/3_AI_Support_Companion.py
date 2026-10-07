from __future__ import annotations

import streamlit as st

from frontend.ui import apply_branding, get_logo_data_uri, render_sidebar_profile
from shared.gateway import bootstrap, support_chat

st.set_page_config(
    page_title="AI Support Companion - MindPulse AI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

bootstrap()
apply_branding()
profile = render_sidebar_profile(require_auth=False)
user_id = profile["user_id"] if profile else "guest_user"

logo_src = get_logo_data_uri()
logo_img = (
    f'<img src="{logo_src}" style="width: 44px; height: 44px; object-fit: contain; border-radius: 10px; margin-right: 0.75rem; vertical-align: middle;" alt="MindPulse Logo"/>'
    if logo_src
    else ""
)

header_col1, header_col2, header_col3 = st.columns([2.5, 1.2, 0.8])
with header_col1:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; margin-bottom: 0.25rem;">
            {logo_img}
            <h1 style="margin: 0; font-size: 2rem;">AI Support Companion</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Empathetic, non-medical dialogue providing tailored psychological grounding, study strategies, and reach-out scripts.")

with header_col2:
    selected_language = st.selectbox(
        "Response Language",
        options=["English", "Tamil", "Hindi", "Telugu", "Kannada"],
        index=0,
        key="support_companion_language",
    )

with header_col3:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state["chat_history"] = []
        st.rerun()

st.session_state.setdefault("chat_history", [])

st.markdown("##### 💡 Suggested Discussion Topics")
pcols = st.columns(6)
preset_message = ""

with pcols[0]:
    if st.button("📚 Exam Stress", use_container_width=True):
        preset_message = "I have an important exam coming up, my syllabus is huge, and I am panicking."
with pcols[1]:
    if st.button("🔋 Deep Burnout", use_container_width=True):
        preset_message = "I am mentally exhausted, overwhelmed by constant deadlines, and feel like collapsing."
with pcols[2]:
    if st.button("⚡ Low Motivation", use_container_width=True):
        preset_message = "I want to study for my semester, but I keep procrastinating and can't start."
with pcols[3]:
    if st.button("🌙 Can't Sleep", use_container_width=True):
        preset_message = "My mind races with overthinking at night and I haven't slept properly for days."
with pcols[4]:
    if st.button("😰 Acute Anxiety", use_container_width=True):
        preset_message = "My heart is racing, chest feels tight, and I feel like everything is spinning out of control."
with pcols[5]:
    if st.button("🫂 Feeling Lonely", use_container_width=True):
        preset_message = "I feel very isolated in college, disconnected from my peers, and have nobody to talk to."

# Render conversation history
for item in st.session_state["chat_history"]:
    with st.chat_message(item["role"]):
        st.markdown(item["message"])

chat_input = st.chat_input("Share what is on your mind or ask for advice...")
message = preset_message or chat_input

if message:
    st.session_state["chat_history"].append({"role": "user", "message": message})
    with st.chat_message("user"):
        st.markdown(message)

    with st.spinner("MindPulse companion is reflecting..."):
        response = support_chat(
            {
                "user_id": user_id,
                "message": message,
                "language": selected_language,
            }
        )

    st.session_state["chat_history"].append({"role": "assistant", "message": response["reply"]})

    with st.chat_message("assistant"):
        st.markdown(response["reply"])

        meta_col1, meta_col2 = st.columns(2)
        meta_col1.markdown(f"🏷️ **Focus Area:** `{response.get('focus_area', 'Support')}`")
        meta_col2.markdown(f"❓ **Reflective Prompt:** *{response.get('follow_up_prompt', '')}*")

        support_plan = response.get("support_plan", [])
        if support_plan:
            st.markdown("##### 🧭 Targeted Action Blueprint")
            plan_cols = st.columns(len(support_plan))
            for col, item in zip(plan_cols, support_plan):
                with col:
                    st.markdown(
                        f"""
                        <div class="wellness-card" style="height: 150px; padding: 0.9rem;">
                            <span style="color: #14B8A6; font-weight: 700; font-size: 0.9rem;">{item['title']}</span>
                            <p style="margin: 0.35rem 0 0 0; font-size: 0.82rem; color: #CBD5E1; line-height: 1.4;">{item['step']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        coping_cards = response.get("coping_cards", [])
        if coping_cards:
            st.markdown("##### 📌 Practical Coping Anchors")
            for card in coping_cards:
                st.markdown(f"- {card}")

        if response.get("contact_script"):
            st.markdown("##### 💬 Need to Reach Out to Someone?")
            st.caption(response.get("contact_script_intro", "If reaching out feels hard, copy and send this message:"))
            st.code(response["contact_script"])

        if response.get("escalation_note"):
            st.error(response["escalation_note"])
