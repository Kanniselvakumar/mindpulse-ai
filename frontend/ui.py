from __future__ import annotations

import base64
from pathlib import Path
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

LOGO_PATH = Path(__file__).resolve().parent / "assets" / "mindpulse_logo.png"


@st.cache_data
def get_logo_data_uri() -> str:
    if LOGO_PATH.exists():
        encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    return ""


NAV_LINKS = [
    ("Home.py", "\U0001F3E0", "Home"),
    ("pages/1_Daily_Check_In.py", "\U0001F4DD", "Check-In"),
    ("pages/2_Mood_Dashboard.py", "\U0001F4CA", "Dashboard"),
    ("pages/3_AI_Support_Companion.py", "\U0001F4AC", "Support"),
    ("pages/4_Resource_Hub.py", "\U0001F9ED", "Resources"),
    ("pages/5_Peer_Support.py", "\U0001F91D", "Peers"),
    ("pages/6_Counselor_Insights.py", "\U0001F6E1", "Insights"),
    ("pages/7_Realtime_Dataset_Studio.py", "⚡", "Realtime"),
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
    "student_email",
    "phone_number",
    "consent_alerts",
    "trusted_contact_email",
    "trusted_contact_phone",
]

PROFILE_FORM_KEYS = {
    field: f"profile_form_{field}" for field in PROFILE_FORM_FIELDS
}

# Fixed pixel height of the navbar, plus the breathing room around it.
# All three are used both by the CSS that pins/pads the bar and by the CSS
# that reserves the equivalent space at the top of the page, so content
# never renders underneath (or jumps around under) the bar.
NAVBAR_HEIGHT_PX = 64
NAVBAR_TOP_GAP_PX = 18       # space between the browser edge and the bar
NAVBAR_BOTTOM_GAP_PX = 40    # space between the bar and the page content below it


def apply_branding() -> None:
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

            :root {{
                --mindpulse-primary: #14B8A6;
                --mindpulse-secondary: #2DD4BF;
                --mindpulse-background: #0B0F19;
                --mindpulse-accent: #6366F1;
                --mindpulse-danger: #F43F5E;
                --mindpulse-warning: #F59E0B;
                --mindpulse-safe: #10B981;
                --mindpulse-text: #F8FAFC;
                --mp-navbar-height: {NAVBAR_HEIGHT_PX}px;
            }}

            /* ── Kill every default top offset that pushes content around ── */
            html, body {{
                margin: 0 !important;
                padding: 0 !important;
                scroll-behavior: smooth;
            }}
            .stApp, [data-testid="stApp"] {{
                background:
                    radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.15), transparent 45%),
                    radial-gradient(circle at 90% 80%, rgba(20, 184, 166, 0.12), transparent 45%),
                    #0B0F19;
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                color: #F8FAFC !important;
                margin: 0 !important;
            }}
            h1, h2, h3, h4, h5, h6 {{
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                font-weight: 700 !important;
                letter-spacing: -0.02em !important;
                color: #FFFFFF !important;
            }}
            section[data-testid="stSidebar"],
            div[data-testid="stSidebarNav"],
            div[data-testid="collapsedControl"],
            [data-testid="stSidebarCollapseButton"],
            [data-testid="stSidebarCollapsedControl"],
            header[data-testid="stHeader"],
            header[data-testid="stAppHeader"] {{
                display: none !important;
                height: 0 !important;
                min-height: 0 !important;
            }}
            [data-testid="stAppViewContainer"],
            [data-testid="stAppViewContainer"] > div:first-child,
            [data-testid="stMain"] {{
                padding-top: 0 !important;
                margin-top: 0 !important;
            }}
            [data-testid="stMain"] > div {{
                gap: 0 !important;
            }}
            /* Reserve a fixed slot for the navbar so page content NEVER shifts,
               regardless of what's rendered above/below it on a given page. */
            .block-container {{
                padding-top: calc(var(--mp-navbar-height) + 2rem) !important;
                padding-bottom: 3rem !important;
                max-width: 100% !important;
            }}
            [data-testid="InputInstructions"] {{
                display: none !important;
            }}

            /* ── Fixed Top Navbar ──────────────────────────────────────────
               Targeted via stable container key and multi-version Streamlit selectors */
            div.st-key-mp-navbar {{
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                width: 100vw !important;
                max-width: 100vw !important;
                z-index: 9999999 !important;
                height: var(--mp-navbar-height) !important;
                min-height: var(--mp-navbar-height) !important;
                max-height: var(--mp-navbar-height) !important;
                margin: 0 !important;
                padding: 0 1.5rem !important;
                background: rgba(11, 15, 25, 0.85) !important;
                backdrop-filter: blur(20px) saturate(160%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(160%) !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
                box-sizing: border-box !important;
                display: flex !important;
                align-items: center !important;
            }}
            div.st-key-mp-navbar > div,
            div.st-key-mp-navbar [data-testid="stVerticalBlockBorderWrapper"],
            div.st-key-mp-navbar [data-testid="stVerticalBlock"] {{
                width: 100% !important;
                max-width: 100% !important;
                display: flex !important;
                align-items: center !important;
                padding: 0 !important;
                margin: 0 !important;
            }}
            div.st-key-mp-navbar div[data-testid="stHorizontalBlock"] {{
                display: flex !important;
                flex-direction: row !important;
                align-items: center !important;
                justify-content: flex-start !important;
                flex-wrap: nowrap !important;
                gap: 0.35rem !important;
                width: 100% !important;
                overflow-x: auto !important;
                overflow-y: hidden !important;
                scrollbar-width: none !important;
                -ms-overflow-style: none !important;
            }}
            div.st-key-mp-navbar div[data-testid="stHorizontalBlock"]::-webkit-scrollbar {{
                display: none !important;
            }}

            /* Nav columns: strictly stay in the same line */
            div.st-key-mp-navbar div[data-testid="stColumn"],
            div.st-key-mp-navbar div[data-testid="column"],
            div.st-key-mp-navbar .stColumn {{
                width: auto !important;
                min-width: max-content !important;
                max-width: none !important;
                flex: 0 0 auto !important;
                padding: 0 !important;
                margin: 0 !important;
                display: inline-flex !important;
                align-items: center !important;
            }}
            div.st-key-mp-navbar div[data-testid="stColumn"]:first-child,
            div.st-key-mp-navbar div[data-testid="column"]:first-child {{
                margin-right: 1.25rem !important;
                flex-shrink: 0 !important;
            }}
            div.st-key-mp-navbar div[data-testid="stColumn"]:last-child:not(:first-child),
            div.st-key-mp-navbar div[data-testid="column"]:last-child:not(:first-child) {{
                margin-left: auto !important;
                padding-left: 0.75rem !important;
                flex-shrink: 0 !important;
            }}

            @media (max-width: 992px) {{
                div.st-key-mp-navbar div[data-testid="stColumn"],
                div.st-key-mp-navbar div[data-testid="column"],
                div.st-key-mp-navbar .stColumn {{
                    width: auto !important;
                    min-width: max-content !important;
                    max-width: none !important;
                    flex: 0 0 auto !important;
                }}
                div.st-key-mp-navbar div[data-testid="stHorizontalBlock"] {{
                    flex-direction: row !important;
                    flex-wrap: nowrap !important;
                }}
            }}

            /* Container elements inside navbar */
            div.st-key-mp-navbar div[data-testid="stElementContainer"],
            div.st-key-mp-navbar div[data-testid="element-container"],
            div.st-key-mp-navbar div[data-testid="stVerticalBlock"],
            div.st-key-mp-navbar .stElementContainer {{
                margin: 0 !important;
                padding: 0 !important;
                gap: 0 !important;
                width: auto !important;
                min-width: 0 !important;
                display: inline-flex !important;
                align-items: center !important;
            }}

            /* Nav links styling */
            div.st-key-mp-navbar div[data-testid="stPageLink"],
            div.st-key-mp-navbar .stPageLink {{
                margin: 0 2px !important;
                padding: 0 !important;
                display: inline-flex !important;
                align-items: center !important;
                width: auto !important;
            }}
            div.st-key-mp-navbar div[data-testid="stPageLink"] a,
            div.st-key-mp-navbar div[data-testid="stPageLink-NavLink"] a,
            div.st-key-mp-navbar .stPageLink a {{
                position: relative !important;
                height: 38px !important;
                min-height: 38px !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 0.45rem !important;
                padding: 0 0.85rem !important;
                border-radius: 10px !important;
                border: 1px solid transparent !important;
                background: rgba(255, 255, 255, 0.02) !important;
                color: #94A3B8 !important;
                font-weight: 500 !important;
                font-size: 0.84rem !important;
                white-space: nowrap !important;
                text-decoration: none !important;
                box-shadow: none !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
                cursor: pointer !important;
            }}
            div.st-key-mp-navbar div[data-testid="stPageLink"] a p,
            div.st-key-mp-navbar div[data-testid="stPageLink"] a span,
            div.st-key-mp-navbar div[data-testid="stPageLink"] a div,
            div.st-key-mp-navbar .stPageLink a p,
            div.st-key-mp-navbar .stPageLink a span {{
                color: inherit !important;
                font-size: 0.84rem !important;
                font-weight: inherit !important;
                margin: 0 !important;
                padding: 0 !important;
                line-height: 1 !important;
                white-space: nowrap !important;
            }}

            div.st-key-mp-navbar div[data-testid="stPageLink"] a:hover,
            div.st-key-mp-navbar .stPageLink a:hover {{
                background: rgba(255, 255, 255, 0.08) !important;
                color: #F8FAFC !important;
                border-color: rgba(255, 255, 255, 0.05) !important;
                transform: translateY(-1px) !important;
            }}
            div.st-key-mp-navbar div[data-testid="stPageLink"] a[aria-current="page"],
            div.st-key-mp-navbar .stPageLink a[aria-current="page"],
            div.st-key-mp-navbar div[data-testid="stPageLink"] a.active,
            div.st-key-mp-navbar .stPageLink a.active {{
                color: #FFFFFF !important;
                background: rgba(20, 184, 166, 0.14) !important;
                border: 1px solid rgba(20, 184, 166, 0.3) !important;
                font-weight: 600 !important;
            }}
            /* Active indicator line */
            div.st-key-mp-navbar div[data-testid="stPageLink"] a[aria-current="page"]::after,
            div.st-key-mp-navbar .stPageLink a[aria-current="page"]::after {{
                content: "" !important;
                position: absolute !important;
                left: 10px !important;
                right: 10px !important;
                bottom: -1px !important;
                height: 2.5px !important;
                border-radius: 3px !important;
                background: linear-gradient(90deg, #14B8A6, #6366F1) !important;
                box-shadow: 0 0 10px rgba(20, 184, 166, 0.8) !important;
            }}

            /* Account popover trigger */
            div.st-key-mp-navbar div[data-testid="stPopover"],
            div.st-key-mp-navbar .stPopover {{
                display: inline-flex !important;
                align-items: center !important;
            }}
            div.st-key-mp-navbar div[data-testid="stPopover"] button,
            div.st-key-mp-navbar .stPopover button {{
                height: 38px !important;
                min-height: 38px !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 0.45rem !important;
                padding: 0 1rem !important;
                border-radius: 999px !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                background: rgba(255, 255, 255, 0.05) !important;
                color: #E2E8F0 !important;
                font-weight: 600 !important;
                font-size: 0.82rem !important;
                white-space: nowrap !important;
                box-shadow: none !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }}
            div.st-key-mp-navbar div[data-testid="stPopover"] button:hover,
            div.st-key-mp-navbar .stPopover button:hover {{
                background: rgba(20, 184, 166, 0.15) !important;
                border-color: rgba(20, 184, 166, 0.45) !important;
                color: #FFFFFF !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 12px rgba(20, 184, 166, 0.2) !important;
            }}

            div[data-testid="stMetric"] {{
                background: rgba(30, 41, 59, 0.4) !important;
                backdrop-filter: blur(12px) !important;
                -webkit-backdrop-filter: blur(12px) !important;
                border: 1px solid rgba(255, 255, 255, 0.06) !important;
                padding: 1rem 1.25rem !important;
                border-radius: 18px !important;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15) !important;
                transition: all 0.3s ease !important;
            }}
            div[data-testid="stMetric"]:hover {{
                transform: translateY(-2px) !important;
                box-shadow: 0 15px 30px rgba(0, 0, 0, 0.25) !important;
                border-color: rgba(20, 184, 166, 0.3) !important;
            }}
            div[data-testid="stMetric"] [data-testid="stMetricLabel"] p {{
                color: #94A3B8 !important;
                font-weight: 500 !important;
                font-size: 0.9rem !important;
            }}
            div[data-testid="stMetric"] [data-testid="stMetricValue"] div {{
                color: #FFFFFF !important;
                font-weight: 700 !important;
                font-size: 1.8rem !important;
            }}
            .wellness-card {{
                background: rgba(30, 41, 59, 0.45) !important;
                backdrop-filter: blur(12px) !important;
                -webkit-backdrop-filter: blur(12px) !important;
                border: 1px solid rgba(255, 255, 255, 0.06) !important;
                border-radius: 20px !important;
                padding: 1.25rem !important;
                margin-bottom: 1rem !important;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15) !important;
                transition: all 0.3s ease !important;
                color: #E2E8F0 !important;
            }}
            .wellness-card:hover {{
                transform: translateY(-3px) !important;
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25) !important;
                border-color: rgba(99, 102, 241, 0.3) !important;
                background: rgba(30, 41, 59, 0.6) !important;
            }}
            .site-brand {{
                display: inline-flex !important;
                align-items: center !important;
                gap: 0.65rem !important;
                color: #FFFFFF !important;
                font-weight: 800 !important;
                font-size: 1.15rem !important;
                letter-spacing: -0.01em !important;
                white-space: nowrap !important;
                text-decoration: none !important;
            }}
            .site-brand-logo {{
                width: 32px !important;
                height: 32px !important;
                object-fit: contain !important;
                border-radius: 8px !important;
                filter: drop-shadow(0 2px 8px rgba(20, 184, 166, 0.45)) !important;
                flex-shrink: 0 !important;
            }}
            .site-brand-mark {{
                width: 14px;
                height: 14px;
                border-radius: 50%;
                background: linear-gradient(135deg, #14B8A6 0%, #6366F1 100%) !important;
                box-shadow: 0 0 0 6px rgba(20, 184, 166, 0.2) !important;
            }}
            .hero-panel {{
                position: relative;
                overflow: hidden;
                background: linear-gradient(135deg, rgba(13, 148, 136, 0.9) 0%, rgba(99, 102, 241, 0.8) 100%) !important;
                color: #FFFFFF !important;
                border-radius: 24px !important;
                padding: 2.25rem !important;
                margin-bottom: 2rem !important;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
            }}
            .hero-panel::before {{
                content: "";
                position: absolute;
                width: 180px;
                height: 180px;
                top: -54px;
                right: -24px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.08);
            }}
            .hero-panel::after {{
                content: "";
                position: absolute;
                width: 110px;
                height: 110px;
                bottom: -30px;
                right: 24%;
                border-radius: 26px;
                transform: rotate(22deg);
                background: rgba(255, 255, 255, 0.06);
            }}
            .hero-panel h1, .hero-panel p {{
                color: #FFFFFF !important;
                position: relative;
                z-index: 1;
            }}
            .brand-kicker {{
                position: relative;
                z-index: 1;
                display: inline-block;
                margin-bottom: 0.8rem;
                padding: 0.35rem 0.9rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.15) !important;
                color: #FFFFFF !important;
                font-size: 0.8rem;
                font-weight: 700;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }}
            .brand-pill-row {{
                position: relative;
                z-index: 1;
                display: flex;
                flex-wrap: wrap;
                gap: 0.55rem;
                margin-top: 1.2rem;
            }}
            .brand-pill {{
                padding: 0.4rem 1rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.1) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                color: #F8FAFC !important;
                font-size: 0.85rem;
                font-weight: 500;
            }}
            .auth-hero-panel {{
                background: linear-gradient(135deg, #14B8A6 0%, #6366F1 100%) !important;
            }}
            .stButton > button {{
                background: linear-gradient(135deg, #14B8A6 0%, #6366F1 100%) !important;
                color: #FFFFFF !important;
                border: 0 !important;
                border-radius: 12px !important;
                font-weight: 600 !important;
                padding: 0.5rem 1.5rem !important;
                box-shadow: 0 8px 20px rgba(99, 102, 241, 0.2) !important;
                transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }}
            .stButton > button:hover {{
                color: #FFFFFF !important;
                border: 0 !important;
                transform: translateY(-1.5px) !important;
                box-shadow: 0 12px 25px rgba(99, 102, 241, 0.3) !important;
                filter: brightness(1.08) !important;
            }}
            .stButton > button:active {{
                transform: translateY(0.5px) !important;
            }}
            div[data-baseweb="tab-list"] {{
                gap: 0.5rem !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
                padding-bottom: 0.5rem !important;
            }}
            div[data-baseweb="tab-list"] button {{
                background: transparent !important;
                border-radius: 10px !important;
                color: #94A3B8 !important;
                font-weight: 600 !important;
                border: none !important;
                padding: 0.6rem 1.2rem !important;
                transition: all 0.25s ease !important;
            }}
            div[data-baseweb="tab-list"] button[aria-selected="true"] {{
                background: rgba(255, 255, 255, 0.05) !important;
                color: #FFFFFF !important;
            }}
            div[data-baseweb="tab-highlight"] {{
                background-color: #14B8A6 !important;
                height: 3px !important;
                border-radius: 3px !important;
            }}
            div[data-testid="stChatMessage"] {{
                background: rgba(30, 41, 59, 0.35) !important;
                border: 1px solid rgba(255, 255, 255, 0.05) !important;
                border-radius: 16px !important;
                padding: 0.75rem 1rem !important;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
                margin-bottom: 0.75rem !important;
            }}
            div[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {{
                color: #F8FAFC !important;
            }}
            div[data-testid="stForm"] {{
                background: rgba(30, 41, 59, 0.4) !important;
                backdrop-filter: blur(12px) !important;
                border: 1px solid rgba(255, 255, 255, 0.06) !important;
                border-radius: 20px !important;
                padding: 1.5rem !important;
            }}
            div[data-baseweb="base-input"] {{
                background: rgba(15, 23, 42, 0.6) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 16px !important;
                box-shadow: none !important;
            }}
            div[data-baseweb="base-input"]:focus-within {{
                border-color: #6366F1 !important;
                box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2) !important;
            }}
            div[data-baseweb="base-input"] input {{
                color: #F8FAFC !important;
                background: transparent !important;
            }}
            div[data-baseweb="select"] > div {{
                background: rgba(15, 23, 42, 0.6) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 16px !important;
            }}
            div[data-baseweb="select"] > div:focus-within {{
                border-color: #6366F1 !important;
                box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2) !important;
            }}
            [data-testid="stTextArea"] textarea {{
                background: rgba(15, 23, 42, 0.6) !important;
                color: #F8FAFC !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 16px !important;
            }}
            [data-testid="stTextArea"] textarea:focus {{
                border-color: #6366F1 !important;
                box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2) !important;
            }}
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


def get_current_page_name() -> str:
    import inspect
    import os
    for frame in inspect.stack():
        filename = frame.filename
        if filename.endswith(".py") and not filename.endswith("ui.py"):
            return os.path.basename(filename)
    return ""


def _ensure_profile_loaded(user_id: str) -> None:
    all_keys_loaded = all(k in st.session_state for k in PROFILE_KEYS)
    if st.session_state.get("_loaded_profile_user_id") == user_id and all_keys_loaded:
        return

    profile = get_profile(user_id)
    for key in PROFILE_KEYS:
        st.session_state[key] = profile.get(key)
    st.session_state["_loaded_profile_user_id"] = user_id


def _sync_profile_form_state(force: bool = False) -> None:
    user_id = st.session_state.get("_loaded_profile_user_id")
    if not user_id:
        return

    # Automatically force-sync when switching pages in Streamlit
    current_page = get_current_page_name()
    last_page = st.session_state.get("_last_seen_page", "")
    if current_page and last_page != current_page:
        force = True
        st.session_state["_last_seen_page"] = current_page

    for field, form_key in PROFILE_FORM_KEYS.items():
        if form_key not in st.session_state or force:
            st.session_state[form_key] = st.session_state.get(field)


def _render_brand() -> None:
    logo_src = get_logo_data_uri()
    img_tag = (
        f'<img src="{logo_src}" class="site-brand-logo" alt="MindPulse Logo" />'
        if logo_src
        else '<span class="site-brand-mark"></span>'
    )
    st.markdown(
        f"""
        <div class="site-brand">
            {img_tag}
            <span class="site-brand-text">MindPulse AI</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _save_profile(account: dict[str, Any]) -> None:
    updated = update_profile(
        {
            "user_id": account["user_id"],
            "name": st.session_state[PROFILE_FORM_KEYS["name"]],
            "course": st.session_state[PROFILE_FORM_KEYS["course"]],
            "year": st.session_state[PROFILE_FORM_KEYS["year"]],
            "campus": st.session_state.get("campus", "Main Campus"),
            "language": "English",
            "student_email": st.session_state[PROFILE_FORM_KEYS["student_email"]],
            "phone_number": st.session_state[PROFILE_FORM_KEYS["phone_number"]],
            "anonymous_mode": False,
            "consent_alerts": st.session_state[PROFILE_FORM_KEYS["consent_alerts"]],
            "alert_contact": "Trusted Contact",
            "alert_channel": "Mentor",
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
            st.text_input("Student Email", key=PROFILE_FORM_KEYS["student_email"])
            st.text_input("Phone Number", key=PROFILE_FORM_KEYS["phone_number"])
            st.toggle("Consent-based alerts", key=PROFILE_FORM_KEYS["consent_alerts"])
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


def _render_navbar_auth_popover() -> None:
    with st.popover("🔑 Login / Sign Up"):
        login_tab, reg_tab = st.tabs(["Sign In", "Register"])
        with login_tab:
            with st.form("nav_login_form"):
                nav_email = st.text_input("Email", key="nav_login_email")
                nav_pwd = st.text_input("Password", type="password", key="nav_login_pwd")
                nav_submit = st.form_submit_button("Sign In", use_container_width=True)
            if nav_submit:
                try:
                    account = login_user({"email": nav_email, "password": nav_pwd})
                except Exception as exc:
                    st.error(str(exc))
                else:
                    _set_authenticated_account(account)
                    st.rerun()

            st.caption("Demo: `demo@studentwellness.local` / `Demo@12345`")
            if st.button("⚡ Quick Demo Sign In", key="nav_demo_login_btn", use_container_width=True):
                try:
                    account = login_user({"email": "demo@studentwellness.local", "password": "Demo@12345"})
                    _set_authenticated_account(account)
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        with reg_tab:
            with st.form("nav_reg_form"):
                reg_name = st.text_input("Full Name", key="nav_reg_name")
                reg_email = st.text_input("College Email", key="nav_reg_email")
                reg_pwd = st.text_input("Password", type="password", key="nav_reg_pwd")
                reg_course = st.text_input("Course", value="B.Tech CSE", key="nav_reg_course")
                reg_year = st.selectbox("Year", options=[1, 2, 3, 4, 5], index=1, key="nav_reg_year")
                reg_submit = st.form_submit_button("Create Account", use_container_width=True)
            if reg_submit:
                try:
                    account = register_user(
                        {
                            "name": reg_name,
                            "email": reg_email,
                            "phone_number": "",
                            "password": reg_pwd,
                            "confirm_password": reg_pwd,
                            "course": reg_course,
                            "year": reg_year,
                            "language": "English",
                        }
                    )
                except Exception as exc:
                    st.error(str(exc))
                else:
                    _set_authenticated_account(account)
                    st.success("Account created successfully.")
                    st.rerun()


def render_site_header(
    account: dict[str, Any] | None = None,
    provider_status: dict[str, Any] | None = None,
    current_page: str = "",
) -> None:
    # Key 'mp-navbar' pins this container to top
    with st.container(key="mp-navbar"):
        col_weights = [1.6] + [1.0] * len(NAV_LINKS) + [1.2]
        header_columns = st.columns(col_weights, vertical_alignment="center")
        with header_columns[0]:
            _render_brand()

        for slot, (page_path, icon, label) in zip(header_columns[1 : 1 + len(NAV_LINKS)], NAV_LINKS):
            with slot:
                st.page_link(page_path, label=label, icon=icon)

        with header_columns[-1]:
            if account and provider_status:
                _render_account_popover(account, provider_status)
            else:
                _render_navbar_auth_popover()


def _render_auth_shell() -> None:
    render_site_header()
    logo_src = get_logo_data_uri()
    logo_img = (
        f'<img src="{logo_src}" style="width: 58px; height: 58px; margin-bottom: 0.75rem; border-radius: 12px; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.3));" alt="MindPulse Logo"/>'
        if logo_src
        else ""
    )
    st.markdown(
        f"""
        <div class="hero-panel auth-hero-panel">
            {logo_img}
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
                            "language": "English",
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


def render_sidebar_profile(require_auth: bool = True) -> dict[str, Any] | None:
    auth_user_id = st.session_state.get("auth_user_id")
    account = None
    if auth_user_id:
        account = get_account(auth_user_id)
        if account:
            st.session_state["auth_role"] = account["role"]
            st.session_state["auth_email"] = account["email"]
        else:
            logout_user()

    if not account:
        if require_auth:
            _render_auth_shell()
            st.stop()
        else:
            provider_status = get_alert_provider_status()
            render_site_header(account=None, provider_status=provider_status)
            return None

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