"""Sidebar façon prototype : marque + navigation verticale par boutons."""

import streamlit as st

NAV_ITEMS = [
    ("overview", "▦  Vue globale"),
    ("segments", "◉  Segments clients"),
    ("campaigns", "↗  Campagnes"),
    ("predict", "✦  Simulateur ML"),
    ("strategy", "◎  Recommandations"),
]


def render_sidebar() -> str:
    if "active_page" not in st.session_state:
        st.session_state.active_page = "overview"

    with st.sidebar:
        st.markdown(
            "<div style='font-size:20px;font-weight:800;padding:4px 4px 4px;color:#fff;'>"
            "MarketIQ"
            "<small style='display:block;color:#b9c4d7;font-size:11px;font-weight:500;margin-top:5px;'>"
            "Marketing Intelligence</small></div><br>",
            unsafe_allow_html=True,
        )
        for key, label in NAV_ITEMS:
            is_active = st.session_state.active_page == key
            if st.button(label, key=f"nav_{key}", type="primary" if is_active else "secondary"):
                st.session_state.active_page = key
                st.rerun()

    return st.session_state.active_page
