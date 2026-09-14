import importlib

import streamlit as st

from components.sidebar import render_sidebar
from components.styles import inject_global_css
from utils.data_loader import load_all

st.set_page_config(page_title="MarketIQ — Marketing Intelligence", page_icon="📊", layout="wide")
inject_global_css()

active_page = render_sidebar()

customers = load_all()

PAGES = {
    "overview": "views.global_page",
    "segments": "views.segments_page",
    "campaigns": "views.campaigns_page",
    "predict": "views.simulator_page",
    "strategy": "views.recommendations_page",
}

module = importlib.import_module(PAGES[active_page])
module.render(customers)
