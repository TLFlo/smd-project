import streamlit as st

from components.cards import kpi_card, not_available_box, page_header
from components.charts import bar_chart
from components.tables import data_table
from utils.preprocessing import campaign_summary, enrich_customers


def render(customers):
    page_header("Performance des campagnes", "Taux d'acceptation et rentabilité estimée par campagne")

    df = enrich_customers(customers)
    camp = campaign_summary(df)

    if camp.empty:
        st.warning("Aucune colonne de campagne trouvée dans les données.")
        return

    total_contacted = camp["Contactés"].iloc[0]
    total_accept = camp["Acceptations"].sum()
    global_rate = camp["Taux d'acceptation"].mean()
    at_least_one = int((df[["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5", "Response"]].sum(axis=1) > 0).sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("CLIENTS CONTACTÉS", f"{total_contacted:,}")
    with c2:
        kpi_card("ACCEPTATIONS CUMULÉES", f"{total_accept:,}")
    with c3:
        kpi_card("TAUX D'ACCEPTATION MOYEN", f"{global_rate:.1f} %")
    with c4:
        kpi_card("CLIENTS AYANT RÉPONDU ≥1 FOIS", f"{at_least_one:,}")

    not_available_box(
        "ROI — Estimation illustrative",
        "Calculé à partir de <code>Z_CostContact</code> / <code>Z_Revenue</code>, des constantes fournies "
        "par le dataset (coût/revenu moyen supposé par contact). Ce n'est pas un revenu réellement attribué "
        "à chaque campagne — à présenter comme une approximation, pas un ROI mesuré.",
    )
    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("##### Taux d'acceptation par campagne")
            st.plotly_chart(bar_chart(camp, "Campagne", "Taux d'acceptation"), use_container_width=True, config={"displayModeBar": False})
    with col2:
        with st.container(border=True):
            st.markdown("##### ROI estimé par campagne")
            st.plotly_chart(bar_chart(camp, "Campagne", "ROI estimé"), use_container_width=True, config={"displayModeBar": False})

    st.write("")
    with st.container(border=True):
        st.markdown("##### Tableau de performance")
        sort_choice = st.selectbox("Trier par :", ["Acceptations", "Taux d'acceptation", "ROI estimé"])
        table = camp.sort_values(sort_choice, ascending=False)
        data_table(table, download_name="campagnes.csv")
