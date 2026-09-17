import pandas as pd
import streamlit as st

from components.cards import not_available_box, page_header, result_box
from utils.ml import (
    CLV_FEATURES,
    CLV_MODEL_PATH,
    load_artifact,
    load_churn_artifact,
    predict_churn_proba,
    predict_value,
)


# ============================================================
# NOMS LISIBLES DES VARIABLES
# ============================================================

FEATURE_LABELS = {
    # Profil client
    "Age": "Âge",
    "Income": "Revenu annuel",

    "Gender_Encoded": "Genre",
    "Is_Online_Shopper": "Achète principalement en ligne",

    # Achats
    "Total_Spent": "Dépenses totales",
    "Frequency": "Nombre total d'achats",
    "Avg_Basket": "Montant moyen par achat",
    "Total_Quantity": "Articles achetés",

    "Tenure_Days": "Ancienneté",
    "Customer_Span_Days": "Durée de la relation",

    "Purchase_Rate": "Rythme d'achat",
    "Avg_Item_Price": "Prix moyen des articles",

    "Unique_Products": "Produits différents",
    "Product Count": "Produits différents",

    "Monetary_Velocity": "Dépense moyenne",
    "Basket_Depth": "Articles par achat",

    # Comportement digital
    "NumWebVisitsMonth": "Visites du site par mois",
    "NumWebPurchases": "Achats en ligne",
    "NumCatalogPurchases": "Achats par catalogue",
    "NumStorePurchases": "Achats en magasin",

    # Parts / proportions
    "Catalog Share": "Part des achats par catalogue",
    "Deal Share": "Part des achats promotionnels",
    "Web Share": "Part des achats en ligne",
    "Store Share": "Part des achats en magasin",

    # Promotions
    "NumDealsPurchases": "Achats promotionnels",
}


# ============================================================
# EXPLICATION DES VARIABLES
# ============================================================

FEATURE_HELP = {
    "Age": "Âge du client en années.",
    "Income": "Revenu annuel estimé du client.",
    "Total_Spent": "Montant total dépensé par le client.",
    "Frequency": "Nombre total d'achats effectués.",
    "Avg_Basket": "Montant moyen dépensé à chaque achat.",
    "Total_Quantity": "Nombre total d'articles achetés.",
    "Tenure_Days": "Nombre de jours depuis l'inscription du client.",
    "Customer_Span_Days": "Durée entre le premier et le dernier achat.",
    "Purchase_Rate": "Rythme auquel le client effectue ses achats.",
    "Avg_Item_Price": "Prix moyen des articles achetés.",
    "Unique_Products": "Nombre de produits différents achetés.",
    "Product Count": "Nombre de produits différents achetés.",
    "Monetary_Velocity": "Montant dépensé rapporté à la période d'activité.",
    "Basket_Depth": "Nombre moyen d'articles dans un achat.",
    "NumWebVisitsMonth": "Nombre moyen de visites du site chaque mois.",
    "NumWebPurchases": "Nombre d'achats réalisés sur le site.",
    "NumCatalogPurchases": "Nombre d'achats réalisés via le catalogue.",
    "NumStorePurchases": "Nombre d'achats réalisés en magasin.",
    "Catalog Share": "Proportion des achats réalisés via catalogue.",
    "Deal Share": "Proportion des achats réalisés avec une promotion.",
    "Web Share": "Proportion des achats réalisés en ligne.",
    "Store Share": "Proportion des achats réalisés en magasin.",
    "NumDealsPurchases": "Nombre d'achats réalisés avec une promotion.",
    "Gender_Encoded": "Genre du client.",
    "Is_Online_Shopper": "Indique si le client achète principalement en ligne.",
}


# ============================================================
# CONFIGURATION DES VARIABLES
# ============================================================

def get_feature_config(feature):

    # --------------------------------------------------------
    # VARIABLES ENTIÈRES
    # --------------------------------------------------------

    integer_features = {
        "Age": {
            "min": 18,
            "max": 100,
            "default": 30,
            "step": 1,
        },

        "Frequency": {
            "min": 0,
            "max": 10000,
            "default": 0,
            "step": 1,
        },

        "Total_Quantity": {
            "min": 0,
            "max": 100000,
            "default": 0,
            "step": 1,
        },

        "Tenure_Days": {
            "min": 0,
            "max": 10000,
            "default": 0,
            "step": 1,
        },

        "Customer_Span_Days": {
            "min": 0,
            "max": 10000,
            "default": 0,
            "step": 1,
        },

        "Unique_Products": {
            "min": 0,
            "max": 10000,
            "default": 0,
            "step": 1,
        },

        "Product Count": {
            "min": 0,
            "max": 10000,
            "default": 0,
            "step": 1,
        },

        "NumWebVisitsMonth": {
            "min": 0,
            "max": 10000,
            "default": 0,
            "step": 1,
        },

        "NumWebPurchases": {
            "min": 0,
            "max": 10000,
            "default": 0,
            "step": 1,
        },

        "NumCatalogPurchases": {
            "min": 0,
            "max": 10000,
            "default": 0,
            "step": 1,
        },

        "NumStorePurchases": {
            "min": 0,
            "max": 10000,
            "default": 0,
            "step": 1,
        },

        "NumDealsPurchases": {
            "min": 0,
            "max": 10000,
            "default": 0,
            "step": 1,
        },
    }

    if feature in integer_features:
        return {
            "type": "int",
            **integer_features[feature],
        }

    # --------------------------------------------------------
    # VARIABLES DÉCIMALES
    # --------------------------------------------------------

    decimal_features = {
        "Income": {
            "min": 0.0,
            "max": 10_000_000.0,
            "default": 0.0,
            "step": 100.0,
        },

        "Total_Spent": {
            "min": 0.0,
            "max": 10_000_000.0,
            "default": 0.0,
            "step": 100.0,
        },

        "Avg_Basket": {
            "min": 0.0,
            "max": 1_000_000.0,
            "default": 0.0,
            "step": 100.0,
        },

        "Purchase_Rate": {
            "min": 0.0,
            "max": 1000.0,
            "default": 0.0,
            "step": 0.01,
        },

        "Avg_Item_Price": {
            "min": 0.0,
            "max": 1_000_000.0,
            "default": 0.0,
            "step": 100.0,
        },

        "Monetary_Velocity": {
            "min": 0.0,
            "max": 1_000_000.0,
            "default": 0.0,
            "step": 100.0,
        },

        "Basket_Depth": {
            "min": 0.0,
            "max": 1000.0,
            "default": 0.0,
            "step": 0.1,
        },

        "Catalog Share": {
            "min": 0.0,
            "max": 1.0,
            "default": 0.0,
            "step": 0.01,
        },

        "Deal Share": {
            "min": 0.0,
            "max": 1.0,
            "default": 0.0,
            "step": 0.01,
        },

        "Web Share": {
            "min": 0.0,
            "max": 1.0,
            "default": 0.0,
            "step": 0.01,
        },

        "Store Share": {
            "min": 0.0,
            "max": 1.0,
            "default": 0.0,
            "step": 0.01,
        },
    }

    if feature in decimal_features:
        return {
            "type": "float",
            **decimal_features[feature],
        }

    # --------------------------------------------------------
    # VARIABLES CATÉGORIELLES
    # --------------------------------------------------------

    if feature == "Gender_Encoded":
        return {
            "type": "select",
            "options": {
                "Homme": 0,
                "Femme": 1,
            },
            "default": "Homme",
        }

    if feature == "Is_Online_Shopper":
        return {
            "type": "select",
            "options": {
                "Non": 0,
                "Oui": 1,
            },
            "default": "Non",
        }

    # --------------------------------------------------------
    # PAR DÉFAUT
    # --------------------------------------------------------

    return {
        "type": "float",
        "min": 0.0,
        "max": 1_000_000.0,
        "default": 0.0,
        "step": 1.0,
    }


# ============================================================
# AFFICHAGE D'UN CHAMP
# ============================================================

def render_feature_input(feature, key_suffix=""):

    label = FEATURE_LABELS.get(
        feature,
        feature.replace("_", " "),
    )

    help_text = FEATURE_HELP.get(
        feature,
        "Information utilisée par le modèle prédictif.",
    )

    config = get_feature_config(feature)

    field_key = f"simulator_{feature}_{key_suffix}"

    # --------------------------------------------------------
    # ENTIER
    # --------------------------------------------------------

    if config["type"] == "int":
        return st.number_input(
            label,
            min_value=config["min"],
            max_value=config["max"],
            value=config["default"],
            step=config["step"],
            format="%d",
            help=help_text,
            key=field_key,
        )

    # --------------------------------------------------------
    # DÉCIMAL
    # --------------------------------------------------------

    if config["type"] == "float":

        # Les variables "Share" sont affichées en %
        if "Share" in feature:

            value = st.number_input(
                label,
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=1.0,
                format="%.0f",
                help=(
                    help_text
                    + " Saisissez une valeur entre 0 et 100 %."
                ),
                key=field_key,
            )

            # Conversion de 0-100 vers 0-1
            return value / 100

        return st.number_input(
            label,
            min_value=config["min"],
            max_value=config["max"],
            value=config["default"],
            step=config["step"],
            help=help_text,
            key=field_key,
        )

    # --------------------------------------------------------
    # CHOIX
    # --------------------------------------------------------

    if config["type"] == "select":

        options = config["options"]

        selected_label = st.selectbox(
            label,
            list(options.keys()),
            index=list(options.keys()).index(
                config["default"]
            ),
            help=help_text,
            key=field_key,
        )

        return options[selected_label]

    return 0.0


# ============================================================
# VALIDATION
# ============================================================

def validate_inputs(input_values):

    errors = []

    # --------------------------------------------------------
    # ÂGE
    # --------------------------------------------------------

    if "Age" in input_values:

        age = input_values["Age"]

        if not isinstance(age, int):

            errors.append(
                "L'âge doit être un nombre entier."
            )

        elif age < 18 or age > 100:

            errors.append(
                "L'âge doit être compris entre 18 et 100 ans."
            )

    # --------------------------------------------------------
    # VARIABLES ENTIÈRES
    # --------------------------------------------------------

    integer_features = [
        "Frequency",
        "Total_Quantity",
        "Tenure_Days",
        "Customer_Span_Days",
        "Unique_Products",
        "Product Count",
        "NumWebVisitsMonth",
        "NumWebPurchases",
        "NumCatalogPurchases",
        "NumStorePurchases",
        "NumDealsPurchases",
    ]

    for feature in integer_features:

        if feature not in input_values:
            continue

        value = input_values[feature]

        if value < 0:

            label = FEATURE_LABELS.get(
                feature,
                feature,
            )

            errors.append(
                f"{label} ne peut pas être négatif."
            )

    # --------------------------------------------------------
    # VARIABLES DÉCIMALES
    # --------------------------------------------------------

    decimal_features = [
        "Income",
        "Total_Spent",
        "Avg_Basket",
        "Purchase_Rate",
        "Avg_Item_Price",
        "Monetary_Velocity",
        "Basket_Depth",
    ]

    for feature in decimal_features:

        if feature not in input_values:
            continue

        value = input_values[feature]

        if value < 0:

            label = FEATURE_LABELS.get(
                feature,
                feature,
            )

            errors.append(
                f"{label} ne peut pas être négatif."
            )

    # --------------------------------------------------------
    # PARTS / POURCENTAGES
    # --------------------------------------------------------

    share_features = [
        "Catalog Share",
        "Deal Share",
        "Web Share",
        "Store Share",
    ]

    for feature in share_features:

        if feature not in input_values:
            continue

        value = input_values[feature]

        if value < 0 or value > 1:

            label = FEATURE_LABELS.get(
                feature,
                feature,
            )

            errors.append(
                f"{label} doit être comprise entre 0 % et 100 %."
            )

    return errors


# ============================================================
# AFFICHAGE DU SIMULATEUR
# ============================================================

def render(customers):

    page_header(
        "Estimez le risque de départ d'un client.",
        "Analyse basée sur le profil et le comportement d'achat",
    )

    # ========================================================
    # CHARGEMENT DES MODÈLES
    # ========================================================

    churn_artifact = load_churn_artifact()

    clv_artifact = load_artifact(
        CLV_MODEL_PATH,
        default_features=CLV_FEATURES,
    )

    if churn_artifact is None:

        not_available_box(
            "Modèle de risque non chargé",
            "Le simulateur nécessite churn_model.json et "
            "churn_metadata.pkl dans le dossier models/.",
        )

        return

    churn_features = churn_artifact["features"]

    # ========================================================
    # FORMULAIRE
    # ========================================================

    with st.form("simulateur"):

        input_values = {}

        # Séparation des variables en deux colonnes
        left_features = churn_features[::2]
        right_features = churn_features[1::2]

        col_left, col_right = st.columns(
            2,
            gap="large",
        )

        # ====================================================
        # GAUCHE
        # ====================================================

        with col_left:

            for feature in left_features:

                input_values[feature] = render_feature_input(
                    feature,
                    "left",
                )

        # ====================================================
        # DROITE
        # ====================================================

        with col_right:

            for feature in right_features:

                input_values[feature] = render_feature_input(
                    feature,
                    "right",
                )

        st.markdown("")

        submitted = st.form_submit_button(
            "Analyser le risque",
            type="primary",
            use_container_width=True,
        )

    # ========================================================
    # PRÉDICTION
    # ========================================================

    if submitted:

        errors = validate_inputs(input_values)

        if errors:

            st.error(
                "Certaines informations doivent être corrigées."
            )

            for error in errors:
                st.markdown(
                    f"- {error}"
                )

            return

        # ----------------------------------------------------
        # Création de la ligne dans l'ordre attendu
        # ----------------------------------------------------

        input_row = pd.DataFrame(
            [
                {
                    feature: input_values.get(
                        feature,
                        0.0,
                    )
                    for feature in churn_features
                }
            ]
        )

        # ====================================================
        # PRÉDICTION DU RISQUE
        # ====================================================

        try:

            proba = (
                predict_churn_proba(
                    churn_artifact,
                    input_row,
                )
                * 100
            )

            proba = max(
                0.0,
                min(
                    100.0,
                    float(proba),
                ),
            )

        except Exception as e:

            st.error(
                "Une erreur est survenue pendant l'analyse."
            )

            st.caption(
                f"Détail technique : {str(e)}"
            )

            return

        # ====================================================
        # NIVEAU DE RISQUE
        # ====================================================

        if proba < 40:

            risk_label = "Faible"
            risk_color = "#5B7F5E"

            reco = (
                "Le client présente un faible risque de départ. "
                "Maintenir la relation grâce à des actions de "
                "fidélisation et des recommandations de produits adaptées."
            )

        elif proba < 65:

            risk_label = "Moyen"
            risk_color = "#C6862E"

            reco = (
                "Le client présente un risque intermédiaire de départ. "
                "Une relance personnalisée et des recommandations "
                "de produits complémentaires peuvent renforcer son engagement."
            )

        else:

            risk_label = "Élevé"
            risk_color = "#A8452F"

            reco = (
                "Le client présente un risque élevé de départ. "
                "Une campagne de réactivation personnalisée avec "
                "une offre adaptée à son comportement d'achat est recommandée."
            )

        # ====================================================
        # RESULTAT
        # ====================================================

        st.markdown("---")

        st.markdown(
            "### Résultat de l'analyse"
        )

        result_col1, result_col2 = st.columns(
            [3, 1],
            gap="large",
        )

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        with result_col1:

            result_box(
                f"{proba:.0f}%",
                f"Risque {risk_label}",
                risk_color,
                reco,
            )

        # ----------------------------------------------------
        # VALEUR CLIENT
        # ----------------------------------------------------

        with result_col2:

            if clv_artifact is not None:

                try:

                    clv_row = pd.DataFrame(
                        [
                            {
                                feature: input_values.get(
                                    feature,
                                    0.0,
                                )
                                for feature in clv_artifact["features"]
                            }
                        ]
                    )

                    clv_pred = predict_value(
                        clv_artifact,
                        clv_row,
                    )

                    st.metric(
                        "Valeur client estimée",
                        f"{clv_pred:,.0f}",
                    )

                except Exception:

                    st.markdown(
                        """
                        <div class="note">
                            La valeur client estimée n'est pas
                            disponible pour ce profil.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        # ====================================================
        # EXPLICATION DU SCORE
        # ====================================================

        st.markdown("")

        st.markdown(
            f"""
            <div class="note">
                <strong>Résultat :</strong>
                le modèle estime une probabilité de départ de
                <strong>{proba:.1f} %</strong>.
                Le niveau de risque est donc considéré comme
                <strong>{risk_label.lower()}</strong>.
            </div>
            """,
            unsafe_allow_html=True,
        )