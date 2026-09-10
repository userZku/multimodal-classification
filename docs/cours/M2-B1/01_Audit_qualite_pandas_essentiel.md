# Audit qualité avec pandas — Mini-cours

> Brief associé : M2-B1
> Durée de lecture + pratique : ~30 min
> Pré-requis : Python 3.11+, pandas, matplotlib/seaborn, environnement
> virtuel actif, dataset `german_credit_raw.csv` placé dans `data/`.

## Pourquoi cette techno ?

Avant de toucher au pipeline de préparation, il faut **savoir ce qu'on a
sous la main**. Un audit qualité bâclé = des hypothèses fausses qui se
propagent dans tout le pipeline, puis dans le modèle, puis en production.

Pour des données tabulaires « petites » (jusqu'à quelques millions de
lignes), **pandas suffit** : `info()`, `describe()`, `isna()`, `value_counts()`,
`crosstab()`, plus quelques visualisations seaborn. Pas besoin de Great
Expectations ou Pandera à ce stade — ces outils deviennent pertinents
quand on industrialise une vérification continue (M5+).

**Alternatives à connaître :**

| Approche | Quand l'utiliser ? |
|---|---|
| **pandas + seaborn** | Audit one-shot, dataset < 10 M lignes. Notre cas M2. |
| **ydata-profiling** (ex pandas-profiling) | Audit auto exhaustif, rapport HTML — utile en démarrage, mais à ne pas servir tel quel à un client (trop verbeux). |
| **Great Expectations** | Audit **continu**, intégré au pipeline de prod — utile en M5/M6 quand on déploie une chaîne data. Pas notre cas M2. |
| **Pandera** | Validation de schéma en code Python (type contrat). Très utile en M5, prématuré ici. |

## Concepts clés

- **Identifier les familles de variables** : avant tout le reste,
  `df.dtypes` donne le type de chaque colonne, et
  `df.select_dtypes(include="number")` / `select_dtypes(include="object")`
  séparent numériques et catégorielles. Trier les colonnes en familles
  (**numérique / catégorielle / ordinale / date / booléenne**) est le **geste
  préalable au `ColumnTransformer`** (mini-cours 03) : on ne traite pas une
  date comme un nombre, ni une ordinale comme une nominale.
- **`df.info()`** : aperçu rapide des types et du nombre de non-nuls par
  colonne. Première chose à regarder après `read_csv`.
- **`df.describe(include="all")`** : stats descriptives. Avec `include="all"`,
  tu obtiens aussi les modalités les plus fréquentes pour les catégorielles.
- **`df.isna().sum().sort_values(ascending=False)`** : nombre de manquants
  par colonne, triés. Si une colonne a > 30 % de manquants, c'est un signal
  fort (suppression ? imputation justifiée ? bug de collecte ?).
- **`df["col"].value_counts(normalize=True)`** : distribution des modalités
  d'une catégorielle. Détecte les **modalités rares** (< 1 % → souvent à
  fusionner ou exclure pour éviter les fuites en OneHot).
- **`pd.crosstab(df["target"], df["sensible"])`** : tableau croisé entre la
  cible et une variable potentiellement sensible. C'est le point de départ
  de l'audit éthique (cf. mini-cours 02).
- **Outlier visuel** : `sns.boxplot()` ou `sns.histplot()` pour une
  numérique. Un outlier qui colle à la réalité métier n'est **pas** une
  erreur — interroge avant de supprimer.

## Exemple minimal qui tourne

```python
# pandas==2.2.2, seaborn==0.13.2, matplotlib==3.9.2
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

df = pd.read_csv(Path("data/german_credit_raw.csv"))

# 1. Aperçu types + non-nuls
df.info()

# 2. Manquants par colonne (top 10)
print(df.isna().sum().sort_values(ascending=False).head(10))

# 3. Distribution de la cible
df["credit_risk"].value_counts(normalize=True)

# 4. Crosstab sensible
pd.crosstab(df["credit_risk"], df["foreign_worker"], normalize="columns")

# 5. Visualisation outliers sur une numérique
sns.boxplot(data=df, x="credit_amount")
plt.show()
```

À la sortie : tu sais le nombre exact de manquants, les modalités rares,
la distribution de la cible, et tu as un premier signal de biais éthique.

## Exercice guidé

Sur `german_credit_raw.csv`, produit **4 visualisations** :

1. Distribution de la cible `credit_risk` (countplot)
2. Distribution de `age` (histogramme, bins=20)
3. Boxplot de `credit_amount` (détection outliers)
4. Crosstab `credit_risk × personal_status_sex` (heatmap normalisée)

**Solution attendue** (squelette) :

```python
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

sns.countplot(data=df, x="credit_risk", ax=axes[0, 0])
sns.histplot(data=df, x="age", bins=20, ax=axes[0, 1])
sns.boxplot(data=df, x="credit_amount", ax=axes[1, 0])

ct = pd.crosstab(df["credit_risk"], df["personal_status_sex"], normalize="columns")
sns.heatmap(ct, annot=True, fmt=".2f", cmap="RdYlGn_r", ax=axes[1, 1])

plt.tight_layout()
```

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Comparer des proportions sans normaliser | Le déséquilibre cible (70/30) masque la vraie info |
| Supprimer les outliers sans regarder | Un crédit de 18 000 DM **n'est pas** une erreur ici |
| Ignorer les manquants implicites | `"unknown / no savings"` est un manquant codé, pas une vraie info |
| Faire `value_counts()` sans `dropna=False` | Tu loupes le compte des `NaN` |
| Imputer avant d'auditer | Tu effaces les patterns de manquants — fais l'audit AVANT |
| Ne regarder que numériques | Les catégorielles cachent souvent les biais |

**Symptôme → cause probable** :

| Symptôme observé | Cause probable |
|---|---|
| `df.info()` montre tout `object` | Le CSV a été chargé sans dtypes, types non inférés (pas grave ici, à fixer en M3) |
| `value_counts()` retourne 0 partout | Erreur de typo sur le nom de colonne |
| Heatmap crosstab toute uniforme | Tu n'as pas normalisé (`normalize="columns"`) |
| Boxplot affiche un range énorme avec 1 point | Outlier extrême — vérifie avant de supprimer (peut être un crédit pro légitime) |
| `seaborn` n'affiche rien dans le notebook | Manque `%matplotlib inline` (à mettre dans la 1ʳᵉ cellule) ou `plt.show()` |

## Pour aller plus loin

- **Doc officielle pandas** — [Visualisation](https://pandas.pydata.org/docs/user_guide/visualization.html)
  (pour les plots intégrés à pandas, alternative à seaborn)
- **Cheat sheet seaborn** — [seaborn.pydata.org/tutorial.html](https://seaborn.pydata.org/tutorial.html)
- **Aurélien Géron — *ML avec scikit-Learn*** (chapitre 2 *End-to-end ML
  project*, partie *Discover and visualize the data to gain insights*) —
  20 min de lecture, le passage de référence pour l'audit qualité.

## Vérification (checklist apprenant)

- [ ] J'ai chargé `german_credit_raw.csv` sans erreur
- [ ] Je connais le nombre exact de manquants par colonne
- [ ] J'ai produit au moins 4 visualisations interprétables
- [ ] J'ai écrit dans mon notebook un paragraphe « Quels problèmes de qualité
      ai-je identifiés ? » qui s'appuie sur ces visualisations
- [ ] Je peux expliquer en 1 phrase pourquoi `personal_status_sex` est un
      anti-pattern (variable composite)