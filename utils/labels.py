"""
Dictionnaire central des libellés d'affichage.

Modifie ce fichier pour changer le nom affiché d'une colonne PARTOUT dans
l'app (tableaux ET graphiques : axes, légendes, infobulles) sans toucher au
code des pages. La clé est le nom technique (colonne du DataFrame), la
valeur est le texte affiché à l'utilisateur.

Toute colonne absente de ce dictionnaire s'affiche telle quelle (son nom
technique brut).
"""

DISPLAY_LABELS = {
    "Customer_ID": "Client",
    "Cluster": "Segment",
    "Age": "Âge",
    "Age_Group": "Tranche d'âge",
    "Income": "Revenu",
    "Total_Spent": "Dépense totale",
    "Total_Spending": "Dépense totale",
    "Total_Purchases": "Nombre d'achats",
    "Purchase_Frequency": "Fréquence d'achat",
    "Average_Basket": "Panier moyen",
    "Recency": "Récence (jours)",
    "NumWebVisitsMonth": "Visites web / mois",
    "Web_Share": "Part Web",
    "Catalog_Share": "Part Catalogue",
    "Store_Share": "Part Magasin",
    "Deal_Share": "Part Promotions",
    "Product_Category_Count": "Catégories achetées",
    "Education": "Éducation",
    "Marital_Status": "Statut marital",
    "Campaign": "Campagne",
    "Campagne": "Campagne",
    "Contactés": "Contactés",
    "Acceptations": "Acceptations",
    "Taux d'acceptation": "Taux d'acceptation (%)",
    "ROI estimé": "ROI estimé (%)",
    "PCA1": "Composante 1",
    "PCA2": "Composante 2",
}


def label(col: str) -> str:
    """Renvoie le libellé d'affichage d'une colonne, ou son nom brut si absent du dictionnaire."""
    return DISPLAY_LABELS.get(col, col)


def label_map(cols) -> dict:
    """Construit un mapping {col: libellé} pour plusieurs colonnes à la fois
    (pratique pour renommer un DataFrame ou passer à Plotly `labels=`)."""
    return {c: DISPLAY_LABELS.get(c, c) for c in cols}
