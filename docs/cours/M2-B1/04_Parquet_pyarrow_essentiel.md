# Parquet avec pyarrow — Mini-cours

> Brief associé : M2-B1
> Durée de lecture + pratique : ~20 min
> Pré-requis : DataFrame propre en main, pyarrow installé.

## Pourquoi cette techno ?

Le CSV est universel mais **dégueulasse en production** :

- Types perdus à chaque rechargement (`int` devient `float` à cause de NaN)
- Pas de schéma, pas de compression native
- Lecture ligne par ligne → lent sur gros volumes
- Encoding fragile (UTF-8 ? Latin-1 ? Espaces avant ?)

**Parquet** (format colonnaire d'Apache) résout ça :

- **Types préservés** (int, float, string, datetime, boolean, listes…)
- **Compression native** (snappy par défaut, x3-x5 sur du tabulaire)
- **Lecture colonnaire** : ne charger que les colonnes utiles → rapide
- **Métadonnées dans le fichier** (schéma, stats par colonne)
- **Standard de fait** dans l'écosystème data (Spark, DuckDB, Polars, BigQuery…)

Pour des données **livrées en production**, c'est le format standard. En M2,
on l'introduit. En M3, on l'utilisera systématiquement. En M5/M6, c'est la
norme.

**Alternatives à connaître :**

| Format | Quand l'utiliser ? |
|---|---|
| **CSV** | Échange humain-lisible, debug, datasets < 100 Ko. Ne **pas** utiliser en prod. |
| **Parquet** | Standard tabulaire de prod. **Notre cas M2.** |
| **JSON / JSON-Lines** | Données semi-structurées, logs, API. Pas du tabulaire pur. |
| **Feather (Arrow IPC)** | Échange ultra-rapide intra-Python/R, pas pour archivage. |
| **HDF5** | Datasets scientifiques très lourds avec hiérarchie. Pas notre besoin. |
| **DuckDB / SQLite** | Quand tu veux **interroger** sans charger en mémoire. Bonus pour M3+. |

## Concepts clés

- **`pd.DataFrame.to_parquet(path, engine="pyarrow", compression="snappy")`** :
  écriture. `snappy` est le bon défaut (rapide + bonne compression). `gzip`
  compresse plus mais lit plus lentement.
- **`pd.read_parquet(path, engine="pyarrow")`** : lecture. Tu peux passer
  `columns=["a", "b"]` pour ne lire qu'un sous-ensemble (le gain en mémoire
  est réel sur gros datasets).
- **Format colonnaire** : Parquet stocke par colonne, pas par ligne. Lire
  3 colonnes sur 100 est ~30x plus rapide qu'avec CSV.
- **Schéma intégré** : le `.parquet` contient les types — pas besoin de les
  redéclarer à la lecture.
- **Partitionnement** (avancé) : `df.to_parquet(path, partition_cols=["year"])`
  crée une arborescence `year=2024/`, `year=2025/`. Utile pour du
  data lake. Pas notre besoin M2.

## Exemple minimal qui tourne

```python
# pandas==2.2.2, pyarrow==17.0.0
from pathlib import Path
import pandas as pd

df = pd.read_csv(Path("data/german_credit_raw.csv"))

# Imputer / nettoyer ce que tu veux livrer "propre"
# (en M2, c'est ton dataset post-imputation par exemple)
df_clean = df.copy()
# ... tes transformations en pandas pur (avant Pipeline sklearn) ...

# Écriture Parquet
clean_path = Path("data/german_credit_clean.parquet")
df_clean.to_parquet(clean_path, engine="pyarrow", compression="snappy")

# Vérification : relecture + comparaison de taille
df_back = pd.read_parquet(clean_path, engine="pyarrow")
assert df_clean.shape == df_back.shape
assert (df_clean.dtypes == df_back.dtypes).all(), "Types non préservés !"

csv_size = Path("data/german_credit_raw.csv").stat().st_size / 1024
pq_size = clean_path.stat().st_size / 1024
print(f"CSV  : {csv_size:.1f} Ko")
print(f"PQ   : {pq_size:.1f} Ko")
print(f"Ratio compression : {csv_size / pq_size:.1f}x")
```

Sur German Credit, tu obtiens typiquement **CSV ~80 Ko → Parquet ~25 Ko**
(ratio ~3x). Sur des volumes plus gros (M3), tu verras 10-20x.

> 💡 **« Pourquoi s'embêter avec pyarrow pour un CSV de 80 Ko ? »** En M2, le
> gain de performance est **invisible** — c'est normal, le dataset est minuscule.
> On apprend Parquet **maintenant** parce qu'il devient le format **standard dès
> M3**, et la norme en M5/M6. Tu installes le réflexe **avant** d'en avoir besoin
> sur de gros volumes, pas le jour où ça coince.

## Exercice guidé

1. Sauvegarde ton dataset propre (post-imputation ou tel que post-EDA, à toi)
   en Parquet snappy
2. Vérifie en relecture que les **types** sont préservés (pas de
   `category → object` ou `int → float`)
3. Compare la taille fichier avec le CSV original

**Solution attendue** : un script de 10 lignes max, avec un `assert` sur
les dtypes et un print du ratio de compression.

```python
from pathlib import Path
import pandas as pd

CSV = Path("data/german_credit_raw.csv")
PQ  = Path("data/german_credit_clean.parquet")

df = pd.read_csv(CSV)
# (insérer ici ton nettoyage minimal — ou laisser tel quel pour M2)
df.to_parquet(PQ, engine="pyarrow", compression="snappy")

df_back = pd.read_parquet(PQ)
assert (df.dtypes == df_back.dtypes).all(), \
    f"Types divergents : {df.dtypes[df.dtypes != df_back.dtypes].to_dict()}"

ratio = CSV.stat().st_size / PQ.stat().st_size
print(f"OK — Parquet {PQ.stat().st_size / 1024:.1f} Ko ({ratio:.1f}x plus compact)")
```

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Oublier `engine="pyarrow"` | Si `fastparquet` est aussi installé, comportement non déterministe entre machines |
| Sauvegarder avec compression différente entre dev et prod | Performance variable, debug compliqué |
| Mélanger `int` et `NaN` dans une colonne | Pandas convertit en `float64` — les `int` sont perdus à la lecture. Utilise `Int64` (pandas nullable) si tu veux conserver |
| Stocker une colonne avec des types mixtes | `to_parquet` crash. Casts explicites avant écriture |
| Compter sur Parquet pour du human-debug | Tu **ne peux pas** ouvrir un Parquet dans Excel. Garde un CSV en parallèle pour debug si besoin |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| `ImportError: pyarrow` | `pip install pyarrow` manquant |
| `ArrowInvalid: Could not convert ... with type` | Une colonne a des types mixtes (souvent `str` et `int` mélangés) — caste avant écriture |
| Fichier Parquet 2x plus gros qu'attendu | Tu as utilisé `compression="none"` ou très peu de répétition dans tes données (Snappy compresse bien les colonnes catégorielles répétées) |
| `dtypes` différents après reload | Tu avais un dtype custom (`category`, `Int64`) que Parquet a sérialisé différemment — vérifie au cas par cas, parfois ok parfois pas |
| Lecture plus lente que CSV | Tu lis toutes les colonnes alors que tu n'en veux que 3 — utilise `columns=[...]` |

## Pour aller plus loin

- **Doc officielle pandas — Parquet** : [pandas.read_parquet](https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html)
- **Doc officielle pyarrow** : [Parquet format](https://arrow.apache.org/docs/python/parquet.html)
- **Comparatif Parquet vs CSV vs Feather** : [Comparing Pandas Dataframes…](https://towardsdatascience.com/the-best-format-to-save-pandas-data-414dca023e0d)
  (article daté mais toujours d'actualité)
- Pour aller bien plus loin : **Apache Arrow** (le format en mémoire derrière
  Parquet), **DuckDB** pour requêter du Parquet en SQL sans tout charger.

## Vérification (checklist apprenant)

- [ ] J'ai écrit mon dataset propre en `data/german_credit_clean.parquet`
- [ ] J'ai relu et vérifié que les **types** sont préservés
- [ ] J'ai noté dans mon notebook le **ratio de compression** CSV → Parquet
- [ ] Je peux expliquer en 1 phrase **pourquoi** Parquet > CSV en production
- [ ] J'ai compris que Parquet n'est **pas** un format humainement lisible
      (pas d'ouverture Excel)