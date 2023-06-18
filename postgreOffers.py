from flask import Flask, jsonify, request
import psycopg2
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Connexion à la base de données PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="jobyssey",
    user="postgres",
    password="Dali123;"
)

# Déclaration du curseur pour interagir avec la base de données
cur = conn.cursor()


@app.route('/offres', methods=['POST'])
def recherche_offres():
    # Récupération des critères de recherche de l'utilisateur depuis la requête POST
    niveau_etude = request.json['niveau_etude']
    annees_experience = request.json['annees_experience']
    competences_valables = request.json['competences_valables']
    print("niveau_etude: ", niveau_etude)
    print("annees_experience: ", annees_experience)
    print("competences: ", competences_valables)
    # Filtrer les offres selon les critères de recherche
    cur.execute("SELECT * FROM offres WHERE niveau <= %s AND experience <= %s",
                (niveau_etude, annees_experience))
    df_filtre = pd.DataFrame(cur.fetchall(), columns=['id', 'titre', 'niveau', 'experience', 'description',
                             'salaire', 'adresse', 'type', 'competences', 'createdAt', 'updatedAt', 'categorieId', 'societeId'])
    print("df_filtre: ", df_filtre)
    # Utiliser scikit-learn pour le tri des offres en fonction des compétences de l'utilisateur
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(df_filtre["competences"])
    print("X: ", X)
    if not competences_valables:
        return jsonify({'error': 'No valid competences provided'})
    user_skills_input = ", ".join(competences_valables)
    print("user_skills_input: ", user_skills_input)
    user_skills = vectorizer.transform([", ".join(competences_valables)])
    print("user_skills: ", user_skills)
    print("user_skills shape: ", user_skills.shape)
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
            "niveau": row["niveau"],
            "experience": row["experience"],
            "description": row["description"],
            "competences": row["competences"],
            "salaire": row["salaire"],
            "adresse": row["adresse"],
            "type": row["type"],
            "createdAt": row["createdAt"],
            "updatedAt": row["updatedAt"],
            "categorieId": row["categorieId"],
            "societeId": row["societeId"],
        }
        offres.append(offre)
    print("offres: ", offres)
    # Retourner les offres triées et leur score de correspondance sous forme de réponse JSON
    return jsonify(offres)


if __name__ == '__main__':
    app.run(debug=True)
