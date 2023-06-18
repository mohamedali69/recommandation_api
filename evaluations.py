import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Lecture du fichier CSV
df = pd.read_csv("offres.csv", delimiter=";")

# Demander les critères de recherche à l'utilisateur
niveau_etude = input("Quel est votre niveau d'études (bac, bac+2, bac+3, bac+5) ? ")
annees_experience = int(input("Combien d'années d'expérience avez-vous ? "))
#filtre de base
competences = input("Veuillez saisir vos compétences (séparées par une virgule) : ")
competences = competences.lower().split(",")

# Filtrer les offres selon les critères de recherche clause where
df = df[df["niveau_etude_requis"].apply(lambda x: x.lower() <= niveau_etude.lower())]
df = df[df["annees_experience_requises"] <= annees_experience]

# Utiliser scikit-learn pour le tri des offres en fonction des compétences de l'utilisateur
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df["competences_requises"])
user_skills = vectorizer.transform([", ".join(competences)])
scores = cosine_similarity(X, user_skills).flatten()
df["score"] = scores * 100
df = df[df["score"] > 20]

# Afficher les offres triées par score décroissant avec pourcentage de correspondance
df = df.sort_values(by="score", ascending=False)
df["pourcentage_correspondance"] = round(df["score"], 2)
print(df[["titre", "competences_requises", "niveau_etude_requis", "annees_experience_requises", "description", "pourcentage_correspondance"]])
