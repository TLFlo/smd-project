"""
Entraîne et sauvegarde les modèles ML à partir de data/customers.csv.

    python train_models.py

Génère dans models/ :
    kmeans.pkl / scaler.pkl   -> segmentation (K=3)
    churn_model.pkl           -> proxy de churn (Recency > 60 jours)
    clv_model.pkl             -> régression sur Total_Spent

Hypothèses : voir utils/preprocessing.py.
"""

import os

import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from utils.ml import CHURN_FEATURES, CLUSTER_FEATURES, CLV_FEATURES
from utils.preprocessing import enrich_customers

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

N_CLUSTERS = 2  # retenu dans le notebook customer-personality-analysis.ipynb (balayage K=2..10, score de silhouette)


def main():
    path = os.path.join(DATA_DIR, "customers.csv")
    if not os.path.exists(path):
        raise SystemExit(f"Fichier manquant : {path}. Place-le dans data/ avant de relancer.")

    raw = pd.read_csv(path, sep=None, engine="python").rename(columns={"ID": "Customer_ID"})
    features = enrich_customers(raw)

    # --- K-Means + scaler ---
    X_cluster = features[CLUSTER_FEATURES].fillna(0)
    scaler = StandardScaler().fit(X_cluster)
    X_scaled = scaler.transform(X_cluster)
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10).fit(X_scaled)
    joblib.dump(kmeans, os.path.join(MODELS_DIR, "kmeans.pkl"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    print(f"K-Means (K={N_CLUSTERS}) et scaler sauvegardés.")

    # --- Churn ---
    if features["Churn"].nunique() < 2:
        print("⚠️  Une seule classe de churn présente : modèle NON entraîné "
              "(ajuste RECENCE_CHURN_JOURS dans utils/preprocessing.py).")
    else:
        X_churn, y_churn = features[CHURN_FEATURES], features["Churn"]
        X_train, X_test, y_train, y_test = train_test_split(
            X_churn, y_churn, test_size=0.2, random_state=42, stratify=y_churn
        )
        churn_model = RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced")
        churn_model.fit(X_train, y_train)
        print(f"Churn model — accuracy test : {churn_model.score(X_test, y_test):.2%}")
        joblib.dump(churn_model, os.path.join(MODELS_DIR, "churn_model.pkl"))

    # --- CLV (régression sur Total_Spent) ---
    X_clv, y_clv = features[CLV_FEATURES], features["Total_Spent"]
    Xc_train, Xc_test, yc_train, yc_test = train_test_split(X_clv, y_clv, test_size=0.2, random_state=42)
    clv_model = RandomForestRegressor(n_estimators=300, random_state=42)
    clv_model.fit(Xc_train, yc_train)
    print(f"CLV model — R² test : {clv_model.score(Xc_test, yc_test):.3f}")
    joblib.dump(clv_model, os.path.join(MODELS_DIR, "clv_model.pkl"))

    print(f"\nTous les modèles disponibles sont sauvegardés dans {MODELS_DIR}")


if __name__ == "__main__":
    main()
