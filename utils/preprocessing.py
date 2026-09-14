"""
Variables dérivées — réplique exacte du feature engineering du notebook
`customer-personality-analysis.ipynb` fourni, pour que le dashboard soit
cohérent avec l'analyse de référence (mêmes formules, même segmentation K=2).

## Correction des anomalies (cf. notebook, cellule "Correction des anomalies")

- `Year_Birth` < 1940 → remplacé par la médiane.
- `Income` > 200 000 → remplacé par la médiane.

  ⚠️ Écart volontaire par rapport au notebook original : celui-ci exécute
  `df.loc[df["Income"] > 200000] = np.nan` (toute la LIGNE passe à NaN, pas
  seulement `Income`), ce qui semble être un bug involontaire — il efface
  aussi Year_Birth, Education, etc. pour ces clients. Ici, seule la colonne
  `Income` est corrigée, pour ne pas perdre le reste des informations client.

## Features de clustering (9 variables, identiques au notebook)

`Total_Spending, Purchase_Frequency, Web_Share, Catalog_Share, Store_Share,
Deal_Share, Recency, NumWebVisitsMonth, Product_Category_Count`

## Segmentation

K=2 (retenu dans le notebook après un balayage de K=2 à 10 par score de
silhouette), K-Means + StandardScaler.

## Churn (dashboard uniquement, absent du notebook de segmentation)

Le notebook fourni ne définit pas de churn : c'est un proxy ajouté pour les
besoins du dashboard, basé sur `Recency > RECENCE_CHURN_JOURS`.
"""

import numpy as np
import pandas as pd

RECENCE_CHURN_JOURS = 60

MNT_COLS = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts", "MntSweetProducts", "MntGoldProds"]
CHANNEL_COLS = ["NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases"]
CAMPAIGN_COLS = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5"]

AGE_BINS = [17, 25, 35, 45, 55, 65, 200]
AGE_LABELS = ["18-25", "26-35", "36-45", "46-55", "56-65", "66+"]

MNT_LABELS = {
    "MntWines": "Vins", "MntFruits": "Fruits", "MntMeatProducts": "Viande",
    "MntFishProducts": "Poisson", "MntSweetProducts": "Sucreries", "MntGoldProds": "Produits premium",
}
CHANNEL_LABELS = {
    "NumWebPurchases": "Web", "NumCatalogPurchases": "Catalogue",
    "NumStorePurchases": "Magasin", "NumDealsPurchases": "Achats promo",
}


def enrich_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Dt_Customer"] = pd.to_datetime(df["Dt_Customer"], dayfirst=True, errors="coerce")

    # --- Correction des anomalies (cf. docstring) ---
    df.loc[df["Year_Birth"] < 1940, "Year_Birth"] = np.nan
    df["Year_Birth"] = df["Year_Birth"].fillna(df["Year_Birth"].median())

    df.loc[df["Income"] > 200_000, "Income"] = np.nan
    df["Income"] = df["Income"].fillna(df["Income"].median())

    ref_year = int(df["Dt_Customer"].dt.year.max())
    df["Age"] = ref_year - df["Year_Birth"]
    df["Age_Group"] = pd.cut(df["Age"], bins=AGE_BINS, labels=AGE_LABELS)

    # --- Feature engineering identique au notebook ---
    df["Total_Spending"] = df[MNT_COLS].sum(axis=1)
    df["Purchase_Frequency"] = df[CHANNEL_COLS].sum(axis=1)

    total_purchases = df[CHANNEL_COLS].sum(axis=1)
    df["Web_Share"] = np.where(total_purchases > 0, df["NumWebPurchases"] / total_purchases, 0.0)
    df["Catalog_Share"] = np.where(total_purchases > 0, df["NumCatalogPurchases"] / total_purchases, 0.0)
    df["Store_Share"] = np.where(total_purchases > 0, df["NumStorePurchases"] / total_purchases, 0.0)
    df["Deal_Share"] = np.where(total_purchases > 0, df["NumDealsPurchases"] / total_purchases, 0.0)

    df["Product_Category_Count"] = (df[MNT_COLS] > 0).sum(axis=1)

    # --- Aliases pour compatibilité avec le reste du dashboard ---
    df["Total_Spent"] = df["Total_Spending"]
    df["Total_Purchases"] = df["Purchase_Frequency"]
    df["Average_Basket"] = np.where(df["Purchase_Frequency"] > 0, df["Total_Spending"] / df["Purchase_Frequency"], 0.0)

    df["Campaigns_Accepted"] = df[CAMPAIGN_COLS].sum(axis=1)
    df["Churn"] = (df["Recency"] > RECENCE_CHURN_JOURS).astype(int)
    df["Children"] = df["Kidhome"].fillna(0) + df["Teenhome"].fillna(0)

    return df


def campaign_summary(df: pd.DataFrame) -> pd.DataFrame:
    z_cost = float(df["Z_CostContact"].iloc[0]) if "Z_CostContact" in df else np.nan
    z_revenue = float(df["Z_Revenue"].iloc[0]) if "Z_Revenue" in df else np.nan

    labels = {
        "AcceptedCmp1": "Campagne 1", "AcceptedCmp2": "Campagne 2", "AcceptedCmp3": "Campagne 3",
        "AcceptedCmp4": "Campagne 4", "AcceptedCmp5": "Campagne 5", "Response": "Dernière campagne",
    }
    rows = []
    for col, label in labels.items():
        if col not in df.columns:
            continue
        contacted = len(df)
        accepted = int(df[col].sum())
        rate = accepted / contacted * 100 if contacted else 0.0
        cost = contacted * z_cost
        revenue = accepted * z_revenue
        roi = ((revenue - cost) / cost * 100) if cost else np.nan
        rows.append({
            "Campagne": label, "Contactés": contacted, "Acceptations": accepted,
            "Taux d'acceptation": rate, "Coût estimé": cost, "Revenu estimé": revenue, "ROI estimé": roi,
        })
    return pd.DataFrame(rows)


def spending_by_category(df: pd.DataFrame) -> pd.DataFrame:
    totals = df[MNT_COLS].sum().reset_index()
    totals.columns = ["Categorie", "Montant"]
    totals["Categorie"] = totals["Categorie"].map(MNT_LABELS)
    return totals.sort_values("Montant", ascending=False)


def purchases_by_channel(df: pd.DataFrame) -> pd.DataFrame:
    cols = CHANNEL_COLS + ["NumDealsPurchases"]
    totals = df[cols].sum().reset_index()
    totals.columns = ["Canal", "Achats"]
    totals["Canal"] = totals["Canal"].map(CHANNEL_LABELS)
    return totals.sort_values("Achats", ascending=False)
