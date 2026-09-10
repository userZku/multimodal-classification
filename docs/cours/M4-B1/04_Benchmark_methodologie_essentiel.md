# Méthodologie benchmark — Mini-cours

> Brief associé : M4-B1
> Durée : ~25 min
> Pré-requis : M1 (la règle d'or *comparabilité* a été plantée là).

## Pourquoi cette techno ?

Comparer 3 modèles, c'est plus dur qu'il n'y paraît. Un benchmark **mal
mené** = des conclusions **fausses** transmises à Inès Tabet, qui va
prendre des décisions tarifaires sur du sable.

**La règle d'or absolue** :

> **Comparabilité** : deux modèles ne se comparent que sur le **même
> split**, les **mêmes métriques**, le **même prétraitement**, les
> **mêmes hyperparamètres par défaut** (sauf variante annoncée).

Sinon : tu n'as pas comparé 2 modèles, tu as comparé 2 expériences
différentes.

## Concepts clés

### Les 5 familles de critères à mesurer

Au-delà de la **précision** (MAE, RMSE, R²), pour un benchmark **utile à
un décideur** — **5 familles de critères** (la précision se décline en 3
métriques, donc ton tableau aura ~7 colonnes) :

1. **Précision** : MAE, RMSE, R²
2. **Vitesse d'entraînement** : `time.perf_counter()` autour de `model.fit(...)`
3. **Vitesse d'inférence** : temps de `model.predict(...)` sur 1 k échantillons
4. **Mémoire** : `joblib.dump(model, ...).st_size` ou via `pympler`
5. **Explicabilité** : note qualitative 1-3 (1=boîte noire, 3=très explicable)

Sans ces 5 familles de critères, ton tableau est unidimensionnel et inutile à
la prise de décision.

### Les 3 familles à benchmarker pour M4-B1

Couvre **3 sensibilités différentes** :

- **Famille A — Linéaire** : `Ridge` (variante régularisée de
  LinearRegression). Rapide, explicable, capte mal les non-linéarités.
- **Famille B — Arbre / Forêt** : `RandomForestRegressor`. Capte
  non-linéarités, moyennement explicable, plus lent.
- **Famille C — Boosting** : `HistGradientBoostingRegressor`. Souvent
  meilleur sur tabulaire, rapide à entraîner.

**Pas besoin de tuner finement** chaque famille. Garde **hyperparamètres
par défaut** + 1 variante raisonnable.

### Boucle benchmark canonique

```python
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
import time

splitter = TimeSeriesSplit(n_splits=5)

models = {
    "Ridge": Ridge(alpha=1.0, random_state=42),
    "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    "HistGBR": HistGradientBoostingRegressor(random_state=42),
}

results = []
for name, model in models.items():
    # MAE en CV
    mae_scores = -cross_val_score(model, X, y, cv=splitter,
                                  scoring="neg_mean_absolute_error")
    # Temps train : on entraîne une fois sur TOUT X juste pour CHRONOMÉTRER
    # (≠ la CV ci-dessus qui, elle, sert à MESURER la performance sans fuite).
    # Ici on ne lit aucun score de ce fit — seulement sa durée.
    t0 = time.perf_counter()
    model.fit(X, y)
    fit_time = time.perf_counter() - t0
    # Temps inférence (sur 1000 échantillons)
    t0 = time.perf_counter()
    _ = model.predict(X.iloc[:1000])
    pred_time_ms = (time.perf_counter() - t0) * 1000

    results.append({
        "model": name,
        "mae_mean": mae_scores.mean(),
        "mae_std": mae_scores.std(),
        "fit_time_sec": fit_time,
        "pred_time_ms_per_1k": pred_time_ms,
    })

import pandas as pd
print(pd.DataFrame(results).round(2))
```

### Garde-fous anti-erreur

1. **Toujours `random_state=42`** sur chaque modèle (cohérence)
2. **Toujours la même cible** (pas de log-transform pour 1 modèle seul)
3. **Toujours le même `X`** (même prétraitement)
4. **Toujours le même splitter** (variable réutilisée, pas redéfinie)

## Exemple minimal — à quoi ressemble un tableau comparatif

> ⚠️ **Chiffres purement illustratifs, sur un AUTRE cas** (prédiction de
> consommation) — surtout **pas** ceux de Bike Sharing. Tes résultats sur le
> dataset du brief seront différents (attends-toi à un R² autour de **0.85**,
> pas 0.94). Ce tableau montre le **format** et le **raisonnement**, pas des
> cibles à atteindre.

| Modèle | MAE | RMSE | R² | Temps train (s) | Latence (ms/1k) | Explicabilité | Mémoire (Mo) |
|---|---|---|---|---|---|---|---|
| **baseline-v0** | 105 | 139 | 0.39 | 0.1 | 1 | 3 (très) | 0.5 |
| Ridge (régularisé) | 102 | 136 | 0.41 | 0.2 | 1 | 3 | 0.5 |
| RandomForest | 35 | 52 | 0.92 | 8.5 | 12 | 2 (SHAP requis) | 50 |
| **HistGradientBoosting** ★ | **32** | **48** | **0.94** | **2.1** | **3** | 2 (SHAP requis) | 8 |

Lecture du tableau : ici HGB améliore nettement le MAE vs la baseline, au prix
d'une explicabilité moindre (que SHAP peut combler). Le raisonnement à
reproduire : **croiser précision, vitesse, explicabilité et mémoire**, pas
seulement regarder le R². La recommandation d'un tel tableau, c'est le modèle
qui optimise le **compromis**, pas le plus précis dans l'absolu.

## Exercice guidé

Reproduis ce tableau sur **tes** modèles (au moins baseline + RandomForest +
HistGradientBoosting) :

1. Pour chaque modèle, mesure le **temps d'entraînement** (`time.perf_counter()`
   autour du `.fit()`) et ajoute-le en colonne.
2. Ajoute une colonne **explicabilité** (note subjective 1-3) et une ligne de
   commentaire métier.
3. Réponds par écrit : *le modèle le plus précis est-il le plus rapide ?* Quel
   **arbitrage** proposes-tu à Inès (précision vs temps vs explicabilité) ?

**Attendu** : un tableau comparatif **chiffré sur plusieurs axes** (pas juste la
MAE) + une recommandation justifiée — c'est le cœur de la compétence C4.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Comparer 2 modèles sur 2 splits différents | Comparaison invalide |
| Tuner finement 1 modèle, pas les autres | Comparaison biaisée — Ridge sans tuning vs HGB avec Optuna = pas fair |
| Mesurer le temps train sur un fold partiel | Temps non comparables |
| Mesurer la latence sur 1 échantillon | Variance énorme — mesure sur ≥ 100 échantillons |
| Pas d'écart-type sur les scores CV | Le R² 0.92 ± 0.01 est très différent de 0.92 ± 0.15 |
| `n_jobs=-1` partout sans le préciser | Comparaison vitesse biaisée — fixe `n_jobs` partout |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| Un modèle est meilleur sur **tous** les critères | Vérifier que la comparaison est bien équitable (mêmes folds/features) |
| Le temps d'entraînement varie énormément | `n_jobs` différents, ou mesure sur des tailles différentes |
| Les écarts-types CV sont élevés | Modèle instable ou folds hétérogènes |
| Deux modèles donnent **exactement** les mêmes scores | Mauvaise instanciation (même modèle réutilisé deux fois) |

## Pour aller plus loin

- **scikit-learn — *Comparing different scaler*** : <https://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html>
  (méthodologie de comparaison fair sur plusieurs preprocessings)
- **`HistGradientBoostingRegressor` doc** : <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html>
  (souvent le meilleur compromis vitesse/précision sur tabulaire)
- **`ressources-publiques/cheatsheet_algos_ML_FR.pdf`** — aide-mémoire de
  sélection par type de problème. Les 3 familles de ce benchmark y sont
  repérées **« TRIO M4B1 »** (Ridge · Random Forest · HistGradientBoosting),
  avec forces/limites de chacune. Utile pour comprendre **pourquoi ce trio**
  (baseline interprétable → ensemble robuste → boosting performant, qui balaient
  le spectre biais-variance) et situer les autres familles que tu croiseras plus tard.

## Vérification

- [ ] J'ai benchmarké **3 familles différentes** (pas 3 variantes d'une seule)
- [ ] **Mêmes folds**, **mêmes métriques**, **même prétraitement** pour tous
- [ ] J'ai mesuré les **5 familles de critères** : précision (MAE/RMSE/R²) + temps train + temps inférence + mémoire + explicabilité
- [ ] Mon tableau a un écart-type sur les métriques CV
- [ ] Mon verdict est **chiffré** (X % d'amélioration sur Y métrique)
