"""Fonctions HTML réutilisables pour reproduire les cartes du prototype."""

from __future__ import annotations

import streamlit as st


def page_header(title: str, subtitle: str, badge: str | None = None) -> None:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"# {title}")
        st.markdown(f"<div class='subtitle'>{subtitle}</div>", unsafe_allow_html=True)
    if badge:
        with col2:
            st.markdown(
                f"<div style='text-align:right;margin-top:18px;'>"
                f"<span class='badge'>● {badge}</span></div>",
                unsafe_allow_html=True,
            )
    st.write("")


def kpi_card(label: str, value: str, delta: str | None = None) -> None:
    delta_html = f"<div class='kpi-delta'>{delta}</div>" if delta else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def pill(text: str, color: str) -> str:
    """color: 'green' | 'orange' | 'red'"""
    return f"<span class='pill pill-{color}'>{text}</span>"


def ivory_metric(label: str, value: str) -> str:
    return f"<div class='ivory-metric'><div class='label'>{label}</div><span class='value'>{value}</span></div>"


def ivory_metric_row(items: list[tuple[str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        with col:
            st.markdown(ivory_metric(label, value), unsafe_allow_html=True)


def segment_card(name: str, count: str, unit: str, pill_text: str, pill_color: str) -> None:
    with st.container(border=True):
        st.markdown(f"#### {name}")
        st.markdown(f"<div style='font-size:23px;font-weight:800;color:#16233F;'>{count}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='note'>{unit}</div>", unsafe_allow_html=True)
        st.markdown(pill(pill_text, pill_color), unsafe_allow_html=True)


def result_box(risk_value: str, risk_label: str, risk_color: str, recommendation: str) -> None:
    st.markdown(
        f"""
        <div class="result-box">
            <div class="risk-value" style="color:{risk_color};">{risk_value}</div>
            <div>{pill(risk_label, 'green' if risk_color == '#5B7F5E' else ('orange' if risk_color == '#C6862E' else 'red'))}</div>
            <div class="reco-box"><b>Recommandation :</b><br>{recommendation}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def not_available_box(title: str, message: str) -> None:
    st.markdown(
        f"""
        <div class="result-box" style="border-left-color:#A8452F;">
            <b style="color:#A8452F;">{title}</b><br>
            <span class="note">{message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
