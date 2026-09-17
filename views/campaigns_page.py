import streamlit as st

from components.cards import kpi_card, not_available_box, page_header
from components.charts import bar_chart
from components.tables import data_table
from utils.preprocessing import campaign_summary, enrich_customers


def render(customers):
    page_header(
        "Performance des campagnes",
        "Taux d'acceptation et rentabilité estimée par campagne"
    )

    df = enrich_customers(customers)
    camp = campaign_summary(df)

    if camp.empty:
        st.warning("Aucune colonne de campagne trouvée dans les données.")
        return

    # ----------------------------------------------------------
    # INDICATEURS GLOBAUX
    # ----------------------------------------------------------

    total_contacted = camp["Contactés"].iloc[0]
    total_accept = camp["Acceptations"].sum()

    # Taux global calculé sur l'ensemble des campagnes
    if total_contacted > 0:
        global_rate = (total_accept / total_contacted) * 100
    else:
        global_rate = 0

    campaign_columns = [
        "AcceptedCmp1",
        "AcceptedCmp2",
        "AcceptedCmp3",
        "AcceptedCmp4",
        "AcceptedCmp5",
        "Response"
    ]

    available_campaign_columns = [
        col for col in campaign_columns
        if col in df.columns
    ]

    if available_campaign_columns:
        at_least_one = int(
            (
                df[available_campaign_columns]
                .fillna(0)
                .sum(axis=1) > 0
            ).sum()
        )
    else:
        at_least_one = 0

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "CLIENTS CONTACTÉS",
            f"{total_contacted:,}"
        )

    with c2:
        kpi_card(
            "ACCEPTATIONS CUMULÉES",
            f"{total_accept:,}"
        )

    with c3:
        kpi_card(
            "TAUX DE RÉPONSE GLOBAL",
            f"{global_rate:.1f} %"
        )

    with c4:
        kpi_card(
            "CLIENTS AYANT RÉPONDU ≥1 FOIS",
            f"{at_least_one:,}"
        )

    # ----------------------------------------------------------
    # EXPLICATION DE LA RENTABILITÉ ESTIMÉE
    # ----------------------------------------------------------

    not_available_box(
        "Rentabilité estimée — à interpréter avec prudence",
        """
        Cette valeur représente une estimation basée sur un coût moyen de contact
        et un revenu moyen associé à une réponse.

        Le coût total estimé correspond au coût de contact appliqué au nombre
        de clients contactés.

        Le revenu total estimé correspond au revenu moyen appliqué au nombre
        de clients ayant répondu à la campagne.

        La rentabilité estimée correspond à la différence entre le revenu total
        estimé et le coût total estimé.

        Cette donnée ne permet pas de déterminer le revenu ou le bénéfice réel
        généré par chaque client ou par chaque campagne. Elle sert uniquement
        d'indicateur comparatif entre les campagnes.

        Le taux de réponse reste l'indicateur directement observable dans les données.
        """,
    )

    st.write("")

    # ----------------------------------------------------------
    # GRAPHIQUES
    # ----------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("##### Taux de réponse par campagne")

            fig_response = bar_chart(
                camp,
                "Campagne",
                "Taux d'acceptation"
            )

            fig_response.update_layout(
                xaxis_title="Campagne",
                yaxis_title="Taux de réponse (%)"
            )

            st.plotly_chart(
                fig_response,
                use_container_width=True,
                config={"displayModeBar": False}
            )

    with col2:
        with st.container(border=True):
            st.markdown("##### Rentabilité estimée par campagne")

            fig_roi = bar_chart(
                camp,
                "Campagne",
                "ROI estimé"
            )

            fig_roi.update_layout(
                xaxis_title="Campagne",
                yaxis_title="Rentabilité estimée"
            )

            st.plotly_chart(
                fig_roi,
                use_container_width=True,
                config={"displayModeBar": False}
            )

    st.write("")

    # ----------------------------------------------------------
    # TABLEAU
    # ----------------------------------------------------------

    with st.container(border=True):
        st.markdown("##### Tableau de performance")

        sort_choice = st.selectbox(
            "Trier par :",
            [
                "Acceptations",
                "Taux d'acceptation",
                "ROI estimé"
            ]
        )

        table = camp.sort_values(
            sort_choice,
            ascending=False
        )

        data_table(
            table,
            download_name="campagnes.csv"
        )