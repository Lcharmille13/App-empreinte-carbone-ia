"""
Génère un dataset simulé de cas d'usage administratifs de l'IA,
à partir de la méthodologie de calcul.py, avec bruit aléatoire.

Dataset simulé, pas mesuré : sert à démontrer statistiquement l'effet
du type de requête (donc du degré d'autonomie/agentivité) sur l'empreinte,
en l'absence de données réelles publiées par les fournisseurs d'IA.
"""
import numpy as np
import pandas as pd
from calcul import calculer_empreinte, ENERGIE_PAR_REQUETE_WH

np.random.seed(42)  # pour que le dataset soit reproductible

ADMINISTRATIONS = ["Bercy", "France Travail", "DGFiP", "Justice", "France Services",
                    "Ministère Europe et Affaires étrangères", "DREAL", "ANCT"]

# Poids réalistes : les administrations utilisent surtout du texte, peu de raisonnement
# (cohérent avec l'état des lieux documenté en 1.2/2.1 de ton mémoire)
TYPES_REQUETE = list(ENERGIE_PAR_REQUETE_WH.keys())
POIDS_TYPES = [0.40, 0.35, 0.15, 0.10]  # texte_simple, texte_complexe, image, raisonnement


def generer_dataset(n_lignes: int = 500) -> pd.DataFrame:
    lignes = []
    for _ in range(n_lignes):
        administration = np.random.choice(ADMINISTRATIONS)
        type_requete = np.random.choice(TYPES_REQUETE, p=POIDS_TYPES)
        nb_agents = int(np.random.lognormal(mean=6, sigma=1.5))       # majorité petite, quelques très grands
        nb_agents = max(10, min(nb_agents, 200_000))
        requetes_par_agent = np.random.randint(5, 80)
        nb_requetes = nb_agents * requetes_par_agent

        pue = round(np.random.uniform(1.1, 1.6), 2)
        intensite_carbone = round(np.random.uniform(25, 55), 1)  # variabilité horaire/saisonnière du mix FR

        empreinte = calculer_empreinte(nb_requetes, type_requete, pue, intensite_carbone)

        # Bruit aléatoire ±10% pour simuler la variabilité réelle des conditions d'exécution
        bruit = np.random.normal(1.0, 0.10)
        emissions_kg = max(0, empreinte["total_kg"] * bruit)

        lignes.append({
            "administration": administration,
            "type_requete": type_requete,
            "nb_agents": nb_agents,
            "requetes_par_agent": requetes_par_agent,
            "nb_requetes_total": nb_requetes,
            "pue": pue,
            "intensite_carbone": intensite_carbone,
            "emissions_kg_co2e": round(emissions_kg, 2),
        })
    df = pd.DataFrame(lignes)
    df["emissions_g_par_requete"] = (df["emissions_kg_co2e"] * 1000) / df["nb_requetes_total"]

    return df



if __name__ == "__main__":
    df = generer_dataset(500)
    df.to_csv("dataset_cas_usage.csv", index=False)
    print(f"Dataset généré : {len(df)} lignes → dataset_cas_usage.csv")
    print(df.head())