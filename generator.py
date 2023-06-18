import random
import csv

titres = ["Développeur web", "Ingénieur Data", "Responsable Marketing", "Chef de projet digital", "Développeur mobile"]
competences = ["Python", "SQL", "HTML/CSS", "JavaScript", "Marketing digital", "Gestion de projet"]
niveaux_bac = [2, 3, 5]
descriptions = ["Nous recherchons un développeur web pour rejoindre notre équipe dynamique.",
                "Nous recherchons un ingénieur Data pour travailler sur nos projets Big Data.",
                "Nous recherchons un responsable Marketing pour développer notre stratégie de communication.",
                "Nous recherchons un chef de projet digital pour gérer nos projets web et mobiles.",
                "Nous recherchons un développeur mobile pour rejoindre notre équipe de développement."]
experiences = [1, 2, 3, 4, 5]

with open("offres.csv", mode="w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file, delimiter=";")
    writer.writerow(["titre", "competences_requises", "niveau_etude_requis", "description", "annees_experience_requises"])
    for i in range(40):
        titre = random.choice(titres)
        competence1 = random.choice(competences)
        competence2 = random.choice(competences)
        while competence2 == competence1:
            competence2 = random.choice(competences)
        niveau_bac = random.choice(niveaux_bac)
        description = random.choice(descriptions)
        experience = random.choice(experiences)
        writer.writerow([titre, competence1+", "+competence2, "bac+"+str(niveau_bac), description, experience])
