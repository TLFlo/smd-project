import streamlit as st

from components.cards import kpi_card, page_header
from components.charts import bar_chart, donut_chart, line_chart
from utils.metrics import fmt_k, global_kpis
from utils.preprocessing import AGE_LABELS, enrich_customers, purchases_by_channel, spending_by_category


def render(customers):
    page_header(
        "Vue globale",
        "Synthèse des performances commerciales et marketing",
        badge="Données actualisées",
    )

    df = enrich_customers(customers)

    # ---------------------------------------------------------- FILTRES --
    with st.expander("Filtres", expanded=False):
        f1, f2, f3 = st.columns(3)
        education_all = sorted(df["Education"].dropna().unique().tolist())
        marital_all = sorted(df["Marital_Status"].dropna().unique().tolist())

        education = f1.multiselect("Éducation", education_all, default=education_all, select_all=False)
        marital = f2.multiselect("Statut marital", marital_all, default=marital_all, select_all=False)
        age_groups = f3.multiselect("Tranche d'âge", AGE_LABELS, default=AGE_LABELS, select_all=False)

    filtered = df[
        df["Education"].isin(education)
        & df["Marital_Status"].isin(marital)
        & df["Age_Group"].astype(str).isin(age_groups)
    ]

    if filtered.empty:
        st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
        return

    # -------------------------------------------------------------- KPIs --
    kpis = global_kpis(filtered)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("CLIENTS", str(kpis["n_customers"]))
    with c2:
        kpi_card("CHIFFRE D'AFFAIRES", fmt_k(kpis["total_ca"]))
    with c3:
        kpi_card("DÉPENSE MOYENNE", fmt_k(kpis["avg_ca"]))
    with c4:
        kpi_card("TAUX DE RÉPONSE", f"{kpis['response_rate']:.1f} %")

    st.write("")

    # ---------------------------------------------------------- LIGNE 2 --
    col1, col2 = st.columns([1.45, 1])
    with col1:
        with st.container(border=True):
            st.markdown("##### Évolution des inscriptions clients")
            st.caption("Le dataset ne contient pas de date de vente individuelle : on utilise ici la date d'inscription (Dt_Customer).")
            inscriptions = filtered.groupby(filtered["Dt_Customer"].dt.to_period("M")).size().reset_index(name="Clients")
            inscriptions["Dt_Customer"] = inscriptions["Dt_Customer"].astype(str)
            st.plotly_chart(line_chart(inscriptions, "Dt_Customer", "Clients"), use_container_width=True, config={"displayModeBar": False})
    with col2:
        with st.container(border=True):
            st.markdown("##### Répartition par éducation")
            edu_dist = filtered.groupby("Education").size()
            st.plotly_chart(donut_chart(edu_dist.index, edu_dist.values), use_container_width=True, config={"displayModeBar": False})

    # ---------------------------------------------------------- LIGNE 3 --
    col3, col4, col5 = st.columns(3)
    with col3:
        with st.container(border=True):
            st.markdown("##### Dépenses par catégorie")
            st.plotly_chart(bar_chart(spending_by_category(filtered), "Categorie", "Montant"), use_container_width=True, config={"displayModeBar": False})
    with col4:
        with st.container(border=True):
            st.markdown("##### Canaux d'achat")
            st.plotly_chart(bar_chart(purchases_by_channel(filtered), "Canal", "Achats"), use_container_width=True, config={"displayModeBar": False})
    with col5:
        with st.container(border=True):
            st.markdown("##### Alertes")
            n_complaints = int(filtered["Complain"].sum())
            st.markdown(
                f"<p><b style='color:#A8452F'>{n_complaints}</b> client(s) ont déposé une réclamation "
                f"(<code>Complain</code>=1) sur la période filtrée.</p>",
                unsafe_allow_html=True,
            )
            n_at_risk = int((filtered["Recency"] > 60).sum())
            st.markdown(
                f"<p><b style='color:#A8452F'>{n_at_risk}</b> client(s) n'ont pas acheté depuis plus de 60 jours.</p>",
                unsafe_allow_html=True,
            )
            top_edu = filtered.groupby("Education")["Total_Spent"].mean().idxmax()
            st.markdown(
                f"<p><b style='color:#5B7F5E'>{top_edu}</b> est le niveau d'éducation avec la dépense moyenne la plus élevée.</p>",
                unsafe_allow_html=True,
            )
