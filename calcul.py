"""
Moteur de calcul de l'empreinte carbone d'un usage de service IA.
Méthodologie : approche cycle de vie (énergie x intensité carbone),
inspirée des méthodologies publiques de type MLCO2 / Green Algorithms.

Sources des valeurs par défaut :
- Énergie par requête : ordres de grandeur issus de la littérature
  (Luccioni et al. 2023, "Power Hungry Processing", ACM FAccT)
- PUE datacenter : moyenne secteur ~1,5 ; datacenters performants ~1,2
- Intensité carbone électricité française : RTE, Bilan électrique 2025
  (~40 gCO2e/kWh en analyse de cycle de vie complète)
"""

# Énergie moyenne consommée par requête, en Wh, selon la complexité de la tâche.
# Ce sont des ordres de grandeur ajustables, pas des constantes absolues.
ENERGIE_PAR_REQUETE_WH = {
    "texte_simple": 0.4,       # reformulation courte, résumé bref
    "texte_complexe": 2.5,     # rédaction longue, synthèse de document
    "image": 15.0,             # génération d'image
    "raisonnement": 25.0,      # modèle de raisonnement, chaîne de calcul multiple
}

PUE_DEFAUT = 1.2
INTENSITE_CARBONE_DEFAUT_G_KWH = 40.0  # gCO2e/kWh, RTE, cycle de vie complet

# Facteurs pour les équivalences pédagogiques
GRAMMES_CO2_PAR_KM_VOITURE = 120
PUISSANCE_AMPOULE_LED_W = 10
GRAMMES_CO2_PAR_KWH_AMPOULE = INTENSITE_CARBONE_DEFAUT_G_KWH


def calculer_empreinte(
    nb_requetes: int,
    type_requete: str,
    pue: float = PUE_DEFAUT,
    intensite_carbone: float = INTENSITE_CARBONE_DEFAUT_G_KWH,
) -> dict:
    """
    Calcule l'empreinte carbone estimée pour un volume de requêtes,
    selon une approche cycle de vie (énergie x intensité carbone).

    Args:
        nb_requetes: nombre de requêtes sur la période considérée
        type_requete: une clé de ENERGIE_PAR_REQUETE_WH
        pue: Power Usage Effectiveness du datacenter (défaut : 1,2)
        intensite_carbone: gCO2e par kWh consommé (défaut : mix électrique français, ACV)

    Returns:
        Un dictionnaire avec le détail du calcul et les équivalences.
    """
    if type_requete not in ENERGIE_PAR_REQUETE_WH:
        raise ValueError(f"Type de requête inconnu : {type_requete}")

    energie_brute_wh = ENERGIE_PAR_REQUETE_WH[type_requete]
    energie_reelle_wh = energie_brute_wh * pue          # on applique le PUE du datacenter
    energie_reelle_kwh = energie_reelle_wh / 1000

    grammes_par_requete = energie_reelle_kwh * intensite_carbone
    total_grammes = grammes_par_requete * nb_requetes
    total_kg = total_grammes / 1000

    km_voiture = total_grammes / GRAMMES_CO2_PAR_KM_VOITURE
    heures_ampoule = (total_grammes * 1000) / (PUISSANCE_AMPOULE_LED_W * GRAMMES_CO2_PAR_KWH_AMPOULE / 1000)

    return {
        "energie_par_requete_wh": round(energie_reelle_wh, 3),
        "grammes_par_requete": round(grammes_par_requete, 3),
        "total_grammes": round(total_grammes, 1),
        "total_kg": round(total_kg, 2),
        "km_voiture": round(km_voiture, 1),
        "heures_ampoule": round(heures_ampoule, 1),
        "pue_utilise": pue,
        "intensite_carbone_utilisee": intensite_carbone,
    }