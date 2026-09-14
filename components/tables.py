"""Tableau standardisé : affichage + téléchargement CSV."""

from __future__ import annotations

import streamlit as st

from utils.labels import label_map


def data_table(df, download_name: str, search_col: str | None = None, rename: dict | None = None):
    """rename : dict optionnel {"nom_colonne_reel": "Libelle Affiche"}.
    Si non fourni, utilise automatiquement utils/labels.py (DISPLAY_LABELS).
    N'affecte que l'affichage — le CSV téléchargé garde les vrais noms de colonnes.
    """
    if search_col and search_col in df.columns:
        query = st.text_input(f"🔎 Rechercher ({search_col})", key=f"search_{download_name}")
        if query:
            df = df[df[search_col].astype(str).str.contains(query, case=False, na=False)]

    effective_rename = rename if rename is not None else label_map(df.columns)
    display_df = df.rename(columns=effective_rename)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Télécharger (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=download_name,
        mime="text/csv",
        key=f"dl_{download_name}",
    )
