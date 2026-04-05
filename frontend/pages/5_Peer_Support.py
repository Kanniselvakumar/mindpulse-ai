from __future__ import annotations

import streamlit as st

from frontend.ui import apply_branding, render_sidebar_profile
from shared.gateway import bootstrap, create_peer_post, get_buddy_matches, list_peer_posts


st.set_page_config(page_title="Peer Support", page_icon="\U0001F91D", layout="wide", initial_sidebar_state="collapsed")

bootstrap()
apply_branding()
profile = render_sidebar_profile()
posts = list_peer_posts()
matches = get_buddy_matches(profile["user_id"])

st.title("Peer Support and Study Buddy Matching")
st.caption("Anonymous encouragement wall plus lightweight buddy suggestions for shared academic context.")

left, right = st.columns([1.2, 1])
with left:
    st.subheader("Anonymous Peer Wall")
    for post in posts:
        st.markdown(
            f"""
            <div class="wellness-card">
                <strong>{post['topic']}</strong><br/>
                {post['message']}<br/>
                <em>posted by {post['alias']}</em>
            </div>
            """,
            unsafe_allow_html=True,
        )

with right:
    st.subheader("Post Your Own")
    with st.form("peer_post_form"):
        alias = st.text_input("Alias", value="Anonymous")
        topic = st.selectbox("Topic", options=["Daily Win", "Recovery Story", "Study Tip", "Need Support"])
        message = st.text_area("Message", max_chars=400)
        submit_post = st.form_submit_button("Share Anonymously", use_container_width=True)

    if submit_post and message.strip():
        create_peer_post({"alias": alias, "topic": topic, "message": message})
        st.success("Your anonymous post has been added.")
        st.rerun()

    st.subheader("Study Buddy Suggestions")
    for buddy in matches:
        st.markdown(
            f"""
            <div class="wellness-card">
                <strong>{buddy['alias']}</strong><br/>
                Strength: {buddy['strength']}<br/>
                Availability: {buddy['availability']}<br/>
                {buddy['reason']}
            </div>
            """,
            unsafe_allow_html=True,
        )

