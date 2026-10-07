from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from frontend.ui import apply_branding, render_notifications, render_sidebar_profile
from shared.gateway import (
    bootstrap,
    get_appointments,
    get_coping_plan,
    get_dashboard,
    get_resources,
    request_appointment,
    update_coping_plan_item,
)


st.set_page_config(page_title="Resource Hub", page_icon="🧭", layout="wide", initial_sidebar_state="collapsed")

bootstrap()
apply_branding()
profile = render_sidebar_profile()
dashboard = get_dashboard(profile["user_id"], days=14)
latest = dashboard.get("latest_entry") or {}
resource_pack = get_resources(profile["campus"], latest.get("risk_level", "Normal"))

st.title("Resource Hub")
st.caption("Campus support, coping tools, appointment booking, and wellness plan — all in one place.")

render_notifications(dashboard["notifications"])

if resource_pack.get("emergency_note"):
    st.error(resource_pack["emergency_note"])

tab1, tab2, tab3 = st.tabs(["📋 Campus Resources", "✅ My Coping Plan", "📅 Book a Session"])

# ─── Tab 1: Original Resources ─────────────────────────────────────────────────
with tab1:
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

# ─── Tab 2: Personalized Coping Plan ──────────────────────────────────────────
with tab2:
    st.subheader("✅ My Personalized Coping Plan")
    st.caption("Track and complete your daily wellness strategies. Check off items as you go!")

    plan_items = get_coping_plan(profile["user_id"])

    if not plan_items:
        st.info("No coping plan generated yet. Complete a check-in first to unlock your personalized plan.")
    else:
        total = len(plan_items)
        completed_count = sum(1 for item in plan_items if item.get("completed"))
        progress = completed_count / total if total > 0 else 0

        st.progress(progress, text=f"{completed_count}/{total} strategies completed today")

        for item in plan_items:
            item_id = item["id"]
            strategy = item["strategy_name"]
            category = item.get("strategy_category", "general")
            is_done = bool(item.get("completed"))

            category_icons = {
                "mindfulness": "🧘",
                "physical": "🚶",
                "journaling": "📓",
                "academic": "📚",
                "social": "🤝",
                "general": "✨",
            }
            icon = category_icons.get(category, "✨")

            col1, col2 = st.columns([0.08, 0.92])
            with col1:
                new_state = st.checkbox("", value=is_done, key=f"plan_{item_id}", label_visibility="collapsed")
            with col2:
                if is_done:
                    st.markdown(f"~~{icon} {strategy}~~ ✅")
                else:
                    st.markdown(f"{icon} {strategy}")

            if new_state != is_done:
                update_coping_plan_item(item_id, completed=new_state)
                st.rerun()

        st.divider()
        if completed_count == total:
            st.success("🌟 You completed your entire wellness plan today! Incredible dedication.")
        elif completed_count >= total // 2:
            st.info(f"👍 More than halfway there! {total - completed_count} strategies left.")

# ─── Tab 3: Counselor Appointment Booking ─────────────────────────────────────
with tab3:
    st.subheader("📅 Book a Counselor Session")
    st.caption("Request a private session with your campus counselor directly from here.")

    with st.form("appointment_form", clear_on_submit=True):
        # Generate available time slots for the next 5 days
        slot_options = []
        for day_offset in range(1, 6):
            slot_day = datetime.now() + timedelta(days=day_offset)
            for hour in [10, 14, 16]:
                slot_dt = slot_day.replace(hour=hour, minute=0, second=0, microsecond=0)
                slot_options.append(slot_dt.strftime("%Y-%m-%d %H:%M"))

        selected_slot = st.selectbox("Select an Available Slot", options=slot_options)
        reason = st.text_area(
            "Brief Reason (optional)",
            placeholder="e.g. Feeling overwhelmed before exams, need guidance on managing stress...",
            max_chars=300,
        )
        submitted = st.form_submit_button("📨 Request Session", use_container_width=True)

        if submitted:
            result = request_appointment(
                student_id=profile["user_id"],
                slot_time=selected_slot,
                reason=reason,
            )
            st.success(f"✅ Session request submitted for **{selected_slot}**. Your counselor will confirm shortly.")

    st.divider()
    st.subheader("My Appointment Requests")
    my_appointments = get_appointments(profile["user_id"], role="student")

    if not my_appointments:
        st.info("No appointment requests yet.")
    else:
        for appt in my_appointments:
            status = appt.get("status", "pending")
            status_colors = {"pending": "🟡", "confirmed": "🟢", "completed": "✅", "cancelled": "🔴"}
            status_icon = status_colors.get(status, "⚪")

            with st.expander(f"{status_icon} {appt['slot_time']} — Status: {status.title()}"):
                st.write(f"**Reason:** {appt.get('reason', 'Not specified')}")
                if appt.get("notes"):
                    st.write(f"**Counselor Notes:** {appt['notes']}")
