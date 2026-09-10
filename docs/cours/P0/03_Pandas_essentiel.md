# Pandas — Mini-cours

> Brief associé : P0
> Durée de lecture + pratique : ~45 min
> Pré-requis : Python de base, notions NumPy (cf `02_Numpy_essentiel.md`).

## Pourquoi cette techno ?

Pandas est l'outil universel de **manipulation de données tabulaires** en Python. Tu
vas en faire à toutes les phases d'un projet IA :

- charger un CSV / Excel / Parquet / SQL
- explorer un dataset (head, describe, info)
- nettoyer (manquants, doublons, types)
- transformer (filtrer, grouper, joindre, encoder)
- visualiser rapidement (`.plot()` est branché sur matplotlib)

**Alternatives modernes** : Polars (plus rapide, syntaxe différente — proche de Spark),
DuckDB (SQL embarqué, excellent pour la data engineering). Pour cette formation,
Pandas suffit largement et reste la lingua franca du domaine.

⚠️ Pandas n'est **pas** fait pour les volumes massifs (au-delà de quelques GB en
RAM). Pour le « gros » data, c'est Spark / Polars / DuckDB.

## Concepts clés

- **`Series`** : tableau 1D étiqueté (= une colonne d'un DataFrame). Repose sur un
  ndarray NumPy + un index.
- **`DataFrame`** : tableau 2D étiqueté (lignes × colonnes). C'est le héros du
  module. On lit, on transforme, on écrit.
- **Index** : étiquette des lignes. Par défaut `RangeIndex(0..n-1)`, mais peut être
  une date, un identifiant, un MultiIndex…
- **Sélection** :
  - `df["colA"]` — une colonne (Series)
  - `df[["colA", "colB"]]` — sous-DataFrame
  - `df.loc[ligne, colonne]` — sélection **par étiquette**
  - `df.iloc[row_idx, col_idx]` — sélection **par position**
  - `df[df["age"] > 30]` — filtre booléen
- **Group by** : `df.groupby("ville")["salaire"].mean()` — agrégation puissante,
  cœur de l'EDA.
- **Manquants** : `df.isna()`, `df.dropna()`, `df.fillna(...)` — toujours **enquêter**
  avant de remplir au pif.

## Exemple minimal qui tourne

```python
# Versions testées : python 3.11, pandas 2.x
import pandas as pd

# Petit dataset bidon
df = pd.DataFrame({
    "ville":   ["Paris", "Lyon", "Paris", "Marseille", "Lyon", "Paris"],
    "age":     [30, 25, 45, 28, 31, 22],
    "salaire": [42000, 38000, 65000, 35000, 41000, 30000],
    "tele":    [True, False, True, False, True, True],
})

# Inspection
print(df.head())
print()
print(df.info())
print()
print(df.describe(include="all"))

# Filtrage + sélection
print()
print(df[df["age"] > 28][["ville", "salaire"]])

# Groupby
print()
print(df.groupby("ville")["salaire"].mean().round(0))

# Petite visualisation (nécessite matplotlib)
df.groupby("ville")["salaire"].mean().plot.bar(title="Salaire moyen par ville")
```

→ Tu obtiens un DataFrame, des stats descriptives, un filtre et un graphique en barre.

## Exercice guidé

Sur le dataset **Palmer Penguins** (alternative moderne aux datasets bateaux Titanic / Iris).
Le dataset contient des mesures morphologiques de pingouins (espèces Adelie, Chinstrap, Gentoo)
sur 3 îles de l'archipel Palmer (Antarctique).

```python
import pandas as pd

URL = "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/inst/extdata/penguins.csv"
df = pd.read_csv(URL)
```

1. Combien de lignes et de colonnes ? Quelles sont les colonnes ? Combien de valeurs
   manquantes par colonne ?
2. Quelle est la **masse corporelle moyenne** (`body_mass_g`) ? La **médiane** ?
3. Quelle est la masse moyenne **par espèce** (`species`) ?
4. Quelle est la masse moyenne **par espèce et par sexe** (croisé) ?
5. Crée une colonne `is_large` qui vaut `True` si `body_mass_g > 4500`. Quelle est la
   **proportion** de pingouins « larges » par espèce ?
6. Produis un graphique simple : un barchart de la masse moyenne par espèce.

<details>
<summary>🔒 <strong>Solution</strong> — clique pour révéler (après avoir cherché)</summary>

```python
# Q1
print(df.shape)
print(df.columns.tolist())
print(df.isna().sum())

# Q2
print(df["body_mass_g"].mean(), df["body_mass_g"].median())

# Q3
print(df.groupby("species")["body_mass_g"].mean().round(0))

# Q4
print(df.groupby(["species", "sex"])["body_mass_g"].mean().round(0))

# Q5
df["is_large"] = df["body_mass_g"] > 4500
print(df.groupby("species")["is_large"].mean().round(3))

# Q6
df.groupby("species")["body_mass_g"].mean().plot.bar(title="Masse moyenne par espèce — Palmer Penguins")
```

</details>

## Pour aller plus loin

- Doc officielle : https://pandas.pydata.org/docs/
- Notebook ZTM `introduction-to-pandas.ipynb` — fourni en complément par la
  formatrice si tu veux aller plus loin pendant la formation.
- Cheat sheet officiel : https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf
- Comparaison Pandas / Polars : https://pola-rs.github.io/polars/user-guide/migration/pandas/

## Vérification (checklist apprenant)

- [ ] J'ai chargé le dataset Penguins et reproduit les 6 questions de l'exercice.
- [ ] Je sais expliquer la différence entre **`.loc`** et **`.iloc`**.
- [ ] J'ai identifié au moins 1 colonne avec des valeurs manquantes dans Penguins.
- [ ] Je sais ce que fait un `groupby` (agrégation : un résultat par groupe).
- [ ] Je peux produire un graphique simple à partir d'un DataFrame en une ligne.