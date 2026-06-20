import csv

fichier_entree = "Cible d'exploration point.csv"
fichier_sortie = "cibles_exploration_lithium_pegmatite.csv"

colonnes_recherche = [
    "ELEM_CHIM1", "ELEM_CHIM2", "ELEM_CHIM3", "ELEM_CHIM4", "ELEM_CHIM5",
    "MINR_SUBS1", "MINR_SUBS2", "MINR_SUBS3", "MINR_SUBS4", "MINR_SUBS5",
    "AUTR_SUBS1", "AUTR_SUBS2", "AUTR_SUBS3", "AUTR_SUBS4", "AUTR_SUBS5",
    "DESCR1", "DESCR2", "DESCR3", "DESCR4",
    "DESCR_ANG1", "DESCR_ANG2", "DESCR_ANG3", "DESCR_ANG4",
    "NOM_PROJE", "CODE_TYPOL"
]

mots_cles = [
    "lithium",
    "pegmatite",
    "spodumène",
    "spodumene",
    "tantale",
    "césium",
    "cesium",
    "rubidium",
    "niobium"
]

with open(fichier_entree, "r", encoding="latin1", newline="") as f:
    lecteur = csv.DictReader(f)
    lignes = list(lecteur)
    colonnes = lecteur.fieldnames

resultats = []

for ligne in lignes:
    textes = []

    for col in colonnes_recherche:
        valeur = ligne.get(col, "")
        if valeur:
            textes.append(str(valeur))

    texte = " ".join(textes).lower()

    trouve = False
    mots_trouves = []

    for mot in mots_cles:
        if mot.lower() in texte:
            trouve = True
            mots_trouves.append(mot)

    if trouve:
        nouvelle_ligne = ligne.copy()
        nouvelle_ligne["MOTS_CLES_TROUVES"] = ", ".join(mots_trouves)
        resultats.append(nouvelle_ligne)

print("Nombre total de cibles :", len(lignes))
print("Nombre de cibles potentiellement liées au lithium/pegmatites :", len(resultats))

print("\nAperçu des cibles trouvées :")
for ligne in resultats[:10]:
    print(
        ligne.get("ID_CIBLE", ""),
        "| Type :", ligne.get("TYPE", ""),
        "| Nature :", ligne.get("NATUR", ""),
        "| Mots trouvés :", ligne.get("MOTS_CLES_TROUVES", ""),
        "| Coordonnées :", ligne.get("Coord_X", ""), ligne.get("Coord_Y", "")
    )

nouvelles_colonnes = colonnes + ["MOTS_CLES_TROUVES"]

with open(fichier_sortie, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=nouvelles_colonnes)
    writer.writeheader()
    writer.writerows(resultats)

print("\nFichier exporté :", fichier_sortie)