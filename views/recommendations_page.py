import pandas as pd
import streamlit as st

from components.cards import not_available_box, page_header, pill
from components.tables import data_table
from utils.ml import apply_segmentation, label_segment
from utils.preprocessing import enrich_customers

RECO_BY_LABEL = {
    "Premium": {"canal": "Email + programme de fidélité", "contenu": "Offres exclusives, avant-premières", "objectif": "Augmenter la CLV"},
    "Régulier": {"canal": "Réseaux sociaux", "contenu": "Recommandations produits personnalisées", "objectif": "Augmenter la fréquence d'achat"},
    "À risque": {"canal": "Email / SMS", "contenu": "Offre de réactivation ciblée", "objectif": "Réduire le taux de churn"},
}


def render(customers):
    page_header("Recommandations marketing", "Passage de l'analyse à l'action personnalisée")

    features = enrich_customers(customers)
    features, available = apply_segmentation(features)

    if not available:
        not_available_box(
            "Recommandations non disponibles",
            "Elles dépendent de la segmentation K-Means. Exécute <code>python train_models.py</code> d'abord.",
        )
        return

    cluster_stats = features.groupby("Cluster").agg(
        Clients=("Customer_ID", "count"),
        Avg_Spent=("Total_Spent", "mean"),
        Avg_Recency=("Recency", "mean"),
        Avg_Purchases=("Total_Purchases", "mean"),
    ).reset_index()
    low_thr = cluster_stats["Avg_Spent"].quantile(1 / 3)
    high_thr = cluster_stats["Avg_Spent"].quantile(2 / 3)

    cols = st.columns(len(cluster_stats))
    rows_table = []
    for col, (_, row) in zip(cols, cluster_stats.sort_values("Avg_Spent", ascending=False).iterrows()):
        name, color, pill_text = label_segment(row["Avg_Spent"], low_thr, high_thr)
        reco = RECO_BY_LABEL[name]
        with col:
            with st.container(border=True):
                st.markdown(f"##### Segment {row['Cluster']} — {name}")
                st.markdown(f"**Canal :** {reco['canal']}")
                st.markdown(f"**Contenu :** {reco['contenu']}")
                st.markdown(f"**Objectif :** {reco['objectif']}")

        priority = "Haute" if name in ("Premium", "À risque") else "Moyenne"
        priority_color = "green" if name == "Premium" else ("red" if name == "À risque" else "orange")
        signal = f"{row['Avg_Recency']:.0f} j sans achat en moyenne" if name == "À risque" else (
            "Forte valeur cumulée" if name == "Premium" else "Fréquence d'achat moyenne"
        )
        rows_table.append({
            "Profil": f"Segment {row['Cluster']} — {name}",
            "Signal": signal,
            "Action recommandée": reco["contenu"],
            "Priorité": pill(priority, priority_color),
        })

    st.write("")
    with st.container(border=True):
        st.markdown("##### Exemple de décision assistée par IA")
        reco_df = pd.DataFrame(rows_table)
        st.markdown(reco_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        st.markdown(
            "<div class='note' style='margin-top:10px;'>Générées à partir des caractéristiques "
            "réellement observées des segments (dépense moyenne, récence, fréquence d'achat).</div>",
            unsafe_allow_html=True,
        )
