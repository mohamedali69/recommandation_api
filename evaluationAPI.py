from flask import Flask, jsonify, request
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Lecture du fichier CSV
df = pd.read_csv("offres.csv", delimiter=";")

@app.route('/offres', methods=['POST'])
def recherche_offres():
    # Récupération des critères de recherche de l'utilisateur depuis la requête POST
    niveau_etude = request.json['niveau_etude']
    annees_experience = request.json['annees_experience']
    competences = request.json['competences']

    # Filtrer les offres selon les critères de recherche
    df_filtre = df[df["niveau_etude_requis"].apply(lambda x: x.lower() <= niveau_etude.lower())]
    df_filtre = df_filtre[df_filtre["annees_experience_requises"] <= annees_experience]

    # Utiliser scikit-learn pour le tri des offres en fonction des compétences de l'utilisateur
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(df_filtre["competences_requises"])
    user_skills = vectorizer.transform([", ".join(competences)])
    scores = cosine_similarity(X, user_skills).flatten()
    df_filtre["score"] = scores * 100
    df_filtre = df_filtre[df_filtre["score"] > 30]

    # Afficher les offres triées par score décroissant
    df_filtre = df_filtre.sort_values(by="score", ascending=False)

    # Générer une liste de dictionnaires pour chaque offre d'emploi correspondant aux critères de recherche
    offres = []
    for index, row in df_filtre.iterrows():
        offre = {
            "titre": row["titre"],
            "niveau_etude_requis": row["niveau_etude_requis"],
            "annees_experience_requises": row["annees_experience_requises"],
            "description": row["description"],
            "competences_requises": row["competences_requises"],
            "score": round(row["score"], 2)
        }
        offres.append(offre)

    # Retourner les offres triées et leur score de correspondance sous forme de réponse JSON
    return jsonify(offres)

if __name__ == '__main__':
    app.run(debug=True)
