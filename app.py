import streamlit as st
from calcul import calculer_empreinte
import pandas as pd
import matplotlib.pyplot as plt
from modele_prediction import charger_donnees, entrainer_modeles, importance_des_facteurs

st.set_page_config(page_title="Empreinte carbone IA", page_icon="🌱")

st.title("Combien de CO₂ derrière un service d'IA administratif ?")
st.write(
    "Preuve de concept pour objectiver l'empreinte carbone d'un service d'IA "
    "déployé dans une administration par exemple L'Assistant."
)

service = st.text_input("Nom du service (facultatif)", placeholder="ex. L'Assistant interministériel")
nb_requetes = st.number_input("Nombre de requêtes par mois", min_value=0, value=50000, step=1000)
type_requete = st.selectbox("Type de requête dominant", ["texte", "image", "raisonnement"])
baseline = st.number_input("g CO₂e par recherche web classique (hypothèse ajustable)", value=0.2, step=0.1)

if st.button("Calculer l'empreinte estimée"):
    resultat = calculer_empreinte(nb_requetes, type_requete, baseline)

    st.metric("Empreinte carbone estimée sur le mois", f"{resultat['total_kg']:.1f} kg CO₂e")

    col1, col2 = st.columns(2)
    col1.metric("Équivalent en voiture", f"{resultat['km_voiture']:.0f} km")
    col2.metric("Équivalent ampoule LED", f"{resultat['heures_ampoule']:.0f} h")

    nom = service if service else "ce service"
    st.caption(
        f"Pour **{nom}** : {nb_requetes:,} requêtes/mois × "
        f"{resultat['grammes_par_requete']:.2f} g CO₂e par requête "
        f"({type_requete}, base {baseline} g)."
    )

st.divider()
st.caption(
    "Estimation illustrative, construite à partir des multiplicateurs publiés par le "
    "Guide d'usage de l'IA pour les agents publics de l'État (2026) et d'une valeur de "
    "référence publique pour une recherche web."
)


st.divider()
st.header("🤖 Modèle prédictif — facteurs d'impact")
st.caption("Dataset simulé de 500 cas d'usage administratifs, à partir de la méthodologie cycle de vie (voir mémoire, 3.3).")

if st.button("Entraîner les modèles"):
    X, y = charger_donnees()
    resultats, X_train = entrainer_modeles(X, y)

    col1, col2 = st.columns(2)
    col1.metric("R² — Régression linéaire", resultats["Régression linéaire"]["r2"])
    col2.metric("R² — Random forest", resultats["Random forest"]["r2"])

    importances = importance_des_facteurs(resultats, X_train)
    st.subheader("Quel facteur pèse le plus sur les émissions ?")
    st.bar_chart(importances.set_index("facteur")["importance"])
    st.dataframe(importances, use_container_width=True)

    
        #Création d'un bouton pour télécharger les résultats en fichier CVS

data = { 
        "texte": ['5'],          
        "image": ['60'],         
        "raisonnement": ['80'],
        }

df = pd.DataFrame(data)
csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Télécharger les données en CSV",
    data=csv,
    file_name='donnees.csv',
    mime='text/csv',
)

