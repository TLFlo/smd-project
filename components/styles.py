"""Injection du CSS global reproduisant fidèlement le prototype HTML.

Palette (identique au prototype) :
  NAVY #16233F | AMBER #C6862E | IVORY #F6F3EC | SAGE #5B7F5E | BRICK #A8452F
  TEXT #243044 | MUTED #738096 | WHITE #FFFFFF | LINE #E6E9EE
"""

import streamlit as st

COLORS = {
    "navy": "#16233F",
    "amber": "#C6862E",
    "ivory": "#F6F3EC",
    "sage": "#5B7F5E",
    "brick": "#A8452F",
    "text": "#243044",
    "muted": "#738096",
    "white": "#FFFFFF",
    "line": "#E6E9EE",
    "bg": "#F7F8FA",
}


def inject_global_css() -> None:
    c = COLORS
    st.markdown(
        f"""
        <style>
        /* ---- Fond général ---- */
        .stApp {{ background-color: {c['bg']}; }}
        [data-testid="stAppViewContainer"] > .main {{ background-color: {c['bg']}; }}
        .block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}

        /* ---- Sidebar façon prototype (navy, nav verticale) ---- */
        section[data-testid="stSidebar"] {{
            background-color: {c['navy']};
            min-width: 250px !important;
            max-width: 260px !important;
        }}
        section[data-testid="stSidebar"] * {{ color: #cbd4e4 !important; }}
        section[data-testid="stSidebar"] .stButton button {{
            width: 100%;
            text-align: left;
            background: transparent;
            border: none;
            color: #cbd4e4 !important;
            padding: 10px 13px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 3px;
        }}
        section[data-testid="stSidebar"] .stButton button:hover {{
            background: rgba(255,255,255,.10);
            color: #fff !important;
        }}
        section[data-testid="stSidebar"] .stButton button[kind="primary"] {{
            background: rgba(255,255,255,.14) !important;
            color: #fff !important;
            font-weight: 700;
        }}

        /* ---- Cartes (st.container(border=True)) façon prototype ---- */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: {c['white']};
            border: 1px solid {c['line']};
            border-radius: 14px;
            box-shadow: 0 8px 24px rgba(22,35,63,.07);
            padding: 6px 10px;
        }}

        /* ---- Titres ---- */
        h1 {{ color: {c['navy']}; font-weight: 800; }}
        h2, h3, h4 {{ color: {c['navy']}; }}
        .subtitle {{ color: {c['muted']}; font-size: 13px; margin-top: -8px; }}

        /* ---- KPI cards (HTML custom) ---- */
        .kpi-card {{
            background: {c['white']};
            border: 1px solid {c['line']};
            border-radius: 14px;
            padding: 18px 19px;
            box-shadow: 0 8px 24px rgba(22,35,63,.07);
        }}
        .kpi-label {{ font-size: 12px; color: {c['muted']}; font-weight: 700; letter-spacing: .03em; text-transform: uppercase; }}
        .kpi-value {{ font-size: 26px; font-weight: 800; color: {c['navy']}; margin: 8px 0 4px; }}
        .kpi-delta {{ font-size: 11px; color: {c['sage']}; font-weight: 700; }}

        /* ---- Badge "Données actualisées" ---- */
        .badge {{
            background: #eaf3eb; color: {c['sage']};
            padding: 8px 12px; border-radius: 20px;
            font-size: 12px; font-weight: 700; display: inline-block;
        }}

        /* ---- Pills de statut ---- */
        .pill {{ display: inline-block; border-radius: 20px; padding: 5px 10px; font-size: 11px; font-weight: 700; }}
        .pill-green {{ background: #eaf3eb; color: {c['sage']}; }}
        .pill-orange {{ background: #fbf1df; color: #9a651b; }}
        .pill-red {{ background: #fae9e5; color: {c['brick']}; }}

        /* ---- Métriques ivoire (profil de segment) ---- */
        .ivory-metric {{
            background: {c['ivory']};
            border-radius: 10px;
            padding: 12px;
            text-align: center;
        }}
        .ivory-metric .label {{ font-size: 12px; color: {c['muted']}; }}
        .ivory-metric .value {{ display: block; color: {c['navy']}; font-size: 17px; font-weight: 800; margin-top: 4px; }}

        /* ---- Carte résultat prédiction ---- */
        .result-box {{
            margin-top: 10px; padding: 18px; border-radius: 12px;
            background: #f5f8fc; border-left: 5px solid {c['navy']};
        }}
        .risk-value {{ font-size: 34px; font-weight: 900; }}

        /* ---- Carte recommandation ---- */
        .reco-box {{
            margin-top: 12px; background: #eef5ef; border-radius: 10px;
            padding: 13px; color: #36513a; font-size: 13px;
        }}

        .note {{ font-size: 11px; color: {c['muted']}; line-height: 1.5; }}

        /* ---- Tableaux HTML custom (ex: recommandations) ---- */
        .stMarkdown table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
        .stMarkdown th, .stMarkdown td {{ text-align: left; padding: 11px; border-bottom: 1px solid {c['line']}; }}
        .stMarkdown th {{ color: {c['muted']}; font-weight: 700; }}

        /* ---- Bouton principal (action) ---- */
        .stButton > button[kind="primary"] {{
            background-color: {c['navy']};
            border-color: {c['navy']};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
