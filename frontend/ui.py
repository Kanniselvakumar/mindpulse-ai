from __future__ import annotations

from typing import Any

import streamlit as st

from shared.gateway import (
    get_account,
    get_alert_provider_status,
    get_profile,
    login_user,
    register_user,
    update_profile,
)


NAV_LINKS = [
    ("Home.py", "\U0001F3E0", "Home"),
    ("pages/1_Daily_Check_In.py", "\U0001F4DD", "Check-In"),
    ("pages/2_Mood_Dashboard.py", "\U0001F4CA", "Dashboard"),
    ("pages/3_AI_Support_Companion.py", "\U0001F4AC", "Support"),
    ("pages/4_Resource_Hub.py", "\U0001F9ED", "Resources"),
    ("pages/5_Peer_Support.py", "\U0001F91D", "Peers"),
    ("pages/6_Counselor_Insights.py", "\U0001F6E1", "Insights"),
]

PROFILE_KEYS = [
    "user_id",
    "name",
    "course",
    "year",
    "campus",
    "language",
    "anonymous_mode",
    "consent_alerts",
    "alert_contact",
    "alert_channel",
    "student_email",
    "phone_number",
    "trusted_contact_email",
    "trusted_contact_phone",
]

PROFILE_FORM_FIELDS = [
    "name",
    "course",
    "year",
    "language",
    "student_email",
    "phone_number",
    "anonymous_mode",
    "consent_alerts",
    "alert_contact",
    "alert_channel",
    "trusted_contact_email",
    "trusted_contact_phone",
]

PROFILE_FORM_KEYS = {
    field: f"profile_form_{field}" for field in PROFILE_FORM_FIELDS
}


def apply_branding() -> None:
    st.markdown(
        """
        <style>
            :root {
                --mindpulse-primary: #4F9D9D;
                --mindpulse-secondary: #A8E6CF;
                --mindpulse-background: #F7F9FB;
                --mindpulse-accent: #6C8EF5;
                --mindpulse-danger: #FF6B6B;
                --mindpulse-warning: #FFD166;
                --mindpulse-safe: #A8E6CF;
                --mindpulse-text: #223943;
            }
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(168, 230, 207, 0.22), transparent 28%),
                    radial-gradient(circle at top right, rgba(108, 142, 245, 0.16), transparent 24%),
                    linear-gradient(180deg, #f7f9fb 0%, #eef5f9 100%);
            }
            section[data-testid="stSidebar"],
            div[data-testid="stSidebarNav"],
            div[data-testid="collapsedControl"],
            [data-testid="stSidebarCollapseButton"],
            [data-testid="stSidebarCollapsedControl"],
            header[data-testid="stHeader"],
            header[data-testid="stAppHeader"] {
                display: none !important;
            }
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 1rem !important;
            }
            div[data-testid="stVerticalBlock"]:has(> div > div > div > .top-nav-marker),
            div[data-testid="stVerticalBlock"]:has(.top-nav-marker) {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                padding: 0.95rem 1.1rem;
                margin-bottom: 1.5rem;
                border: 1px solid rgba(79, 157, 157, 0.15);
                box-shadow: 0 10px 26px rgba(71, 95, 132, 0.08);
                border-radius: 24px;
            }
            div[data-testid="stPageLink"] {
                margin-top: 0 !important;
                margin-bottom: 0 !important;
            }
            div[data-testid="stPageLink"] a {
                width: 100%;
                min-height: 42px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.22rem;
                padding: 0.35rem 0.45rem;
                border-radius: 999px;
                border: 1px solid rgba(79, 157, 157, 0.10);
                background: rgba(255, 255, 255, 0.90);
                color: var(--mindpulse-text);
                font-weight: 600;
                font-size: 0.82rem;
                white-space: nowrap;
                box-shadow: 0 8px 18px rgba(79, 111, 143, 0.05);
            }
            div[data-testid="stPageLink"] a:hover {
                border-color: rgba(108, 142, 245, 0.22);
                background: linear-gradient(135deg, rgba(79, 157, 157, 0.12) 0%, rgba(108, 142, 245, 0.12) 100%);
                color: var(--mindpulse-text);
            }
            div[data-testid="stPageLink"] a[aria-current="page"] {
                background: linear-gradient(135deg, #4F9D9D 0%, #6C8EF5 100%);
                color: #ffffff;
                border-color: transparent;
                box-shadow: 0 12px 28px rgba(108, 142, 245, 0.18);
            }
            div[data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.94);
                border: 1px solid rgba(79, 157, 157, 0.16);
                padding: 0.95rem 1rem;
                border-radius: 18px;
                box-shadow: 0 14px 30px rgba(79, 157, 157, 0.08);
            }
            .wellness-card {
                background: rgba(255, 255, 255, 0.96);
                border: 1px solid rgba(108, 142, 245, 0.12);
                border-radius: 20px;
                padding: 1rem 1.1rem;
                margin-bottom: 0.8rem;
                box-shadow: 0 12px 28px rgba(71, 95, 132, 0.08);
            }
            .site-brand {
                display: inline-flex;
                align-items: center;
                gap: 0.65rem;
                color: var(--mindpulse-text);
                font-weight: 700;
                font-size: 1.02rem;
                margin-top: 0;
                white-space: nowrap;
            }
            .site-brand-mark {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: linear-gradient(135deg, #4F9D9D 0%, #6C8EF5 100%);
                box-shadow: 0 0 0 6px rgba(168, 230, 207, 0.32);
            }
            .hero-panel {
                position: relative;
                overflow: hidden;
                background:
                    radial-gradient(circle at top right, rgba(255, 255, 255, 0.18), transparent 24%),
                    linear-gradient(135deg, rgba(79, 157, 157, 0.98) 0%, rgba(108, 142, 245, 0.96) 58%, rgba(168, 230, 207, 0.96) 100%);
                color: #ffffff;
                border-radius: 30px;
                padding: 1.5rem 1.7rem;
                margin-bottom: 1.15rem;
                box-shadow: 0 24px 48px rgba(79, 111, 143, 0.18);
            }
            .hero-panel::before {
                content: "";
                position: absolute;
                width: 180px;
                height: 180px;
                top: -54px;
                right: -24px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.12);
            }
            .hero-panel::after {
                content: "";
                position: absolute;
                width: 110px;
                height: 110px;
                bottom: -30px;
                right: 24%;
                border-radius: 26px;
                transform: rotate(22deg);
                background: rgba(255, 255, 255, 0.10);
            }
            .hero-panel h1, .hero-panel p {
                color: #ffffff;
                position: relative;
                z-index: 1;
            }
            .brand-kicker {
                position: relative;
                z-index: 1;
                display: inline-block;
                margin-bottom: 0.7rem;
                padding: 0.35rem 0.8rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.18);
                color: #efffff;
                font-size: 0.82rem;
                font-weight: 600;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }
            .brand-pill-row {
                position: relative;
                z-index: 1;
                display: flex;
                flex-wrap: wrap;
                gap: 0.55rem;
                margin-top: 1rem;
            }
            .brand-pill {
                padding: 0.42rem 0.8rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.18);
                border: 1px solid rgba(255, 255, 255, 0.14);
                color: #ffffff;
                font-size: 0.9rem;
            }
            .auth-hero-panel {
                background:
                    radial-gradient(circle at top right, rgba(255, 255, 255, 0.16), transparent 26%),
                    linear-gradient(135deg, #4F9D9D 0%, #6C8EF5 62%, #A8E6CF 100%);
            }
            .stButton > button {
                background: linear-gradient(135deg, #4F9D9D 0%, #6C8EF5 100%);
                color: #ffffff;
                border: 0;
                border-radius: 14px;
                box-shadow: 0 12px 24px rgba(108, 142, 245, 0.18);
            }
            .stButton > button:hover {
                color: #ffffff;
                border: 0;
                filter: brightness(1.03);
            }
            div[data-baseweb="tab-list"] {
                gap: 0.4rem;
            }
            div[data-baseweb="tab-list"] button {
                background: rgba(168, 230, 207, 0.20);
                border-radius: 14px;
            }
            div[data-baseweb="tab-highlight"] {
                background-color: #4F9D9D;
            }
            div[data-testid="stChatMessage"] {
                background: rgba(255, 255, 255, 0.82);
                border: 1px solid rgba(168, 230, 207, 0.24);
                border-radius: 20px;
                padding: 0.2rem 0.35rem;
            }
            div[data-testid="stForm"] {
                background: rgba(255, 255, 255, 0.97);
                border: 1px solid rgba(79, 157, 157, 0.16);
                border-radius: 22px;
                padding: 1rem 1rem 0.8rem 1rem;
                box-shadow: 0 14px 30px rgba(79, 111, 143, 0.08);
            }
            div[data-baseweb="base-input"] {
                background: #ffffff !important;
                border: 1px solid rgba(79, 157, 157, 0.22) !important;
                border-radius: 16px !important;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
            }
            div[data-baseweb="base-input"]:focus-within {
                border-color: #6C8EF5 !important;
                box-shadow: 0 0 0 4px rgba(108, 142, 245, 0.14);
            }
            div[data-baseweb="base-input"] input {
                color: var(--mindpulse-text) !important;
                background: transparent !important;
            }
            div[data-baseweb="select"] > div {
                background: #ffffff !important;
                border: 1px solid rgba(79, 157, 157, 0.22) !important;
                border-radius: 16px !important;
            }
            div[data-baseweb="select"] > div:focus-within {
                border-color: #6C8EF5 !important;
                box-shadow: 0 0 0 4px rgba(108, 142, 245, 0.14);
            }
            [data-testid="stTextArea"] textarea {
                background: #ffffff !important;
                color: var(--mindpulse-text) !important;
                border: 1px solid rgba(79, 157, 157, 0.22) !important;
                border-radius: 16px !important;
            }
            [data-testid="stTextArea"] textarea:focus {
                border-color: #6C8EF5 !important;
                box-shadow: 0 0 0 4px rgba(108, 142, 245, 0.14);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _clear_profile_state() -> None:
    for key in PROFILE_KEYS + list(PROFILE_FORM_KEYS.values()) + [
        "_loaded_profile_user_id",
        "_profile_form_synced_user_id",
        "profile_save_notice",
    ]:
        st.session_state.pop(key, None)


def _set_authenticated_account(account: dict[str, Any]) -> None:
    st.session_state["auth_user_id"] = account["user_id"]
    st.session_state["auth_role"] = account["role"]
    st.session_state["auth_email"] = account["email"]
    _clear_profile_state()


def logout_user() -> None:
    for key in ["auth_user_id", "auth_role", "auth_email", "chat_history", "last_checkin_result"]:
        st.session_state.pop(key, None)
    _clear_profile_state()


def _ensure_profile_loaded(user_id: str) -> None:
    if st.session_state.get("_loaded_profile_user_id") == user_id:
        return

    profile = get_profile(user_id)
    for key in PROFILE_KEYS:
        if key in profile:
            st.session_state[key] = profile[key]
    st.session_state["_loaded_profile_user_id"] = user_id


def _sync_profile_form_state(force: bool = False) -> None:
    user_id = st.session_state.get("_loaded_profile_user_id")
    synced_user_id = st.session_state.get("_profile_form_synced_user_id")
    has_all_form_keys = all(form_key in st.session_state for form_key in PROFILE_FORM_KEYS.values())

    if not user_id:
        return
    if not force and synced_user_id == user_id and has_all_form_keys:
        return

    for field, form_key in PROFILE_FORM_KEYS.items():
        st.session_state[form_key] = st.session_state.get(field)
    st.session_state["_profile_form_synced_user_id"] = user_id


def _render_brand() -> None:
    st.markdown(
        """
        <div class="site-brand">
            <span class="site-brand-mark"></span>
            <span>MindPulse AI</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_nav_links(slots: list[Any]) -> None:
    for slot, (page_path, icon, label) in zip(slots, NAV_LINKS):
        with slot:
            st.page_link(page_path, label=label, icon=icon)


def _save_profile(account: dict[str, Any]) -> None:
    updated = update_profile(
        {
            "user_id": account["user_id"],
            "name": st.session_state[PROFILE_FORM_KEYS["name"]],
            "course": st.session_state[PROFILE_FORM_KEYS["course"]],
            "year": st.session_state[PROFILE_FORM_KEYS["year"]],
            "campus": st.session_state.get("campus", "Main Campus"),
            "language": st.session_state[PROFILE_FORM_KEYS["language"]],
            "student_email": st.session_state[PROFILE_FORM_KEYS["student_email"]],
            "phone_number": st.session_state[PROFILE_FORM_KEYS["phone_number"]],
            "anonymous_mode": st.session_state[PROFILE_FORM_KEYS["anonymous_mode"]],
            "consent_alerts": st.session_state[PROFILE_FORM_KEYS["consent_alerts"]],
            "alert_contact": st.session_state[PROFILE_FORM_KEYS["alert_contact"]],
            "alert_channel": st.session_state[PROFILE_FORM_KEYS["alert_channel"]],
            "trusted_contact_email": st.session_state[PROFILE_FORM_KEYS["trusted_contact_email"]],
            "trusted_contact_phone": st.session_state[PROFILE_FORM_KEYS["trusted_contact_phone"]],
        }
    )
    for key in PROFILE_KEYS:
        if key in updated:
            st.session_state[key] = updated[key]
    st.session_state["_profile_form_synced_user_id"] = ""
    st.session_state["profile_save_notice"] = "Profile saved."
    st.rerun()


def _render_account_popover(account: dict[str, Any], provider_status: dict[str, Any]) -> None:
    _sync_profile_form_state()

    with st.popover("\U0001F464 Account"):
        st.caption(f"{account['email']} | role: {account['role'].title()}")
        with st.form("top_profile_form"):
            st.text_input("Name", key=PROFILE_FORM_KEYS["name"])
            st.text_input("Course", key=PROFILE_FORM_KEYS["course"])
            st.selectbox("Year", options=[1, 2, 3, 4, 5], key=PROFILE_FORM_KEYS["year"])
            st.selectbox("Language", options=["English", "Hindi", "Tamil"], key=PROFILE_FORM_KEYS["language"])
            st.text_input("Student Email", key=PROFILE_FORM_KEYS["student_email"])
            st.text_input("Phone Number", key=PROFILE_FORM_KEYS["phone_number"])
            st.toggle("Anonymous mode", key=PROFILE_FORM_KEYS["anonymous_mode"])
            st.toggle("Consent-based alerts", key=PROFILE_FORM_KEYS["consent_alerts"])
            st.text_input("Trusted contact name", key=PROFILE_FORM_KEYS["alert_contact"])
            st.selectbox("Contact type", options=["Mentor", "Friend", "Teacher"], key=PROFILE_FORM_KEYS["alert_channel"])
            st.text_input("Trusted contact email", key=PROFILE_FORM_KEYS["trusted_contact_email"])
            st.text_input("Trusted contact phone", key=PROFILE_FORM_KEYS["trusted_contact_phone"])
            save_submit = st.form_submit_button("Save Profile", use_container_width=True)
        if save_submit:
            _save_profile(account)

        with st.expander("Alert Providers", expanded=False):
            email_status = provider_status["email"]
            sms_status = provider_status["sms"]
            st.write(f"Real delivery enabled: {provider_status['real_delivery_enabled']}")
            st.write(f"Email provider: {email_status['provider']} | configured: {email_status['configured']}")
            if email_status["missing"]:
                st.caption("Email setup needs: " + ", ".join(email_status["missing"]))
            st.write(f"SMS provider: {sms_status['provider']} | configured: {sms_status['configured']}")
            if sms_status["missing"]:
                st.caption("SMS setup needs: " + ", ".join(sms_status["missing"]))

        if st.button("Logout", use_container_width=True, key="top_logout_button"):
            logout_user()
            st.rerun()


def render_site_header(
    account: dict[str, Any] | None = None,
    provider_status: dict[str, Any] | None = None,
) -> None:
    with st.container():
        st.markdown('<span class="top-nav-marker" style="display: none;"></span>', unsafe_allow_html=True)
        header_columns = st.columns([1.8, 1.0, 1.1, 1.15, 1.1, 1.15, 1.0, 1.0, 1.35], vertical_alignment="center")
        with header_columns[0]:
            _render_brand()
        _render_nav_links(header_columns[1:8])
        with header_columns[8]:
            if account and provider_status:
                _render_account_popover(account, provider_status)
            else:
                st.caption("Wellness hub")


def _render_auth_shell() -> None:
    render_site_header()
    st.markdown(
        """
        <div class="hero-panel auth-hero-panel">
            <span class="brand-kicker">MindPulse AI</span>
            <h1>Welcome Back</h1>
            <p>Sign in to open your wellness workspace, check-ins, support tools, and consent-based alert settings.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left, center, right = st.columns([0.8, 1.35, 0.8])
    with center:
        login_tab, register_tab = st.tabs(["Login", "Register"])

        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                login_submit = st.form_submit_button("Sign In", use_container_width=True)
            if login_submit:
                try:
                    account = login_user({"email": email, "password": password})
                except Exception as exc:
                    st.error(str(exc))
                else:
                    _set_authenticated_account(account)
                    st.rerun()

            st.info(
                "Demo student: demo@studentwellness.local / Demo@12345\n\n"
                "Demo counselor: counselor@studentwellness.local / Counselor@123"
            )

        with register_tab:
            with st.form("register_form"):
                name = st.text_input("Full Name")
                email = st.text_input("College Email")
                phone_number = st.text_input("Phone Number")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                course = st.text_input("Course", value="B.Tech CSE")
                year = st.selectbox("Year", options=[1, 2, 3, 4, 5], index=1)
                language = st.selectbox("Language", options=["English", "Hindi", "Tamil"])
                register_submit = st.form_submit_button("Create Account", use_container_width=True)
            if register_submit:
                try:
                    account = register_user(
                        {
                            "name": name,
                            "email": email,
                            "phone_number": phone_number,
                            "password": password,
                            "confirm_password": confirm_password,
                            "course": course,
                            "year": year,
                            "language": language,
                        }
                    )
                except Exception as exc:
                    st.error(str(exc))
                else:
                    _set_authenticated_account(account)
                    st.success("Account created successfully.")
                    st.rerun()


def require_login() -> dict[str, Any]:
    auth_user_id = st.session_state.get("auth_user_id")
    if auth_user_id:
        account = get_account(auth_user_id)
        if account:
            st.session_state["auth_role"] = account["role"]
            st.session_state["auth_email"] = account["email"]
            return account
        logout_user()

    _render_auth_shell()
    st.stop()


def render_sidebar_profile() -> dict[str, Any]:
    account = require_login()
    _ensure_profile_loaded(account["user_id"])
    provider_status = get_alert_provider_status()
    render_site_header(account, provider_status)
    save_notice = st.session_state.pop("profile_save_notice", None)
    if save_notice:
        st.success(save_notice)

    return {
        "user_id": account["user_id"],
        "name": st.session_state["name"],
        "course": st.session_state["course"],
        "year": st.session_state["year"],
        "campus": st.session_state.get("campus", "Main Campus"),
        "language": st.session_state["language"],
        "student_email": st.session_state["student_email"],
        "phone_number": st.session_state["phone_number"],
        "anonymous_mode": st.session_state["anonymous_mode"],
        "consent_alerts": st.session_state["consent_alerts"],
        "alert_contact": st.session_state["alert_contact"],
        "alert_channel": st.session_state["alert_channel"],
        "trusted_contact_email": st.session_state["trusted_contact_email"],
        "trusted_contact_phone": st.session_state["trusted_contact_phone"],
        "role": account["role"],
        "email": account["email"],
    }


def render_notifications(notifications: list[dict]) -> None:
    for item in notifications:
        box = {
            "success": st.success,
            "warning": st.warning,
            "error": st.error,
            "info": st.info,
        }.get(item.get("level", "info"), st.info)
        box(f"{item['title']}: {item['message']}")
