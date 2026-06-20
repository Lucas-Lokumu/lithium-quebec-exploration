import csv

fichier_entree = "Substances metalliques.csv"
fichier_sortie = "indices_lithium_gmli_quebec.csv"

# Lecture du CSV
with open(fichier_entree, "r", encoding="latin1", newline="") as f:
    lecteur = csv.DictReader(f)
    colonnes = lecteur.fieldnames
    lignes = list(lecteur)

print("Base chargée avec succès")
print("Nombre de lignes :", len(lignes))
print("Nombre de colonnes :", len(colonnes))

print("\nColonnes disponibles :")
print(colonnes)

# Recherche des lignes liées au lithium
mots_cles = ["GMLI", "Li", "Lithium", "lithium", "spodumène", "spodumene", "pegmatite"]

for mot in mots_cles:
    resultats = []
    for ligne in lignes:
        texte_ligne = " ".join(str(valeur) for valeur in ligne.values())
        if mot.lower() in texte_ligne.lower():
            resultats.append(ligne)

    print(f"\nMot-clé : {mot}")
    print("Nombre de lignes trouvées :", len(resultats))

# Filtre principal : GMLI
lignes_gmli = []
for ligne in lignes:
    texte_ligne = " ".join(str(valeur) for valeur in ligne.values())
    if "GMLI" in texte_ligne.upper():
        lignes_gmli.append(ligne)

print("\nNombre total d'occurrences GMLI :", len(lignes_gmli))

print("\nAperçu des premières occurrences GMLI :")
for ligne in lignes_gmli[:5]:
    print(ligne)

# Export du fichier filtré
with open(fichier_sortie, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=colonnes)
    writer.writeheader()
    writer.writerows(lignes_gmli)

print("\nFichier exporté :", fichier_sortie)