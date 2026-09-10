# Split temporel vs stratifié — Mini-cours

> Brief associé : M4-B1
> Durée : ~15 min
> Pré-requis : `train_test_split` vu en M1.

## Pourquoi cette techno ?

En M1 tu as utilisé `train_test_split` simple. Bike Sharing introduit
deux complications :

1. **Saisonnalité forte** : si tu shuffles aléatoirement, des observations
   de juillet 2012 se retrouvent dans le train et le test — le modèle
   « voit » le futur. C'est une **fuite temporelle**.
2. **Distribution déséquilibrée temporellement** : 2012 > 2011 en
   moyenne (croissance du service). Un split aléatoire mélange les 2
   années → ne reflète pas comment le modèle sera utilisé en prod
   (prédire l'avenir).

D'où l'usage de **`TimeSeriesSplit`** (folds ordonnés dans le temps) ou
de **`KFold` stratifié** sur une feature de saison.

## Concepts clés

### `TimeSeriesSplit`

Folds **ordonnés** : chaque fold de test est **après** son fold de train.
Pas de fuite future. Volume des folds croissant.

```python
from sklearn.model_selection import TimeSeriesSplit
splitter = TimeSeriesSplit(n_splits=5)

for fold_idx, (train_idx, test_idx) in enumerate(splitter.split(X, y)):
    # train_idx avant test_idx en temps
    ...
```

Schéma :

```
Fold 1 : [TRAIN: ----][TEST: --]
Fold 2 : [TRAIN: ------][TEST: --]
Fold 3 : [TRAIN: --------][TEST: --]
Fold 4 : [TRAIN: ----------][TEST: --]
Fold 5 : [TRAIN: ------------][TEST: --]
```

**Quand l'utiliser** :
- Données ordonnées temporellement (ce qui est notre cas)
- On veut **prédire le futur** à partir du passé
- Saisonnalité, drift, tendance

### `KFold` (random)

Folds aléatoires (par défaut `shuffle=False`, à mettre à `True` pour
mélanger).

```python
from sklearn.model_selection import KFold
splitter = KFold(n_splits=5, shuffle=True, random_state=42)
```

**Quand l'utiliser** :
- Pas d'ordre temporel
- Données i.i.d. (chaque échantillon indépendant)
- Tu veux maximiser le volume train à chaque fold

### `StratifiedKFold` (pour classification déséquilibrée)

Hors-sujet en M4-B1 (régression). À connaître pour la classification.

### `cross_val_score`

Helper qui automatise : applique le splitter, entraîne, mesure, retourne
les scores.

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=splitter, scoring="neg_mean_absolute_error")
print(f"MAE moyen : {-scores.mean():.2f} (±{scores.std():.2f})")
```

### Fuite de prétraitement : le préprocesseur va DANS le pipeline

Attention, **« fuite » désigne trois choses différentes** — ne les confonds pas :

| Type de fuite | Cause | Parade |
|---|---|---|
| **Temporelle** | `shuffle=True` sur série datée → le modèle voit le futur | `TimeSeriesSplit` (ci-dessus) |
| **De cible** | une feature contient (un bout de) la réponse — ici `casual_riders` + `registered_riders` **somment** `total_rentals` | les exclure de `X` |
| **De prétraitement** | un transformateur **qui apprend des paramètres** (`StandardScaler`, `SimpleImputer`, `TargetEncoder`) est `fit` sur **tout** `X` *avant* le split → il « voit » le test | l'enfermer dans le `Pipeline` du modèle |

La troisième est celle qui prolonge **M2-B1** : tu y as construit un `Pipeline`
scikit-learn sans modèle ni split, donc la fuite ne pouvait pas se produire. Ici
tu as les deux → la règle s'applique. **Ne passe jamais un `X` déjà transformé à
`cross_val_score`** ; passe le `Pipeline` complet, scikit-learn re-`fit` le
prétraitement sur les seuls folds d'entraînement :

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

# ✅ propre — le scaler est re-fitté sur chaque fold d'entraînement
pipe = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
scores = cross_val_score(pipe, X, y, cv=splitter, scoring="r2")

# ❌ fuite — le scaler a vu tout X (dont les folds de test) avant la CV
# X_scaled = StandardScaler().fit_transform(X)
# scores = cross_val_score(Ridge(), X_scaled, y, cv=splitter, scoring="r2")
```

> 💡 Sur Bike Sharing (~17k lignes), l'écart fuite/propre **avec un simple
> scaler** est minime : moyennes et écarts-types sont stables d'un fold à
> l'autre. Le danger devient réel avec **peu de données**, une **imputation**
> par moyenne/médiane, ou un **encodage supervisé**. On encapsule donc le
> prétraitement **par défaut** — pas seulement quand la fuite se voit.

## Décision pour Bike Sharing

| Critère | TimeSeriesSplit | KFold shuffled |
|---|---|---|
| Anti-fuite temporelle | ✅✅ | ❌ |
| Reflète l'usage prod (prédire futur) | ✅ | ❌ |
| Volume train à chaque fold | Croissant | Constant |
| Évaluation conservatrice | Plus | Moins |

**Recommandation** : **`TimeSeriesSplit(n_splits=5)`** pour Bike Sharing.
Justifie dans ton notebook : *« comme on veut prédire la demande
future, on adopte un split temporel pour éviter la fuite. »*

> 💡 Variante valable : `KFold` shuffled si tu argumentes que la
> saisonnalité étant **cyclique annuelle**, le modèle a besoin de voir
> au moins une fois chaque saison. **Justifie le choix** dans ton notebook.

## Exemple minimal

```python
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.linear_model import Ridge
import pandas as pd

df = pd.read_csv("data/bike_sharing.csv")
# (assume preprocessing fait, X et y prêts)

splitter = TimeSeriesSplit(n_splits=5)
model = Ridge(alpha=1.0)

scores = cross_val_score(model, X, y, cv=splitter,
                         scoring="neg_mean_absolute_error")
print(f"MAE : {-scores.mean():.2f} ± {scores.std():.2f}")
```

## Exercice guidé

Sur `bike_sharing.csv`, fais **deux** découpages et compare-les :

1. Un **split aléatoire** 80/20 (`train_test_split(..., random_state=42)`).
2. Un **split temporel** : train = tout sauf le dernier mois, test = dernier mois
   (trie par `date`/`hour` d'abord).

Pour chacun, entraîne le même modèle et regarde la MAE de test. **Question** :
lequel donne la MAE la plus optimiste, et lequel reflète mieux la réalité
(« prédire le futur à partir du passé ») ? Justifie en 2 phrases.

**Attendu** : tu constates que le split aléatoire **surestime** la performance
(fuite temporelle) et tu sais expliquer pourquoi le split temporel est plus
honnête pour une série datée comme Bike Sharing.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| `KFold(shuffle=True)` sur données temporelles | Fuite future, R² artificiellement haut |
| `StandardScaler().fit_transform(X)` avant la CV | Fuite de prétraitement → scores optimistes (mettre le scaler dans le `Pipeline`) |
| Garder `casual_riders` / `registered_riders` dans `X` | Fuite de cible → R² ~1.0 (ces colonnes somment la cible) |
| Oublier de **trier par date avant** TimeSeriesSplit | Folds incohérents |
| Comparer 2 modèles avec splitters différents | Comparaison invalide (règle d'or *comparabilité* violée) |
| `cross_val_score` avec `scoring="r2"` quand on veut MAE | Confusion — `scoring="neg_mean_absolute_error"` puis `-scores.mean()` |
| Pas de `random_state` sur KFold shuffled | Résultats non-reproductibles |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| R² ≈ 0.99 | Fuite de cible (`casual_riders`, `registered_riders`) |
| Les scores changent beaucoup entre deux exécutions | `random_state` absent |
| `TimeSeriesSplit` donne des résultats incohérents | Données non triées par date |
| Les scores CV sont meilleurs que le test final | Fuite ou surapprentissage |
| Tous les modèles donnent des résultats très proches | Split mal choisi ou features peu informatives |

## Pour aller plus loin

- **scikit-learn — *Cross-validation*** : <https://scikit-learn.org/stable/modules/cross_validation.html>
- **`TimeSeriesSplit`** : <https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html>

## Vérification

- [ ] J'ai choisi entre `TimeSeriesSplit` ou `KFold` shuffled
- [ ] J'ai **justifié** ce choix dans le notebook
- [ ] J'utilise le **même splitter** pour tous les modèles (comparabilité)
- [ ] J'ai trié les données par date avant `TimeSeriesSplit`
- [ ] Mon prétraitement (scaler) est **dans le `Pipeline`**, pas appliqué à `X` avant la CV
- [ ] J'ai **exclu** `casual_riders` / `registered_riders` de `X` (fuite de cible)
