"""
Segmentation (K-Means + PCA) et chargement des modèles pré-entraînés.

Aucun faux clustering n'est présenté comme réel : si les artefacts requis
(modèle K-Means, scaler) sont absents, `load_kmeans_artifacts` renvoie None
et les pages appelantes doivent afficher clairement que la segmentation
n'est pas disponible.

## Format du modèle de churn

Le modèle de churn fourni n'est PAS du XGBoost : c'est un
GradientBoostingClassifier scikit-learn, exporté sous une forme portable
(sans dépendance sklearn/xgboost à l'inférence) en 2 fichiers :
  - models/churn_model.json    -> les arbres de décision + la valeur de base
  - models/churn_metadata.pkl  -> {'features': [...], 'scaler': None, ...}
    (scaler=None car absent du modèle source ; les modèles à base d'arbres
    n'en ont généralement pas besoin)

La fonction `_predict_tree_json` réimplémente la formule d'un
GradientBoostingClassifier binaire (loss='log_loss') :
    raw_score(x) = baseline + learning_rate * somme(arbre_i.predire(x))
    proba(x) = sigmoid(raw_score(x))
"""

import json
import math
import os
import pickle

import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

KMEANS_PATH = os.path.join(MODELS_DIR, "kmeans.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")
CHURN_MODEL_JSON_PATH = os.path.join(MODELS_DIR, "churn_model.json")
CHURN_METADATA_PATH = os.path.join(MODELS_DIR, "churn_metadata.pkl")
CLV_MODEL_PATH = os.path.join(MODELS_DIR, "clv_model.pkl")

CLUSTER_FEATURES = [
    "Total_Spending", "Purchase_Frequency", "Web_Share", "Catalog_Share",
    "Store_Share", "Deal_Share", "Recency", "NumWebVisitsMonth", "Product_Category_Count",
]
CHURN_FEATURES = ["Age", "Income", "Recency", "Total_Purchases", "Average_Basket", "NumWebVisitsMonth"]
CLV_FEATURES = ["Age", "Income", "Recency", "Total_Purchases", "Average_Basket", "NumWebVisitsMonth"]


def load_pickle(path):
    if os.path.exists(path):
        return joblib.load(path)
    return None


def load_artifact(path, default_features):
    """Charge un .pkl qui peut être :
      - un dictionnaire {'model': ..., 'scaler': ..., 'features': [...]}
        (format livré avec un scaler et une liste de colonnes explicite) ;
      - ou un objet modèle "brut" (ancien format, sans scaler dédié).

    Renvoie toujours un dict {'model', 'scaler', 'features'} ou None si le
    fichier n'existe pas.
    """
    obj = load_pickle(path)
    if obj is None:
        return None
    if isinstance(obj, dict) and "model" in obj:
        return {
            "model": obj.get("model"),
            "scaler": obj.get("scaler"),
            "features": obj.get("features") or default_features,
        }
    return {"model": obj, "scaler": None, "features": default_features}


def _predict_single_tree(tree: dict, x: list) -> float:
    """Parcourt un arbre exporté en JSON (feature/threshold/children_left/
    children_right/value) jusqu'à une feuille (feature == -2)."""
    node = 0
    feature, threshold = tree["feature"], tree["threshold"]
    left, right, value = tree["children_left"], tree["children_right"], tree["value"]
    while feature[node] != -2:
        node = left[node] if x[feature[node]] <= threshold[node] else right[node]
    return value[node]


def load_churn_artifact():
    """Charge le modèle de churn portable (churn_model.json + churn_metadata.pkl).
    Renvoie None si l'un des deux fichiers est absent — pas de fausse prédiction.
    """
    if not (os.path.exists(CHURN_MODEL_JSON_PATH) and os.path.exists(CHURN_METADATA_PATH)):
        return None

    with open(CHURN_MODEL_JSON_PATH, "r") as f:
        model_data = json.load(f)
    with open(CHURN_METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)

    return {
        "trees": model_data["trees"],
        "baseline": model_data["baseline_log_odds"],
        "learning_rate": model_data["learning_rate"],
        "features": metadata["features"],
        "scaler": metadata.get("scaler"),  # None pour ce modèle (pas de scaler source)
    }


def predict_churn_proba(artifact: dict, df_client: pd.DataFrame) -> float:
    """Probabilité de churn pour un client, à partir de l'artefact JSON+PKL."""
    features = artifact["features"]
    row = df_client.iloc[0]
    x = [row[f] for f in features]

    if artifact.get("scaler") is not None:
        x = artifact["scaler"].transform([x])[0]

    score = artifact["baseline"]
    for tree in artifact["trees"]:
        score += artifact["learning_rate"] * _predict_single_tree(tree, x)
    return 1.0 / (1.0 + math.exp(-score))


def predict_value(artifact: dict, df_client: pd.DataFrame) -> float:
    """Valeur prédite par un modèle de régression scikit-learn classique (ex: CLV)."""
    features = artifact["features"]
    X = df_client[features]
    if artifact["scaler"] is not None:
        X = artifact["scaler"].transform(X)
    return float(artifact["model"].predict(X)[0])


def load_kmeans_artifacts():
    """Renvoie (kmeans, scaler) ou (None, None) si non entraînés."""
    return load_pickle(KMEANS_PATH), load_pickle(SCALER_PATH)


def apply_segmentation(customer_features: pd.DataFrame):
    """Applique le K-Means pré-entraîné aux clients actuels.
    Renvoie (df_avec_cluster_et_pca, disponible: bool).
    """
    kmeans, scaler = load_kmeans_artifacts()
    if kmeans is None or scaler is None:
        return customer_features, False

    X = customer_features[CLUSTER_FEATURES].fillna(0)
    X_scaled = scaler.transform(X)

    df = customer_features.copy()
    df["Cluster"] = kmeans.predict(X_scaled).astype(str)

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X_scaled)
    df["PCA1"], df["PCA2"] = coords[:, 0], coords[:, 1]
    return df, True


def label_segment(avg_spent: float, low_thr: float, high_thr: float, cluster_id: str | None = None) -> tuple:
    """Attribue un nom + une couleur de pill à un cluster.

    ==========================================================================
    POUR RENOMMER LES SEGMENTS : modifie simplement CLUSTER_LABELS ci-dessus.
    Chaque clé est l'identifiant de cluster (celui que K-Means attribue, ex.
    "0", "1"), et la valeur est (nom_affiche, couleur, texte_du_pill).
    Couleurs possibles : "green", "orange", "red".
    ==========================================================================

    Si cluster_id est fourni ET présent dans CLUSTER_LABELS, ce libellé fixe
    est utilisé. Sinon (cluster non répertorié, ou K différent de 2), un nom
    générique est calculé relativement à la dépense moyenne des autres
    clusters (terciles).
    """
    if cluster_id is not None and cluster_id in CLUSTER_LABELS:
        return CLUSTER_LABELS[cluster_id]

    if avg_spent >= high_thr:
        return "Premium", "green", "Forte valeur"
    if avg_spent <= low_thr:
        return "À risque", "red", "Risque élevé"
    return "Régulier", "orange", "Valeur moyenne"
