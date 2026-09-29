"""
Entraîne et compare deux modèles de prédiction de l'empreinte carbone
à partir des caractéristiques d'un cas d'usage : régression linéaire
et random forest. Objectif : identifier quel facteur pèse le plus
sur les émissions (feature importance).
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


def charger_donnees(chemin: str = "dataset_cas_usage.csv", cible: str = "emissions_kg_co2e",
                     inclure_volume: bool = True):
    df = pd.read_csv(chemin)
    features = ["type_requete", "pue", "intensite_carbone"]
    if inclure_volume:
        features += ["nb_agents", "requetes_par_agent"]
    X = df[features]
    y = df[cible]
    return X, y


def entrainer_modeles(X, y):
       X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

       preprocesseur = ColumnTransformer([
        ("categorie", OneHotEncoder(), ["type_requete"]),
    ], remainder="passthrough")

       modeles = [
        ("Régression linéaire", LinearRegression()),
        ("Random forest", RandomForestRegressor(n_estimators=200, random_state=42))
    ]
       resultats = {}
       for nom, modele in modeles:
        pipeline = Pipeline([("prep", preprocesseur), ("modele", modele)])
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        resultats[nom] = {
            "pipeline": pipeline,
            "r2": round(r2_score(y_test, y_pred), 3),
            "mae": round(mean_absolute_error(y_test, y_pred), 3),
        }

       return resultats, X_train


def importance_des_facteurs(resultats, X_train):
    """Extrait l'importance de chaque facteur depuis le Random Forest (plus interprétable qu'une régression)."""
    pipeline_rf = resultats["Random forest"]["pipeline"]
    modele_rf = pipeline_rf.named_steps["modele"]
    noms_colonnes = pipeline_rf.named_steps["prep"].get_feature_names_out()

    importances = pd.DataFrame({
        "facteur": noms_colonnes,
        "importance": modele_rf.feature_importances_,
    }).sort_values("importance", ascending=False)

    return importances

def graphique_comparatif(chemin_sortie: str = "importance_facteurs.png"):
    """Compare l'importance des facteurs entre le modèle 'volume total' et le modèle 'par requête'."""
    import matplotlib.pyplot as plt

    # Modèle 1 : émissions totales, avec le volume comme feature
    X1, y1 = charger_donnees(cible="emissions_kg_co2e", inclure_volume=True)
    resultats1, X_train1 = entrainer_modeles(X1, y1)
    imp1 = importance_des_facteurs(resultats1, X_train1)

    # Modèle 2 : émissions par requête, sans le volume (pour isoler l'effet du type d'usage)
    X2, y2 = charger_donnees(cible="emissions_g_par_requete", inclure_volume=False)
    resultats2, X_train2 = entrainer_modeles(X2, y2)
    imp2 = importance_des_facteurs(resultats2, X_train2)

    def nettoyer_labels(df_imp):
        return df_imp["facteur"].str.replace("categorie__type_requete_", "", regex=False)\
                                  .str.replace("remainder__", "", regex=False)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].barh(nettoyer_labels(imp1), imp1["importance"], color="#3F6B4A")
    axes[0].set_title(f"Émissions totales\n(R² Random forest = {resultats1['Random forest']['r2']})")
    axes[0].invert_yaxis()

    axes[1].barh(nettoyer_labels(imp2), imp2["importance"], color="#C9A227")
    axes[1].set_title(f"Émissions par requête\n(R² Random forest = {resultats2['Random forest']['r2']})")
    axes[1].invert_yaxis()

    fig.suptitle("Quel facteur pèse le plus sur l'empreinte carbone d'un usage IA ?", fontsize=13)
    plt.tight_layout()
    plt.savefig(chemin_sortie, dpi=150, bbox_inches="tight")
    print(f"Graphique enregistré → {chemin_sortie}")


if __name__ == "__main__":
    graphique_comparatif()