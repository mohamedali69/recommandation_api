from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)
# Modèle du candidat


class Candidat:
    def __init__(self, niveau, specialite, competences, experience, cv):
        self.niveau = niveau
        self.specialite = specialite
        self.competences = competences
        self.experience = experience
        self.cv = cv

# Modèle de l'offre


class Offre:
    def __init__(self, id, titre, competences, niveau, experience, description, salaire, adresse, type, societe, updatedAt):
        self.id = id
        self.titre = titre
        self.competences = competences
        self.niveau = niveau
        self.experience = experience
        self.description = description
        self.salaire = salaire
        self.adresse = adresse
        self.type = type
        self.societe = societe
        self.updatedAt = updatedAt


@app.route('/recommendations', methods=['POST'])
def get_matching_offres():
    profile_data = request.json  # Récupérer les données du profil du candidat

    offres_response = requests.get('http://localhost:8080/api/offres')
    offres_data = offres_response.json()  # Convertir la réponse en format JSON

    candidat = Candidat(
        niveau=profile_data['niveau'],
        specialite=profile_data['specialite'],
        competences=profile_data['competences'],
        experience=profile_data['experience'],
        cv=profile_data['cv']
    )

    offres = []
    for offre in offres_data:
        offre_obj = Offre(
            id=offre['id'],
            titre=offre['titre'],
            competences=offre['competences'],
            niveau=offre['niveau'],
            experience=offre['experience'],
            description=offre['description'],
            salaire=offre['salaire'],
            adresse=offre['adresse'],
            type=offre['type'],
            societe=offre['societe'],
            updatedAt=offre['updatedAt']
        )
        offres.append(offre_obj)

    matching_offres = find_matching_offres(candidat, offres)
    matching_offres_json = [offre.__dict__ for offre in matching_offres]

    return jsonify(matching_offres_json)


def find_matching_offres(candidat, offres):
    vectorizer = TfidfVectorizer()
    corpus = [candidat.competences] + [offre.competences for offre in offres]
    features = vectorizer.fit_transform(corpus)
    candidate_vector = features[0]
    offre_vectors = features[1:]

    similarities = cosine_similarity(candidate_vector, offre_vectors)
    matching_offres = []

    for i, similarity in enumerate(similarities[0]):
        if similarity > 0.3:
            matching_offres.append(offres[i])

    return matching_offres


if __name__ == '__main__':
    app.run()
