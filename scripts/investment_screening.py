import csv

INPUT_FILE = "croisement_potentiel_cibles_lithium.csv"
OUTPUT_FILE = "investment_screening_lithium_quebec.csv"

zones = {
    "Adina / Adina Main": ["Adina Main (Jamar)"],
    "CV5 / CV13 / Shaakichiuwaanaan": ["CV13", "CV5"],
    "Galaxy / Cyr-Lithium": ["Cyr-Lithium (James Bay Lithium)"],
    "Rose / Whabouchi": ["Rose", "Whabouchi"],
    "Moblan / Sirmac-Dike #5": ["Lac Moblan Ouest", "Sirmac"],
    "Authier / Complexe Lithium Amérique du Nord": ["Authier"],
}

def to_float(value):
    if value is None:
        return None
    value = str(value).replace(",", ".").strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None

with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Garder seulement les lignes au score maximal
top_rows = []
for row in rows:
    score = to_float(row.get("SCORE_POTENTIEL"))
    if score == 14:
        top_rows.append(row)

results = []

for zone, noms_occurrences in zones.items():
    zone_rows = []

    for row in top_rows:
        nom_gite = row.get("NOM_GITE", "").strip()
        nom_corps = row.get("NOM_CORPS", "").strip()

        for nom in noms_occurrences:
            if nom in nom_gite or nom in nom_corps:
                zone_rows.append(row)

    if not zone_rows:
        continue

    projets = sorted(set(
        row.get("PROJET_PLUS_PROCHE", "").strip()
        for row in zone_rows
        if row.get("PROJET_PLUS_PROCHE", "").strip()
    ))

    cibles = sorted(set(
        row.get("CIBLE_PLUS_PROCHE", "").strip()
        for row in zone_rows
        if row.get("CIBLE_PLUS_PROCHE", "").strip()
    ))

    distances_projet = [
        to_float(row.get("DISTANCE_PROJET_KM"))
        for row in zone_rows
        if to_float(row.get("DISTANCE_PROJET_KM")) is not None
    ]

    distances_cible = [
        to_float(row.get("DISTANCE_CIBLE_KM"))
        for row in zone_rows
        if to_float(row.get("DISTANCE_CIBLE_KM")) is not None
    ]

    distance_min_projet = min(distances_projet) if distances_projet else None
    distance_min_cible = min(distances_cible) if distances_cible else None

    classes = sorted(set(
        row.get("CLASSE_DISTANCE_CIBLE", "").strip()
        for row in zone_rows
        if row.get("CLASSE_DISTANCE_CIBLE", "").strip()
    ))

    if distance_min_cible is not None and distance_min_cible <= 20:
        interet = "Élevé"
        risque = "Modéré"
        signal = "Score maximal, cible très proche, projet lithium proche"
    elif distance_min_cible is not None and distance_min_cible <= 100:
        interet = "Moyen à élevé"
        risque = "Modéré à élevé"
        signal = "Score maximal, cible dans un rayon de 100 km, projet lithium proche"
    else:
        interet = "Moyen"
        risque = "Élevé"
        signal = "Score maximal et projet lithium proche, mais cible éloignée"

    results.append({
        "zone_prioritaire": zone,
        "occurrences_associees": ", ".join(noms_occurrences),
        "projets_associes": ", ".join(projets),
        "score_prospectivite_max": 14,
        "distance_min_projet_km": round(distance_min_projet, 2) if distance_min_projet is not None else "",
        "distance_min_cible_km": round(distance_min_cible, 2) if distance_min_cible is not None else "",
        "classe_distance_cible": ", ".join(classes),
        "cibles_associees": ", ".join(cibles),
        "signal_spatial": signal,
        "risque_exploration": risque,
        "interet_investisseur": interet,
        "commentaire": "Pré-analyse indicative fondée sur les données SIGÉOM, le score de prospectivité et les distances spatiales."
    })

fieldnames = [
    "zone_prioritaire",
    "occurrences_associees",
    "projets_associes",
    "score_prospectivite_max",
    "distance_min_projet_km",
    "distance_min_cible_km",
    "classe_distance_cible",
    "cibles_associees",
    "signal_spatial",
    "risque_exploration",
    "interet_investisseur",
    "commentaire"
]

with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print("Fichier créé :", OUTPUT_FILE)
print("Nombre de zones exportées :", len(results))

for r in results:
    print("-", r["zone_prioritaire"], "|", r["interet_investisseur"])