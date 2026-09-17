import pandas as pd
import streamlit as st

from components.cards import not_available_box, page_header, pill
from utils.ml import apply_segmentation, label_segment
from utils.preprocessing import enrich_customers


def render(customers):
    page_header(
        "Recommandations marketing",
        "Passage de l'analyse à l'action personnalisée"
    )

    features = enrich_customers(customers)
    features, available = apply_segmentation(features)

    if not available:
        not_available_box(
            "Recommandations non disponibles",
            "Elles dépendent de la segmentation K-Means. "
            "Exécute <code>python train_models.py</code> d'abord.",
        )
        return

    # ------------------------------------------------------ STATISTIQUES --

    cluster_stats = (
        features
        .groupby("Cluster")
        .agg(
            Clients=("Customer_ID", "count"),
            Avg_Spent=("Total_Spent", "mean"),
            Avg_Recency=("Recency", "mean"),
            Avg_Purchases=("Total_Purchases", "mean"),
        )
        .reset_index()
    )

    low_thr = cluster_stats["Avg_Spent"].quantile(1 / 3)
    high_thr = cluster_stats["Avg_Spent"].quantile(2 / 3)

    # ------------------------------------------------ RECOMMANDATIONS --

    cols = st.columns(len(cluster_stats))

    rows_table = []

    for col, (_, row) in zip(
        cols,
        cluster_stats
        .sort_values("Avg_Spent", ascending=False)
        .iterrows()
    ):

        name, color, pill_text = label_segment(
            row["Avg_Spent"],
            low_thr,
            high_thr
        )

        cluster_id = row["Cluster"]

        # Clients du segment
        segment = features[
            features["Cluster"] == cluster_id
        ]

        # --------------------------------------------------
        # Analyse des campagnes
        # --------------------------------------------------

        campaign_columns = [
            "AcceptedCmp1",
            "AcceptedCmp2",
            "AcceptedCmp3",
            "AcceptedCmp4",
            "AcceptedCmp5",
            "Response",
        ]

        available_campaigns = [
            c for c in campaign_columns
            if c in segment.columns
        ]

        campaign_rates = {}

        for campaign in available_campaigns:
            campaign_rates[campaign] = segment[campaign].mean() * 100

        best_campaigns = sorted(
            campaign_rates.items(),
            key=lambda x: x[1],
            reverse=True
        )[:2]

        # --------------------------------------------------
        # Analyse des produits
        # --------------------------------------------------

        wine_interest = None

        if "MntWines" in segment.columns:
            wine_interest = segment["MntWines"].mean()

        # --------------------------------------------------
        # Analyse des canaux
        # --------------------------------------------------

        channel_values = {}

        if "NumWebPurchases" in segment.columns:
            channel_values["Site web"] = segment["NumWebPurchases"].mean()

        if "NumCatalogPurchases" in segment.columns:
            channel_values["Catalogue"] = segment["NumCatalogPurchases"].mean()

        if "NumStorePurchases" in segment.columns:
            channel_values["Magasin"] = segment["NumStorePurchases"].mean()

        if channel_values:
            main_channel = max(
                channel_values,
                key=channel_values.get
            )
        else:
            main_channel = "Canal non disponible"

        # --------------------------------------------------
        # RECOMMANDATION PAR SEGMENT
        # --------------------------------------------------

        if name == "Premium":

            canal = (
                f"{main_channel} + programme de fidélité"
            )

            if best_campaigns:
                campaigns_text = ", ".join(
                    [
                        campaign.replace("AcceptedCmp", "Campagne ")
                        for campaign, _ in best_campaigns
                    ]
                )
            else:
                campaigns_text = "les campagnes les mieux acceptées"

            contenu = (
                f"Proposer en priorité les offres liées aux "
                f"{campaigns_text}. "
                f"Privilégier également des offres autour du vin "
                f"et des avantages de fidélité."
            )

            objectif = (
                "Fidéliser les clients à forte valeur "
                "et augmenter leur fréquence d'achat."
            )

            signal = (
                f"Valeur moyenne élevée ; canal privilégié : "
                f"{main_channel}"
            )

            priority = "Haute"
            priority_color = "green"

        elif name == "Régulier":

            canal = (
                f"{main_channel} + recommandations personnalisées"
            )

            if best_campaigns:
                campaigns_text = ", ".join(
                    [
                        campaign.replace("AcceptedCmp", "Campagne ")
                        for campaign, _ in best_campaigns
                    ]
                )
            else:
                campaigns_text = "les campagnes les mieux acceptées"

            contenu = (
                f"Tester davantage les offres des {campaigns_text}, "
                f"avec une attention particulière aux produits liés "
                f"au vin. Utiliser principalement le {main_channel} "
                f"pour diffuser les offres."
            )

            objectif = (
                "Augmenter la fréquence d'achat et identifier "
                "les offres auxquelles le segment réagit le mieux."
            )

            signal = (
                f"Fréquence d'achat moyenne ; canal privilégié : "
                f"{main_channel}"
            )

            priority = "Moyenne"
            priority_color = "orange"

        else:

            canal = (
                f"{main_channel} + campagne de réactivation"
            )

            contenu = (
                "Proposer des offres ciblées et limitées dans le temps, "
                "en privilégiant les produits ayant déjà suscité "
                "de l'intérêt."
            )

            objectif = (
                "Réactiver les clients et réduire l'inactivité."
            )

            signal = (
                f"{row['Avg_Recency']:.0f} jours sans achat "
                "en moyenne"
            )

            priority = "Haute"
            priority_color = "red"

        # --------------------------------------------------
        # CARTE DU SEGMENT
        # --------------------------------------------------

        with col:
            with st.container(border=True):

                st.markdown(
                    f"##### Segment {name}"
                )

                st.markdown(
                    f"**Canal :** {canal}"
                )

                st.markdown(
                    f"**Contenu :** {contenu}"
                )

                st.markdown(
                    f"**Objectif :** {objectif}"
                )

                if best_campaigns:
                    st.markdown("**Campagnes à tester :**")

                    for campaign, rate in best_campaigns:
                        campaign_name = campaign.replace(
                            "AcceptedCmp",
                            "Campagne "
                        )

                        st.markdown(
                            f"- {campaign_name} : "
                            f"**{rate:.1f} % de réponse**"
                        )

                if wine_interest is not None:
                    st.markdown(
                        f"**Intérêt pour le vin :** "
                        f"{wine_interest:,.0f} $ de dépense moyenne"
                    )

        # --------------------------------------------------
        # TABLEAU DE SYNTHÈSE
        # --------------------------------------------------

        rows_table.append(
            {
                "Profil": f"Segment {name}",
                "Signal": signal,
                "Canal privilégié": main_channel,
                "Action recommandée": contenu,
                "Priorité": pill(
                    priority,
                    priority_color
                ),
            }
        )

    # ------------------------------------------------------ SYNTHÈSE --

    st.write("")

    with st.container(border=True):

        st.markdown(
            "##### Exemple de décision assistée par IA"
        )

        reco_df = pd.DataFrame(rows_table)

        st.markdown(
            reco_df.to_html(
                escape=False,
                index=False
            ),
            unsafe_allow_html=True
        )

        # st.markdown(
        #     "<div class='note' style='margin-top:10px;'>"
        #     "Les recommandations sont générées à partir des "
        #     "comportements observés dans chaque segment : "
        #     "réponse aux campagnes, habitudes d'achat, produits "
        #     "consommés et canaux utilisés."
        #     "</div>",
        #     unsafe_allow_html=True,
        # )

    # ------------------------------------------------------ SUIVI IA --

    st.write("")

    with st.container(border=True):

        st.markdown(
            "##### Suivi recommandé"
        )

        st.markdown(
            """
            <p>
            Les offres proposées peuvent être testées progressivement
            afin de mesurer la réaction de chaque segment.
            </p>

            <p>
            Un suivi des réponses aux campagnes, des produits achetés
            et des canaux utilisés permettrait d'identifier les périodes
            et les offres générant le plus d'engagement.
            </p>

            <p>
            Ces observations peuvent ensuite alimenter un système
            de recommandation capable d'adapter les offres et les
            canaux de communication aux comportements récents.
            </p>
            """,
            unsafe_allow_html=True,
        )