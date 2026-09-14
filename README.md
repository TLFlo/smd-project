# MarketIQ — Marketing Intelligence Dashboard

Dashboard Streamlit branché sur un **dataset client unique** (format
"Customer Personality Analysis") : une ligne par client, avec démographie,
dépenses par catégorie, canaux d'achat et historique de réponse aux
campagnes marketing.

## 1. Installation

```bash
cd marketing_iq
python -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Données

Place **un seul fichier** dans `data/customers.csv` (virgule ou tabulation,
détecté automatiquement), avec ces colonnes :

```text
ID, Year_Birth, Education, Marital_Status, Income, Kidhome, Teenhome,
Dt_Customer, Recency, MntWines, MntFruits, MntMeatProducts, MntFishProducts,
MntSweetProducts, MntGoldProds, NumDealsPurchases, NumWebPurchases,
NumCatalogPurchases, NumStorePurchases, NumWebVisitsMonth,
AcceptedCmp1, AcceptedCmp2, AcceptedCmp3, AcceptedCmp4, AcceptedCmp5,
Complain, Z_CostContact, Z_Revenue, Response
```

Si le fichier ou une colonne manque, l'app affiche une erreur et s'arrête —
aucune donnée n'est inventée.

### Hypothèses documentées (voir `utils/preprocessing.py`)

| Variable dérivée | Calcul | Pourquoi |
|---|---|---|
| `Age` | année la plus récente de `Dt_Customer` − `Year_Birth` | reproductible sans dépendre de la date du jour |
| `Total_Spent` | somme des 6 colonnes `Mnt*` | dépense cumulée, tous produits |
| `Total_Purchases` | `NumWebPurchases + NumCatalogPurchases + NumStorePurchases` | `NumDealsPurchases` exclu pour éviter un double comptage (achats promo déjà comptés dans un canal) |
| `Average_Basket` | `Total_Spent / Total_Purchases` | — |
| `Churn` (proxy) | 1 si `Recency > 60` jours | `Recency` est une colonne native, pas un vrai churn confirmé — seuil ajustable via `RECENCE_CHURN_JOURS` |
| `Income` manquant | rempli par la médiane | quelques valeurs manquantes dans ce type de dataset |
| ROI campagnes | à partir de `Z_CostContact` / `Z_Revenue` (constantes fournies par le dataset) | approximation illustrative, pas un revenu réellement attribué — affiché comme telle dans l'app |

## 3. Entraîner les modèles ML

```bash
python train_models.py
```

Génère dans `models/` :
- `kmeans.pkl` + `scaler.pkl` — segmentation (K=3 : Premium / Régulier / À risque)
- `churn_model.pkl` — Random Forest sur le proxy de churn
- `clv_model.pkl` — Random Forest, régression sur `Total_Spent`

Tant que ces fichiers n'existent pas, les pages concernées l'affichent
clairement au lieu d'inventer un résultat.

### Utiliser ton propre modèle de churn (ex. XGBoost déjà entraîné)

Le simulateur accepte un fichier `models/churn_model.pkl` sous deux formats :
- un dictionnaire `{'model': ..., 'scaler': ..., 'features': [...]}` (recommandé —
  le formulaire se génère **automatiquement** à partir de la liste `features`,
  quel que soit leur nombre ou leur nom) ;
- ou un modèle "brut" (fallback sur les features par défaut de `utils/ml.py`).

## 4. Lancer l'application

```bash
streamlit run app.py
```

## 5. Structure

```text
marketing_iq/
├── app.py                    # CSS global, sidebar, routage
├── train_models.py
├── requirements.txt
│
├── views/                    # Modules de pages (fonction render())
│   ├── global_page.py          → Vue globale
│   ├── segments_page.py        → Segments clients
│   ├── campaigns_page.py       → Campagnes
│   ├── simulator_page.py       → Simulateur ML
│   └── recommendations_page.py → Recommandations
│
├── components/                # Sidebar, cartes, graphiques, tableaux, CSS
├── utils/
│   ├── data_loader.py           # Chargement + validation de customers.csv
│   ├── preprocessing.py          # Variables dérivées, hypothèses documentées
│   ├── metrics.py                 # KPIs
│   └── ml.py                       # Clustering + chargement générique de modèles
│
├── models/   # kmeans.pkl, scaler.pkl, churn_model.pkl, clv_model.pkl
└── data/     # customers.csv
```

> Note technique : le dossier de pages s'appelle `views/` et non `pages/`,
> pour éviter que Streamlit n'ajoute automatiquement sa propre navigation
> par-dessus la sidebar personnalisée (navy, boutons actifs stylés).

## 6. Fonctionnement des pages

- **Vue globale** : KPIs (clients, CA, dépense moyenne, taux de réponse),
  évolution des inscriptions clients (pas de date de vente individuelle dans
  ce dataset, donc `Dt_Customer` est utilisé comme proxy — mentionné dans
  l'app), répartition par éducation, dépenses par catégorie de produit,
  canaux d'achat, alertes calculées en direct.
- **Segments clients** : K-Means (Age, Income, Total_Spent, Total_Purchases,
  Average_Basket, Recency), cartes Premium/Régulier/À risque nommées selon
  la dépense moyenne réelle, profil détaillé, projection PCA.
- **Campagnes** : taux d'acceptation par campagne (`AcceptedCmp1..5` +
  `Response`), ROI **explicitement marqué comme estimation illustrative**
  (basée sur `Z_CostContact`/`Z_Revenue`, pas un revenu réellement mesuré).
- **Simulateur ML** : formulaire généré dynamiquement à partir des features
  du modèle chargé, prédiction de churn + CLV, recommandation associée.
- **Recommandations** : une carte par segment réel + tableau de décisions
  générées à partir des caractéristiques observées.

## 9. Alignement sur le notebook `customer-personality-analysis.ipynb`

La segmentation du dashboard reproduit la méthodologie du notebook fourni
(validé : mêmes tailles de segments, mêmes dépenses moyennes) :

- **9 features de clustering** : `Total_Spending, Purchase_Frequency,
  Web_Share, Catalog_Share, Store_Share, Deal_Share, Recency,
  NumWebVisitsMonth, Product_Category_Count`
- **K=2** (retenu dans le notebook après balayage K=2..10 par score de
  silhouette) — Segment 0 = forte valeur, Segment 1 = valeur plus faible /
  sensible aux promotions.
- Les vraies fiches persona générées par le notebook (`assets/personas/`)
  s'affichent automatiquement dans la page Segments pour le cluster
  correspondant.

⚠️ **Écart volontaire** par rapport au notebook original sur la correction
des anomalies `Income` : le notebook exécute `df.loc[df["Income"] >
200000] = np.nan`, ce qui met TOUTE la ligne à NaN (probable bug), pas
seulement `Income`. Le dashboard corrige uniquement la colonne `Income`,
pour ne pas perdre les autres informations de ces clients.
