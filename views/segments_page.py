import os

import streamlit as st

from components.cards import ivory_metric_row, not_available_box, page_header, pill, segment_card
from components.charts import scatter_chart
from components.tables import data_table
from utils.ml import apply_segmentation, label_segment
from utils.preprocessing import enrich_customers


ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets",
    "personas"
)


def render(customers):
    page_header(
        "Explorateur de segment de clientèle",
        "Analyse des profils issus de la segmentation client"
    )

    features = enrich_customers(customers)
    features, available = apply_segmentation(features)

    if not available:
        not_available_box(
            "Segmentation non disponible",
            "Le modèle K-Means doit être entraîné avant d'afficher les clusters réels. "
            "Exécute <code>python train_models.py</code> à la racine du projet.",
        )
        return

    # ---------------------------------------------------------- FILTRES --

    age_range = st.slider(
        "Filtrer par âge",
        int(features["Age"].min()),
        int(features["Age"].max()),
        (
            int(features["Age"].min()),
            int(features["Age"].max())
        ),
    )

    filtered = features[
        (features["Age"] >= age_range[0]) &
        (features["Age"] <= age_range[1])
    ]

    if filtered.empty:
        st.warning("Aucun client ne correspond à ce filtre d'âge.")
        return

    # -------------------------------------------------- CARTES DE SEGMENTS --

    cluster_stats = (
        filtered.groupby("Cluster")
        .agg(
            Clients=("Customer_ID", "count"),
            Avg_Spent=("Total_Spent", "mean")
        )
        .reset_index()
    )

    low_thr = cluster_stats["Avg_Spent"].quantile(1 / 3)
    high_thr = cluster_stats["Avg_Spent"].quantile(2 / 3)

    cols = st.columns(len(cluster_stats))

    for col, (_, row) in zip(
        cols,
        cluster_stats.sort_values(
            "Avg_Spent",
            ascending=False
        ).iterrows()
    ):
        name, color, pill_text = label_segment(
            row["Avg_Spent"],
            low_thr,
            high_thr
        )

        with col:
            segment_card(
                f"Segment {row['Cluster']} — {name}",
                f"{int(row['Clients']):,}",
                "clients",
                pill_text,
                color
            )

    st.write("")

    # ----------------------------------------------------------- PROFIL --

    with st.container(border=True):

        cluster_choice = st.selectbox(
            "Segment de clientèle",
            sorted(filtered["Cluster"].unique())
        )

        seg = filtered[
            filtered["Cluster"] == cluster_choice
        ]

        name, color, pill_text = label_segment(
            seg["Total_Spent"].mean(),
            low_thr,
            high_thr
        )

        st.markdown(
            f"##### Profil : Segment {cluster_choice} — {name} "
            f"{pill(pill_text, color)}",
            unsafe_allow_html=True
        )

        # ------------------------------------------------------ INDICATEURS --

        ivory_metric_row([
            ("Clients", f"{len(seg):,} clients"),
            ("Âge moyen", f"{seg['Age'].mean():.0f} ans"),
            ("Revenu moyen", f"{seg['Income'].mean():,.0f} $"),
            ("Dépense moyenne", f"{seg['Total_Spent'].mean():,.0f} $"),
            ("Achats moyens", f"{seg['Total_Purchases'].mean():.1f}"),
        ])

        st.write("")

        # ------------------------------------------------ DÉMOGRAPHIE --

        st.markdown("###### Informations démographiques")

        demo_cols = st.columns(3)

        # Âge
        with demo_cols[0]:
            st.markdown("**Âge**")
            st.write(
                f"Âge moyen : **{seg['Age'].mean():.0f} ans**"
            )

            st.write(
                f"Tranche d'âge : **{seg['Age'].min():.0f} – "
                f"{seg['Age'].max():.0f} ans**"
            )

        # Éducation
        with demo_cols[1]:
            st.markdown("**Éducation**")

            if "Education" in seg.columns:
                education = (
                    seg["Education"]
                    .value_counts()
                    .head(3)
                )

                for value, count in education.items():
                    percentage = count / len(seg) * 100
                    st.write(
                        f"{value} : **{percentage:.1f} %**"
                    )
            else:
                st.write("Information non disponible")

        # Situation familiale
        with demo_cols[2]:
            st.markdown("**Situation familiale**")

            if "Marital_Status" in seg.columns:
                marital = (
                    seg["Marital_Status"]
                    .value_counts()
                    .head(3)
                )

                for value, count in marital.items():
                    percentage = count / len(seg) * 100
                    st.write(
                        f"{value} : **{percentage:.1f} %**"
                    )
            else:
                st.write("Information non disponible")

        st.write("")

        # --------------------------------------------------------- TABLEAU --

        show_table = st.checkbox(
            "Afficher le détail des clients",
            value=False
        )

        if show_table:
            data_table(
                seg[
                    [
                        "Customer_ID",
                        "Age",
                        "Income",
                        "Total_Spent",
                        "Total_Purchases",
                        "Average_Basket",
                        "Recency"
                    ]
                ],
                download_name=f"segment_{cluster_choice}.csv",
            )

        # --------------------------------------------------------- PERSONA --

        persona_path = os.path.join(
            ASSETS_DIR,
            f"persona_segment_{cluster_choice}.png"
        )

        if os.path.exists(persona_path):
            st.write("")
            st.markdown(
                "###### Fiche persona "
                "(générée depuis l'analyse de référence)"
            )

            st.image(
                persona_path,
                use_container_width=True
            )

    st.write("")

    # -------------------------------------------------------------- PCA --