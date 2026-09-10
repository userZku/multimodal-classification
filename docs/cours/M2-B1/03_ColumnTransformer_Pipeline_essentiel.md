# ColumnTransformer + Pipeline scikit-learn — Mini-cours

> Brief associé : M2-B1
> Durée de lecture + pratique : ~30 min
> Pré-requis : audits qualité et éthique faits, listes de features
> approximativement décidées.

## Pourquoi cette techno ?

Un dataset tabulaire mixte (numériques + catégorielles ordonnées + catégorielles
nominales) demande des **transformations différentes par colonne**. Si tu
fais ça à la main en pandas, tu obtiens :

- du code fragile (un changement de schéma = bug en cascade)
- une fuite de données quasi-garantie (fit avant split)
- un pipeline impossible à persister / rejouer

Le **`ColumnTransformer`** (sklearn) résout ça en assemblant proprement
les sous-pipelines par groupe de colonnes. Combiné à un **`Pipeline`**
sklearn englobant, tu obtiens un **objet unique** :

- **persistable** (`joblib.dump`)
- **rejouable** sur de nouvelles données (`pipeline.transform(new_X)`)
- **inspectable** (chaque étape est nommée et accessible)

C'est le **standard scikit-learn** pour la préparation de données tabulaires.
On le retrouvera en M5 (intégration en service) et M6 (réentraînement).

**Alternatives à connaître :**

| Approche | Quand l'utiliser ? |
|---|---|
| **sklearn `Pipeline` + `ColumnTransformer`** | Standard pour tabulaire. **Notre cas M2.** |
| **`make_pipeline` + `make_column_transformer`** | Variante sans nommer les étapes — concis mais moins introspectable |
| **`category_encoders` lib** | Encodeurs avancés (Target, James-Stein, etc.) — utile au cas par cas, pas requis ici |
| **DataFrame transformations à la main** | Acceptable pour un POC ultra-rapide, mais **non livrable** en production |

## Concepts clés

- **`Pipeline([("step1", obj1), ("step2", obj2), ...])`** : enchaîne plusieurs
  étapes sklearn. Chaque étape est un nom + un transformer/estimator. La sortie
  d'une étape est l'entrée de la suivante.
- **`ColumnTransformer([("nom1", pipe1, cols1), ("nom2", pipe2, cols2), ...])`** :
  applique des pipelines **différents** à des **groupes de colonnes**
  différents. Concatène les sorties horizontalement.
- **`remainder="drop"`** vs `"passthrough"` : que faire des colonnes non
  référencées dans aucun groupe ? `drop` est plus sûr (force l'explicite).
  `passthrough` les garde telles quelles — utile pour les datasets très
  larges où on transforme juste quelques colonnes.
- **`OneHotEncoder(handle_unknown="ignore")`** : si une modalité inconnue
  arrive au `transform`, elle est encodée en zéro partout (vs lever une
  exception). **Toujours mettre `ignore`** pour la robustesse en production.
- **`OrdinalEncoder(categories=[...])`** : encode des catégorielles dont
  l'ordre est sémantiquement significatif (ex. `savings_account` : `< 100 DM`
  < `100-500 DM` < `500-1000 DM` < ...). Le paramètre `categories` impose
  l'ordre.
- **`Pipeline` global** : tu peux englober un `ColumnTransformer` dans un
  `Pipeline` plus large qui ajoute un modèle ou d'autres étapes. En M2 on
  s'arrête au `ColumnTransformer` (pas de modèle ici, on prépare).
- **`pipeline.fit_transform(X)`** vs `fit(X).transform(X)` : équivalent, mais
  `fit_transform` est optimisé. En production tu fais `fit` une fois sur le
  train, puis `transform` sur tous les nouveaux lots.

## Vue mentale : ce que fait le `ColumnTransformer`

Beaucoup d'apprenants peinent à visualiser ce qui se passe. L'image à
retenir : **chaque famille de colonnes passe dans _son propre_ sous-pipeline**,
puis tout est recollé horizontalement en **une seule matrice** :

```
                       ┌──────────────────────┐
  colonnes num ──────► │  impute + scale      │──┐
                       └──────────────────────┘  │
                       ┌──────────────────────┐  │   ColumnTransformer
  colonnes ord ──────► │  impute + ordinal    │──┼──► (concat horizontal) ──► matrice
                       └──────────────────────┘  │                            finale
                       ┌──────────────────────┐  │
  colonnes cat ──────► │  impute + one-hot    │──┘
                       └──────────────────────┘
```

Retiens : **1 branche = 1 famille de colonnes = 1 traitement**. Le
`ColumnTransformer` ne fait que **router** chaque colonne vers le bon
sous-pipeline, puis **recoller** les sorties côte à côte.

## Exemple minimal qui tourne

```python
# scikit-learn==1.5.1
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

df = pd.read_csv("data/german_credit_raw.csv")
X = df.drop(columns=["credit_risk"])
y = df["credit_risk"]

# 1. Sous-pipeline numérique
numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

# 2. Sous-pipeline catégoriel ordinal (ordre imposé !)
savings_order = ["< 100 DM", "100-500 DM", "500-1000 DM",
                 ">= 1000 DM", "unknown / no savings"]
ordinal_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("ordinal", OrdinalEncoder(categories=[savings_order])),
])

# 3. Sous-pipeline catégoriel one-hot
categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

# 4. Assemblage avec ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_pipeline, ["duration_months", "credit_amount", "age"]),
        ("ord", ordinal_pipeline, ["savings_account"]),
        ("cat", categorical_pipeline, ["purpose", "housing", "telephone"]),
    ],
    remainder="drop",
    verbose_feature_names_out=False,
)

# 5. Fit + transform
X_prep = preprocessor.fit_transform(X)
print(f"Shape originale : {X.shape}")
print(f"Shape transformée : {X_prep.shape}")

# 6. Persistance
joblib.dump(preprocessor, "src/pipeline.joblib", compress=3)

# 7. Rechargement et test
loaded = joblib.load("src/pipeline.joblib")
X_again = loaded.transform(X.head(5))
print(f"Reload OK, shape (5 lignes) : {X_again.shape}")
```

## Exercice guidé

Construis le `ColumnTransformer` complet pour le dataset Eckmühl, avec **tes
choix** depuis l'audit. Persiste-le et **recharge-le dans un script séparé**
pour vérifier que la sérialisation est propre.

**Squelette attendu** :

```python
# src/preprocess.py
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

NUMERIC_FEATURES = [...]    # tes choix
ORDINAL_FEATURES = {        # tes choix, avec l'ordre des modalités
    "savings_account": [...],
    # ...
}
CATEGORICAL_FEATURES = [...]  # tes choix

def build_preprocessor():
    # ... (cf. exemple minimal ci-dessus)
    return ColumnTransformer(...)
```

```python
# test_reload.py (à lancer dans un terminal séparé)
import joblib, pandas as pd

pipe = joblib.load("src/pipeline.joblib")
df = pd.read_csv("data/german_credit_raw.csv").drop(columns=["credit_risk"])
out = pipe.transform(df.head(10))
assert out.shape[0] == 10, "Reload broken"
print(f"OK — output shape {out.shape}")
```

## Et si une nouvelle variable arrive ? (geste « adapter »)

C'est tout l'intérêt d'un `ColumnTransformer` : **tu n'as pas à tout réécrire**.
Quand une colonne imprévue arrive (cf. tâche 5 bis, `customer_segment`), la
démarche tient en 3 questions :

1. **Quelle est sa nature ?** Numérique → `NUMERIC_FEATURES`. Catégorielle
   **ordonnée** (des tiers, des niveaux) → `ORDINAL_FEATURES` avec l'ordre
   explicite. Catégorielle **non ordonnée** → `CATEGORICAL_FEATURES` (OneHot).
2. **À quel branch je la rattache ?** Tu l'ajoutes à la bonne liste : elle
   hérite automatiquement de l'imputation + l'encodage de ce branch. Ses
   manquants sont gérés par l'imputer du branch (pas besoin d'y penser deux fois).
3. **Combien de colonnes en sortie ?** Ordinal → **+1 colonne**. OneHot →
   **+1 colonne par modalité**. Re-`fit` et vérifie la nouvelle shape.

> ⚠️ Le piège : mettre une variable **ordonnée** (`basic < plus < premium <
> private`) en OneHot → tu **perds l'ordre**. Si tu choisis quand même OneHot,
> assume-le et explique pourquoi (parfois l'ordre n'est pas pertinent pour la
> cible — mais c'est un choix à argumenter, pas un défaut).

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Fit sur tout le dataset avant un split | Fuite de données — en M2 on fitte sur tout volontairement (pas de modèle ici), mais à savoir pour M4+ |
| `OneHotEncoder` sans `handle_unknown="ignore"` | Crash si une modalité inconnue arrive en production |
| `OrdinalEncoder` sans `categories=[...]` | Ordre fixé par sklearn alphabétiquement (souvent faux pour la sémantique) |
| `remainder="passthrough"` par défaut | Tu gardes des colonnes que tu n'as pas voulues — sois explicite |
| `sparse_output=True` (défaut OneHot) + matplotlib | Erreurs cryptiques en visualisation post-transform |
| Pipeline non sérialisable | Tu utilises une lambda dans une étape → joblib ne peut pas pickler |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| `ValueError: A given column is not a column of the dataframe` | Faute de frappe dans le nom d'une feature, ou colonne pas dans le DataFrame d'entrée |
| Shape de sortie qui explose (5000 colonnes pour 20 features) | Une catégorielle a une cardinalité énorme (ex. `purpose` avec 1000 modalités) — à fusionner ou exclure |
| `transform` plante après `joblib.load` | Versions sklearn différentes entre `fit` et `load` (fige tes versions dans `requirements.txt`) |
| Shape de sortie différente entre `fit_transform` et `transform` | Tu as une étape avec un état caché qui n'est pas reproductible — vérifie tes random_state |
| `OrdinalEncoder` met `-1` partout | Modalité non listée dans `categories` — ajoute-la ou passe `handle_unknown="use_encoded_value"` |

## Pour aller plus loin

- **Doc officielle sklearn** — [ColumnTransformer for heterogeneous data](https://scikit-learn.org/stable/auto_examples/compose/plot_column_transformer_mixed_types.html)
  (exemple officiel pertinent)
- **Doc officielle sklearn** — [Pipeline visualisation](https://scikit-learn.org/stable/modules/compose.html#visualizing-composite-estimators)
  (`set_config(display='diagram')` pour voir le pipeline graphiquement dans
  Jupyter)
- **Aurélien Géron — *ML avec scikit-Learn*** (chapitre 2 *Prepare the data
  for ML algorithms*) — référence francophone exhaustive

## Vérification (checklist apprenant)

- [ ] J'ai construit un `ColumnTransformer` avec au moins 2 branches
      (numérique + catégorielle)
- [ ] J'ai utilisé `handle_unknown="ignore"` sur tous mes `OneHotEncoder`
- [ ] Si j'ai des ordinales, j'ai passé `categories=[...]` avec le bon ordre
- [ ] J'ai persisté avec `joblib.dump(pipe, ..., compress=3)`
- [ ] J'ai **rechargé** mon pipeline dans un script séparé et vérifié que
      `transform` retourne bien la bonne shape
- [ ] Je peux expliquer en 1 phrase la différence entre `fit_transform`
      et `fit().transform()`
