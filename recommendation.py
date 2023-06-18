from flask import Flask, jsonify, request
import psycopg2.pool
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

# Connection pooling
conn_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host="localhost",
    database="jobyssey",
    user="postgres",
    password="Dali123;"
)

# Use a more efficient search algorithm
nbrs = NearestNeighbors(n_neighbors=10, algorithm='auto', metric='cosine')

if not hasattr(app, 'vectorizer'):
    app.vectorizer = CountVectorizer()

@app.route('/offres', methods=['POST'])
def recherche_offres():
    # Récupération des critères de recherche de l'utilisateur depuis la requête POST
    niveau_etude = request.json['niveau_etude']
    annees_experience = request.json['annees_experience']
    competences_valables = request.json['competences_valables']
    print("niveau_etude: ", niveau_etude)
    print("annees_experience: ", annees_experience)
    print("competences: ", competences_valables)

    # Use a cached connection from the connection pool
    conn = conn_pool.getconn()
    # Optimized database query
    cur = conn.cursor()
    cur.execute("SELECT * FROM offres WHERE niveau <= %s AND experience <= %s",
                (niveau_etude, annees_experience))
    rows = cur.fetchall()

    if not rows:
        return jsonify({'error': 'No matching job offers found'})

    df = pd.DataFrame(rows, columns=['id', 'titre', 'niveau', 'experience', 'description', 'competences',
                                     'salaire', 'adresse', 'type', 'categorieId', 'societeId', 'createdAt', 'updatedAt'])
    print("df: ", df)

    if not competences_valables:
        return jsonify({'error': 'No valid competences provided'})

        # Use a cached vectorizer from a previous request
    if not hasattr(app, 'vectorizer'):
        app.vectorizer = CountVectorizer()

    X = app.vectorizer.transform(df["competences"])
    print("X: ", X)

    user_skills_input = ", ".join(competences_valables)
    print("user_skills_input: ", user_skills_input)
    user_skills = app.vectorizer.transform([", ".join(competences_valables)])
    print("user_skills: ", user_skills)
    print("user_skills shape: ", user_skills.shape)

    # Use a cached fitted model from a previous request
    if not hasattr(app, 'model'):
        app.model = nbrs.fit(X)

        distances, indices = app.model.kneighbors(user_skills)

        df_filtre = df.iloc[indices[0]]
        df_filtre["score"] = (1 - distances[0]) * 100
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
                "categorieId": row["categorieId"],
                "societeId": row["societeId"],
                "score": round(row["score"], 2)
            }
        offres.append(offre)
        # Instead of iterating through rows and creating the dictionary one by one, we can create a list of dictionaries
        # using a list comprehension, which should be faster and more concise.
        offres = [
            {
                "titre": row["titre"],
                "niveau": row["niveau"],
                "experience": row["experience"],
                "description": row["description"],
                "competences": row["competences"],
                "salaire": row["salaire"],
                "adresse": row["adresse"],
                "type": row["type"],
                "categorieId": row["categorieId"],
                "societeId": row["societeId"],
                "score": round(row["score"], 2)
            }
            for _, row in df_filtre.iterrows()
        ]

    # Return the filtered and sorted job offers in JSON format
        print("offres: ", offres)


if __name__ == '__main__':
    app.run(debug=True)
