"""
Chargement du dataset unique data/customers.csv.

Format attendu (une ligne = un client) :
    ID, Year_Birth, Education, Marital_Status, Income, Kidhome, Teenhome,
    Dt_Customer, Recency, MntWines, MntFruits, MntMeatProducts,
    MntFishProducts, MntSweetProducts, MntGoldProds, NumDealsPurchases,
    NumWebPurchases, NumCatalogPurchases, NumStorePurchases,
    NumWebVisitsMonth, AcceptedCmp1..5, Complain, Z_CostContact, Z_Revenue,
    Response

Le séparateur (virgule ou tabulation) est détecté automatiquement, car le
dataset source de référence est habituellement tabulé.

Aucune donnée n'est inventée : si le fichier ou une colonne manque,
l'application affiche une erreur explicite et s'arrête.
"""

import os

import pandas as pd
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.csv")

REQUIRED_COLUMNS = {
    "ID", "Year_Birth", "Education", "Marital_Status", "Income", "Kidhome", "Teenhome",
    "Dt_Customer", "Recency", "MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts",
    "MntSweetProducts", "MntGoldProds", "NumDealsPurchases", "NumWebPurchases",
    "NumCatalogPurchases", "NumStorePurchases", "NumWebVisitsMonth",
    "AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5",
    "Complain", "Z_CostContact", "Z_Revenue", "Response",
}


@st.cache_data
def load_customers() -> pd.DataFrame:
    if not os.path.exists(CUSTOMERS_FILE):
        st.error(f"Fichier manquant : `{CUSTOMERS_FILE}`.\n\nPlace **customers.csv** dans le dossier `data/`.")
        st.stop()

    # sep=None + engine="python" détecte automatiquement virgule / tabulation / point-virgule.
    df = pd.read_csv(CUSTOMERS_FILE, sep=None, engine="python")

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        st.error(f"Colonnes manquantes dans customers.csv : {missing}")
        st.stop()

    df = df.rename(columns={"ID": "Customer_ID"})
    return df


def load_all():
    return load_customers()
