import csv
import math
from collections import Counter

fichier_indices = "score_potentiel_lithium_quebec.csv"
fichier_cibles = "cibles_exploration_lithium_pegmatite.csv"

fichier_sortie = "croisement_potentiel_cibles_lithium.csv"
fichier_synthese = "synthese_croisement_potentiel_cibles.txt"


def convertir_float(valeur):
    try:
        return float(str(valeur).replace(",", "."))
    except:
        return None


def distance_km(lon1, lat1, lon2, lat2):
    rayon_terre = 6371

    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return rayon_terre * c


# Charger les occurrences GMLI scorées
with open(fichier_indices, "r", encoding="utf-8-sig", newline="") as f:
    lecteur = csv.DictReader(f)
    indices = list(lecteur)
    colonnes_indices = lecteur.fieldnames

# Charger les cibles d'exploration lithium/pegmatites
with open(fichier_cibles, "r", encoding="utf-8-sig", newline="") as f:
    lecteur = csv.DictReader(f)
    cibles = list(lecteur)

print("Occurrences GMLI chargées :", len(indices))
print("Cibles lithium/pegmatites chargées :", len(cibles))

resultats = []

for indice in indices:
    lon_i = convertir_float(indice.get("Coord_X", ""))
    lat_i = convertir_float(indice.get("Coord_Y", ""))

    distance_min = None
    cible_plus_proche = ""
    type_cible = ""
    nature_cible = ""
    mots_cibles = ""

    if lon_i is not None and lat_i is not None:
        for cible in cibles:
            lon_c = convertir_float(cible.get("Coord_X", ""))
            lat_c = convertir_float(cible.get("Coord_Y", ""))

            if lon_c is not None and lat_c is not None:
                d = distance_km(lon_i, lat_i, lon_c, lat_c)

                if distance_min is None or d < distance_min:
                    distance_min = d
                    cible_plus_proche = cible.get("ID_CIBLE", "")
                    type_cible = cible.get("TYPE", "")
                    nature_cible = cible.get("NATUR", "")
                    mots_cibles = cible.get("MOTS_CLES_TROUVES", "")

    if distance_min is None:
        classe_distance = "Distance inconnue"
    elif distance_min <= 25:
        classe_distance = "Très proche d'une cible"
    elif distance_min <= 50:
        classe_distance = "Proche d'une cible"
    elif distance_min <= 100:
        classe_distance = "Dans un rayon de 100 km"
    else:
        classe_distance = "Éloigné des cibles"

    nouvelle_ligne = indice.copy()
    nouvelle_ligne["CIBLE_PLUS_PROCHE"] = cible_plus_proche
    nouvelle_ligne["TYPE_CIBLE"] = type_cible
    nouvelle_ligne["NATURE_CIBLE"] = nature_cible
    nouvelle_ligne["MOTS_CLES_CIBLE"] = mots_cibles
    nouvelle_ligne["DISTANCE_CIBLE_KM"] = round(distance_min, 2) if distance_min is not None else ""
    nouvelle_ligne["CLASSE_DISTANCE_CIBLE"] = classe_distance

    resultats.append(nouvelle_ligne)

# Trier par score puis proximité avec une cible
resultats = sorted(
    resultats,
    key=lambda x: (
        -int(x.get("SCORE_POTENTIEL", 0)),
        float(x.get("DISTANCE_CIBLE_KM", 999999)) if x.get("DISTANCE_CIBLE_KM", "") != "" else 999999
    )
)

nouvelles_colonnes = colonnes_indices + [
    "CIBLE_PLUS_PROCHE",
    "TYPE_CIBLE",
    "NATURE_CIBLE",
    "MOTS_CLES_CIBLE",
    "DISTANCE_CIBLE_KM",
    "CLASSE_DISTANCE_CIBLE"
]

with open(fichier_sortie, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=nouvelles_colonnes)
    writer.writeheader()
    writer.writerows(resultats)

# Synthèse
compteur_distance = Counter([ligne["CLASSE_DISTANCE_CIBLE"] for ligne in resultats])
compteur_potentiel = Counter([ligne["CLASSE_POTENTIEL"] for ligne in resultats])

top_10 = resultats[:10]

with open(fichier_synthese, "w", encoding="utf-8-sig") as f:
    f.write("SYNTHÈSE — CROISEMENT OCCURRENCES GMLI ET CIBLES D'EXPLORATION\n\n")

    f.write(f"Nombre d'occurrences GMLI analysées : {len(indices)}\n")
    f.write(f"Nombre de cibles lithium/pegmatites utilisées : {len(cibles)}\n\n")

    f.write("Répartition par classe de potentiel :\n")
    for classe, nombre in compteur_potentiel.items():
        f.write(f"- {classe} : {nombre}\n")

    f.write("\nRépartition par proximité avec une cible d'exploration :\n")
    for classe, nombre in compteur_distance.items():
        f.write(f"- {classe} : {nombre}\n")

    f.write("\nTop 10 des occurrences les plus intéressantes après croisement :\n")
    for ligne in top_10:
        f.write(
            f"- {ligne.get('NOM_GITE', '')} | "
            f"Score : {ligne.get('SCORE_POTENTIEL', '')} | "
            f"Potentiel : {ligne.get('CLASSE_POTENTIEL', '')} | "
            f"Cible proche : {ligne.get('CIBLE_PLUS_PROCHE', '')} | "
            f"Distance cible : {ligne.get('DISTANCE_CIBLE_KM', '')} km | "
            f"Classe distance : {ligne.get('CLASSE_DISTANCE_CIBLE', '')}\n"
        )

print("\nCroisement terminé.")
print("Fichier exporté :", fichier_sortie)
print("Synthèse exportée :", fichier_synthese)

print("\nRépartition par proximité avec une cible d'exploration :")
for classe, nombre in compteur_distance.items():
    print(classe, ":", nombre)

print("\nTop 10 après croisement :")
for ligne in top_10:
    print(
        ligne.get("NOM_GITE", ""),
        "| Score :", ligne.get("SCORE_POTENTIEL", ""),
        "| Potentiel :", ligne.get("CLASSE_POTENTIEL", ""),
        "| Cible proche :", ligne.get("CIBLE_PLUS_PROCHE", ""),
        "| Distance cible :", ligne.get("DISTANCE_CIBLE_KM", "km"),
        "|", ligne.get("CLASSE_DISTANCE_CIBLE", "")
    )