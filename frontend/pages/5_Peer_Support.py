from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json

import streamlit as st

from frontend.ui import apply_branding, render_sidebar_profile
from shared.gateway import (
    bootstrap,
    create_peer_post,
    get_buddy_matches,
    get_peer_circles,
    join_peer_circle,
    list_peer_posts,
)


st.set_page_config(page_title="Peer Support", page_icon="🤝", layout="wide", initial_sidebar_state="collapsed")

bootstrap()
apply_branding()
profile = render_sidebar_profile()

st.title("Peer Support & Community")
st.caption("Anonymous encouragement wall, buddy matching, and moderated support circles.")

tab1, tab2 = st.tabs(["🗣️ Peer Wall & Buddies", "🫂 Support Circles"])

# ─── Tab 1: Original Peer Wall & Buddy Matching ───────────────────────────────
with tab1:
    posts = list_peer_posts()
    matches = get_buddy_matches(profile["user_id"])

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

# ─── Tab 2: Peer Support Circles ──────────────────────────────────────────────
with tab2:
    st.subheader("🫂 Structured Support Circles")
    st.caption(
        "Small, themed peer support groups with AI-facilitated prompts. "
        "Join a circle that matches your current challenge and connect with others who understand."
    )

    circles = get_peer_circles()

    if not circles:
        st.info("No support circles available yet. Check back soon.")
    else:
        theme_icons = {
            "Exam Stress": "📝",
            "Sleep & Lifestyle": "😴",
            "Attendance & Deadlines": "📅",
        }

        for circle in circles:
            circle_id = circle["id"]
            name = circle["name"]
            theme = circle["theme"]
            prompt = circle.get("facilitator_prompt", "")
            try:
                members = json.loads(circle.get("members", "[]"))
            except Exception:
                members = []
            member_count = len(members)
            is_member = profile["user_id"] in members

            icon = theme_icons.get(theme, "🫂")

            with st.expander(f"{icon} **{name}** — *{theme}* · {member_count} member(s)", expanded=False):
                st.markdown(f"**This week's facilitator prompt:**")
                st.info(f"💬 {prompt}")

                if is_member:
                    st.success("✅ You are a member of this circle.")
                    st.markdown("*Check in with your circle members through the peer wall or the AI companion.*")
                else:
                    if st.button(f"Join '{name}'", key=f"join_{circle_id}"):
                        join_peer_circle(circle_id, profile["user_id"])
                        st.success(f"You've joined **{name}**! Use the peer wall to share with your circle.")
                        st.rerun()

                st.caption(f"Theme: {theme} · Members: {member_count}")
