import pandas as pd

# Charger la base
df = pd.read_csv("Mines_projets.csv", sep=",", encoding="latin1")

print("Base chargée avec succès")
print("Dimensions :", df.shape)

print("\nColonnes disponibles :")
print(df.columns.tolist())

print("\nPremières lignes :")
print(df.head())

# Identifier les colonnes de substances
colonnes_substances = [col for col in df.columns if col.startswith("CODE_SUB")]

print("\nColonnes substances :")
print(colonnes_substances)

# Filtrer les projets liés au lithium
df_lithium = df[df[colonnes_substances].eq("Li2O").any(axis=1)]

print("\nNombre de projets lithium :", len(df_lithium))

print("\nListe des projets lithium :")
print(df_lithium[[
    "NOM_MINE",
    "STAT_MINE",
    "PROMOTEUR",
    "PLAN_NORD",
    "TYPE_EXPLO",
    "Coord_X",
    "Coord_Y"
]])

print("\nRépartition Plan Nord :")
print(df_lithium["PLAN_NORD"].value_counts())

print("\nRépartition par statut :")
print(df_lithium["STAT_MINE"].value_counts().sort_index())

print("\nRépartition par promoteur :")
print(df_lithium["PROMOTEUR"].value_counts())

# Exporter les projets lithium dans un fichier Excel
df_lithium.to_excel("projets_lithium_quebec.xlsx", index=False)
print("\nFichier exporté : projets_lithium_quebec.xlsx")

import matplotlib.pyplot as plt

# Graphique 1 : Plan Nord / hors Plan Nord
plan_nord = df_lithium["PLAN_NORD"].replace({"O": "Plan Nord", "N": "Hors Plan Nord"})

plan_nord.value_counts().plot(kind="bar")
plt.title("Répartition des projets lithium selon le territoire")
plt.xlabel("Localisation")
plt.ylabel("Nombre de projets")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("graphique_plan_nord.png")
plt.close()

# Graphique 2 : Répartition par statut
df_lithium["STAT_MINE"].value_counts().sort_index().plot(kind="bar")
plt.title("Répartition des projets lithium par statut")
plt.xlabel("Statut du projet")
plt.ylabel("Nombre de projets")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("graphique_statut.png")
plt.close()

# Graphique 3 : Répartition par promoteur
df_lithium["PROMOTEUR"].value_counts().plot(kind="bar")
plt.title("Répartition des projets lithium par promoteur")
plt.xlabel("Promoteur")
plt.ylabel("Nombre de projets")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("graphique_promoteur.png")
plt.close()

print("\nGraphiques exportés avec succès.")

df_lithium.to_csv("projets_lithium_quebec.csv", index=False, encoding="utf-8-sig")
print("Fichier CSV exporté : projets_lithium_quebec.csv")

#partie 3
