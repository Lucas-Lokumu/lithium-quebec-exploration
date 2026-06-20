import csv
import math
from collections import Counter

# Fichiers d'entrée
fichier_indices = "indices_lithium_gmli_quebec.csv"
fichier_projets = "projets_lithium_quebec.csv"

# Fichiers de sortie
fichier_sortie = "score_potentiel_lithium_quebec.csv"
fichier_synthese = "synthese_potentiel_lithium.txt"


def convertir_float(valeur):
    try:
        return float(str(valeur).replace(",", "."))
    except:
        return None


def distance_km(lon1, lat1, lon2, lat2):
    """
    Distance approximative entre deux points GPS en kilomètres.
    Formule de Haversine.
    """
    rayon_terre = 6371

    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return rayon_terre * c


# Charger les indices GMLI
with open(fichier_indices, "r", encoding="utf-8-sig", newline="") as f:
    lecteur = csv.DictReader(f)
    indices = list(lecteur)
    colonnes_indices = lecteur.fieldnames

# Charger les projets lithium connus
with open(fichier_projets, "r", encoding="utf-8-sig", newline="") as f:
    lecteur = csv.DictReader(f)
    projets = list(lecteur)

print("Indices GMLI chargés :", len(indices))
print("Projets lithium chargés :", len(projets))

# Colonnes de substances associées
colonnes_substances = [
    "SUBST_PRIN", "SUBST_P2", "SUBST_P3", "SUBST_P4", "SUBST_P5", "SUBST_P6",
    "SUBST_P7", "SUBST_P8", "SUBST_P9", "SUBST_P10", "SUBST_P11", "SUBST_P12",
    "SUBST_SECN", "SUBST_S2", "SUBST_S3", "SUBST_S4", "SUBST_S5", "SUBST_S6",
    "SUBST_S7", "SUBST_S8", "SUBST_S9", "SUBST_S10", "SUBST_S11", "SUBST_S12"
]

substances_associees_importantes = ["Ta", "Cs", "Be", "Nb", "Rb"]

resultats = []

for indice in indices:
    score = 0
    commentaires = []

    nom_gite = indice.get("NOM_GITE", "")
    nom_corps = indice.get("NOM_CORPS", "")
    etat = indice.get("ETAT_CORPS", "")
    code_etat = indice.get("CODE_ETAT", "")
    typl = indice.get("TYPL", "")
    ressource_estimee = indice.get("RESS_ESTIM", "")
    code_symbl = indice.get("CODE_SYMBL", "")

    # 1. Présence du code GMLI
    if "GMLI" in code_symbl.upper():
        score += 2
        commentaires.append("Code GMLI")

    # 2. Lithium en substance principale
    if indice.get("SUBST_PRIN", "").strip().lower() == "li":
        score += 2
        commentaires.append("Lithium en substance principale")

    # 3. Typologie pegmatitique
    if "pegmatite" in typl.lower():
        score += 2
        commentaires.append("Typologie pegmatitique")

    # 4. Ressource estimée
    if ressource_estimee.strip().upper() == "O":
        score += 2
        commentaires.append("Ressource estimée")

    # 5. État du corps : gîte ou indice travaillé
    if code_etat.strip().upper() == "G":
        score += 2
        commentaires.append("Gîte")
    elif code_etat.strip().upper() == "P":
        score += 1
        commentaires.append("Indice travaillé")

    # 6. Substances associées typiques des pegmatites lithium
    substances_ligne = []
    for col in colonnes_substances:
        valeur = indice.get(col, "").strip()
        if valeur:
            substances_ligne.append(valeur)

    associees_trouvees = [
        s for s in substances_associees_importantes
        if s in substances_ligne
    ]

    if associees_trouvees:
        score += 1
        commentaires.append("Substances associées : " + ", ".join(associees_trouvees))

    # 7. Distance au projet lithium connu le plus proche
    lon_i = convertir_float(indice.get("Coord_X", ""))
    lat_i = convertir_float(indice.get("Coord_Y", ""))

    distance_min = None
    projet_plus_proche = ""

    if lon_i is not None and lat_i is not None:
        for projet in projets:
            lon_p = convertir_float(projet.get("Coord_X", ""))
            lat_p = convertir_float(projet.get("Coord_Y", ""))

            if lon_p is not None and lat_p is not None:
                d = distance_km(lon_i, lat_i, lon_p, lat_p)

                if distance_min is None or d < distance_min:
                    distance_min = d
                    projet_plus_proche = projet.get("NOM_MINE", "")

    if distance_min is not None:
        if distance_min <= 25:
            score += 3
            commentaires.append("Très proche d’un projet lithium connu")
        elif distance_min <= 50:
            score += 2
            commentaires.append("Proche d’un projet lithium connu")
        elif distance_min <= 100:
            score += 1
            commentaires.append("Dans un rayon de 100 km d’un projet lithium connu")

    # Classement final
    if score >= 9:
        classe = "Potentiel fort"
    elif score >= 6:
        classe = "Potentiel moyen"
    else:
        classe = "Potentiel faible"

    nouvelle_ligne = indice.copy()
    nouvelle_ligne["SCORE_POTENTIEL"] = score
    nouvelle_ligne["CLASSE_POTENTIEL"] = classe
    nouvelle_ligne["PROJET_PLUS_PROCHE"] = projet_plus_proche
    nouvelle_ligne["DISTANCE_PROJET_KM"] = round(distance_min, 2) if distance_min is not None else ""
    nouvelle_ligne["COMMENTAIRE_SCORE"] = " | ".join(commentaires)

    resultats.append(nouvelle_ligne)


# Trier du score le plus fort au plus faible
resultats = sorted(resultats, key=lambda x: int(x["SCORE_POTENTIEL"]), reverse=True)

# Export CSV
nouvelles_colonnes = colonnes_indices + [
    "SCORE_POTENTIEL",
    "CLASSE_POTENTIEL",
    "PROJET_PLUS_PROCHE",
    "DISTANCE_PROJET_KM",
    "COMMENTAIRE_SCORE"
]

with open(fichier_sortie, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=nouvelles_colonnes)
    writer.writeheader()
    writer.writerows(resultats)

# Synthèse
compteur_classes = Counter([ligne["CLASSE_POTENTIEL"] for ligne in resultats])
compteur_etats = Counter([ligne.get("ETAT_CORPS", "") for ligne in resultats])
compteur_typologie = Counter([ligne.get("TYPL", "") for ligne in resultats])

top_10 = resultats[:10]

with open(fichier_synthese, "w", encoding="utf-8-sig") as f:
    f.write("SYNTHÈSE — SCORE EXPLORATOIRE DU POTENTIEL LITHIUM\n\n")
    f.write(f"Nombre total d'occurrences GMLI analysées : {len(resultats)}\n\n")

    f.write("Répartition par classe de potentiel :\n")
    for classe, nombre in compteur_classes.items():
        f.write(f"- {classe} : {nombre}\n")

    f.write("\nRépartition par état du corps :\n")
    for etat, nombre in compteur_etats.most_common():
        f.write(f"- {etat} : {nombre}\n")

    f.write("\nPrincipales typologies :\n")
    for typologie, nombre in compteur_typologie.most_common(10):
        f.write(f"- {typologie} : {nombre}\n")

    f.write("\nTop 10 des occurrences au score le plus élevé :\n")
    for ligne in top_10:
        f.write(
            f"- {ligne.get('NOM_GITE', '')} | "
            f"Score : {ligne['SCORE_POTENTIEL']} | "
            f"Classe : {ligne['CLASSE_POTENTIEL']} | "
            f"Projet proche : {ligne['PROJET_PLUS_PROCHE']} | "
            f"Distance : {ligne['DISTANCE_PROJET_KM']} km\n"
        )

print("\nAnalyse terminée.")
print("Fichier exporté :", fichier_sortie)
print("Synthèse exportée :", fichier_synthese)

print("\nRépartition par classe de potentiel :")
for classe, nombre in compteur_classes.items():
    print(classe, ":", nombre)

print("\nTop 10 des occurrences les plus prometteuses :")
for ligne in top_10:
    print(
        ligne.get("NOM_GITE", ""),
        "| Score :", ligne["SCORE_POTENTIEL"],
        "| Classe :", ligne["CLASSE_POTENTIEL"],
        "| Projet proche :", ligne["PROJET_PLUS_PROCHE"],
        "| Distance :", ligne["DISTANCE_PROJET_KM"], "km"
    )