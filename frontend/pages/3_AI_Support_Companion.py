from __future__ import annotations

import streamlit as st

from frontend.ui import apply_branding, render_sidebar_profile
from shared.gateway import bootstrap, support_chat


st.set_page_config(
    page_title="AI Support Companion",
    page_icon="\U0001F4AC",
    layout="wide",
    initial_sidebar_state="collapsed",
)

bootstrap()
apply_branding()
profile = render_sidebar_profile()

st.title("AI Support Companion")
st.caption("Supportive, non-medical conversations with more specific grounding, study, and reach-out guidance.")

st.session_state.setdefault("chat_history", [])

prompt_cols = st.columns(3)
preset_message = ""
with prompt_cols[0]:
    if st.button("Exam Stress", use_container_width=True):
        preset_message = "I feel anxious about my upcoming exams and I cannot focus."
with prompt_cols[1]:
    if st.button("Burnout", use_container_width=True):
        preset_message = "I am exhausted, behind on work, and mentally drained."
with prompt_cols[2]:
    if st.button("Need Motivation", use_container_width=True):
        preset_message = "I want to study but I have no motivation today."

for item in st.session_state["chat_history"]:
    with st.chat_message(item["role"]):
        st.markdown(item["message"])

chat_input = st.chat_input("Share what is on your mind...")
message = preset_message or chat_input

if message:
    st.session_state["chat_history"].append({"role": "user", "message": message})
    with st.chat_message("user"):
        st.markdown(message)

    response = support_chat(
        {
            "user_id": profile["user_id"],
            "message": message,
            "language": profile["language"],
        }
    )
    st.session_state["chat_history"].append({"role": "assistant", "message": response["reply"]})

    with st.chat_message("assistant"):
        st.markdown(response["reply"])

        meta_col1, meta_col2 = st.columns(2)
        meta_col1.caption(f"Focus area: {response.get('focus_area', 'Support')}")
        meta_col2.caption(response["follow_up_prompt"])

        support_plan = response.get("support_plan", [])
        for start in range(0, len(support_plan), 3):
            row_items = support_plan[start:start + 3]
            row_columns = st.columns(len(row_items))
            for column, item in zip(row_columns, row_items):
                with column:
                    st.markdown(
                        f"""
                        <div class="wellness-card">
                            <strong>{item['title']}</strong><br/>
                            {item['step']}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        st.subheader("Helpful Prompts")
        for card in response["coping_cards"]:
            st.markdown(f"- {card}")

        if response.get("reflection"):
            st.info(response["reflection"])

        if response.get("contact_script"):
            st.caption(response.get("contact_script_intro", "If reaching out feels hard, send this message:"))
            st.code(response["contact_script"])

        if response.get("escalation_note"):
            st.error(response["escalation_note"])


