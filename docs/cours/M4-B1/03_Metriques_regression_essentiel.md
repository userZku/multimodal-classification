# Métriques régression — MAE, RMSE, R² — Mini-cours

> Brief associé : M4-B1
> Durée : ~15 min
> Pré-requis : M1 (métriques classification déjà vues).

## Pourquoi cette techno ?

En M1 tu as utilisé F1 macro, ROC-AUC (classification). En M4-B1 c'est de
la **régression** — d'autres métriques.

**3 métriques essentielles** à connaître pour la régression :
1. **MAE** (Mean Absolute Error)
2. **RMSE** (Root Mean Squared Error)
3. **R²** (coefficient de détermination)

Chacune répond à une question différente. Le bon choix dépend du contexte
Mistral (tarification mobilité).

## Concepts clés

### MAE — Erreur moyenne absolue

```
MAE = (1/n) Σ |y_true - y_pred|
```

- **Unité** : même que la cible (locations de vélos)
- **Interprétation** : « en moyenne, je me trompe de X locations »
- **Robustesse** : peu sensible aux gros écarts (outliers)
- **Quand l'utiliser** : tu veux une métrique **lisible par un actuaire**
  (« on se trompe de 80 vélos par heure en moyenne »)

### RMSE — Erreur quadratique racine

```
RMSE = sqrt( (1/n) Σ (y_true - y_pred)² )
```

- **Unité** : même que la cible
- **Interprétation** : « erreur typique avec **pénalité** sur les grosses
  erreurs »
- **Robustesse** : **sensible aux outliers** (erreurs au carré)
- **Quand l'utiliser** : tu veux **éviter les grosses erreurs** (ex. un
  pic week-end mal prédit coûte beaucoup à Mistral)

### R² — Coefficient de détermination

```
R² = 1 - SS_residual / SS_total
```

- **Unité** : sans unité, dans [-∞, 1]
- **Interprétation** :
  - R² = 1 : prédiction parfaite
  - R² = 0 : aussi bon que prédire toujours la moyenne
  - R² < 0 : pire que prédire la moyenne (modèle vraiment mauvais)
- **Quand l'utiliser** : pour **comparer** entre datasets de tailles
  différentes, ou pour avoir un **score normalisé**

> ⚠️ **Ne mets pas R² sur le même plan que MAE/RMSE.** MAE et RMSE mesurent une
> **erreur** (en vélos — une grandeur concrète) ; R² mesure une **qualité
> d'explication** (la part de variance de la cible que le modèle capte, sans
> unité). Les deux se lisent **ensemble**, pas l'un à la place de l'autre.

## Quelle métrique pour Mistral ?

Inès Tabet veut tarifier la mobilité douce. Question : *« le coût d'une
sous-estimation est-il symétrique vs une surestimation ? »*

- Si **sous-estimation** = stocks insuffisants en station = clients perdus
  = coût fort
- Si **surestimation** = stocks excessifs = coût stockage modéré

→ Asymétrie possible. **MAE robuste**, **RMSE pénalise les grosses
sous-estimations**. Tu peux aussi calculer **MAPE** (`mean_absolute_percentage_error`)
pour une lecture en pourcentage (« on se trompe de 25 % en moyenne »).

**Recommandation Mistral** : **MAE + RMSE + R²** ensemble dans ton
tableau. Le MAE pour la lisibilité actuaire, le RMSE pour la pénalité
des pics, le R² pour la comparaison normalisée.

## Exemple minimal

```python
from sklearn.metrics import (
    mean_absolute_error,
    root_mean_squared_error,
    r2_score,
    mean_absolute_percentage_error,
)

y_true = [10, 20, 30, 40]
y_pred = [12, 18, 35, 38]

mae = mean_absolute_error(y_true, y_pred)   # → 3.0
rmse = root_mean_squared_error(y_true, y_pred)  # → 3.39 (légèrement > MAE)
r2 = r2_score(y_true, y_pred)               # → 0.94
mape = mean_absolute_percentage_error(y_true, y_pred)  # → 0.123 (12.3%)
```

## Exercice guidé

Sur `bike_sharing.csv` :

1. Calcule MAE, RMSE et R² d'un **modèle baseline** (qui prédit toujours la
   moyenne — `DummyRegressor(strategy="mean")`).
2. Fais de même pour un **RandomForest**. De combien la **MAE baisse**-t-elle ?
3. RMSE et MAE sont assez différentes sur ce jeu : qu'est-ce que ça t'apprend
   sur la présence de **grosses erreurs ponctuelles** (heures de pointe) ?
4. **Laquelle** des 3 métriques présenterais-tu à Inès (non technicienne) et
   pourquoi ?

**Attendu** : tu sais qu'une métrique ne suffit pas, et tu choisis la MAE pour
le dialogue métier (interprétable en « vélos/h ») tout en gardant RMSE/R² pour
le diagnostic technique.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| RMSE sur une cible en log → confusion d'unité | Reconvertis (exp) avant de communiquer |
| R² très haut (> 0.99) suspect | Probable fuite — vérifie tes features |
| R² négatif | Ton modèle est pire que la moyenne — vérifie ton split |
| Choisir 1 seule métrique | Tu rates une dimension — toujours **2-3 métriques** |
| MAPE sur cible avec valeurs nulles | Division par zéro — utilise `symmetric_mean_absolute_percentage_error` |
| `mean_squared_error(...)` puis `**0.5` à la main | Utilise `root_mean_squared_error` (sklearn 1.4+) |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| R² < 0 | Modèle pire que la moyenne, ou problème de split |
| RMSE ≫ MAE | Présence de grosses erreurs ponctuelles (la RMSE les pénalise) |
| MAE faible mais R² moyen | Faible variance de la cible — à interpréter avec les autres métriques |

> 📌 Dans le **benchmark M4-B1**, tous les modèles sont comparés sur
> **exactement les mêmes métriques** (mêmes folds, même calcul) — c'est ce qui
> rend la comparaison équitable.

## Pour aller plus loin

- **scikit-learn — *Regression metrics*** : <https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics>
- **Article *MAE vs RMSE*** : <https://medium.com/human-in-a-machine-world/mae-and-rmse-which-metric-is-better-e60ac3bde13d>

## Vérification

- [ ] Mon tableau comparatif a **MAE + RMSE + R²** au minimum
- [ ] J'ai interprété chaque métrique en **langage actuaire**
- [ ] Si R² > 0.95 → j'ai vérifié l'absence de fuite
- [ ] J'ai justifié le **choix de la métrique principale** pour la
      recommandation
