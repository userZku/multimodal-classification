# Disparate impact (règle des 4/5) — Mini-cours

> Brief associé : M2-B1
> Durée de lecture + pratique : ~25 min
> Pré-requis : audit qualité fait (mini-cours 01), variables sensibles
> identifiées dans ton dataset.

## Pourquoi cette techno ?

**Le disparate impact (DI)** est une mesure standard pour détecter si un
résultat (ici, recevoir le crédit) est **statistiquement défavorable** à
un groupe protégé (genre, origine, âge, etc.).

C'est l'outil le plus simple pour faire un **premier diagnostic éthique**
d'un dataset ou d'un modèle — bien avant de parler de mitigation. Pas besoin
de framework lourd : un calcul Pandas en 3 lignes suffit pour le diagnostic
de niveau M2.

**Histoire** : la règle des 4/5 vient de l'**EEOC américaine** (Equal
Employment Opportunity Commission, 1978) pour détecter la discrimination
à l'embauche. Elle dit : si le taux de sélection du groupe minoritaire
est inférieur à 80 % de celui du groupe majoritaire, il y a un signal
de discrimination indirecte à investiguer.

**Alternatives à connaître :**

| Approche | Quand l'utiliser ? |
|---|---|
| **Calcul pandas direct** | Diagnostic M2, 1 ou 2 variables. Notre cas. |
| **Fairlearn (`MetricFrame`)** | Plusieurs variables + plusieurs métriques d'un coup. Bonus M2, central en M7. |
| **AIF360 (IBM)** | Framework complet (détection + mitigation). Trop pour M2, à reconsidérer en M7. |
| **What-If Tool (Google)** | UI interactive pour exploration éthique. Démo, pas industrialisable ici. |

## Concepts clés

- **Groupe minoritaire / majoritaire** : pour une variable sensible binaire
  (ex. `sex`), le groupe minoritaire est celui dont le **taux de sélection**
  (= % d'outcome positif) est le plus bas.
- **Outcome positif** : c'est **l'événement favorable** pour la personne.
  Pour un crédit : `good_credit` (le crédit est accordé).
- **Taux de sélection (selection rate)** : `P(outcome_positif | groupe)`.
  En Pandas : `df.groupby(groupe)["outcome"].apply(lambda x: (x == positif).mean())`.
- **Disparate impact (DI)** :
  ```
  DI = taux_sélection_groupe_minoritaire / taux_sélection_groupe_majoritaire
  ```
- **Règle des 4/5** :
  - **DI < 0.8** → signal de **discrimination indirecte** (groupe minoritaire
    pénalisé)
  - **DI > 1.25** → signal **inversé** (groupe majoritaire pénalisé — souvent
    suspect aussi, à investiguer)
  - **0.8 ≤ DI ≤ 1.25** → pas de signal au sens de la règle 4/5 (mais ça
    ne veut pas dire qu'il n'y a pas de biais — la règle est un seuil
    grossier, à compléter par d'autres mesures en M7)

> ⚠️ **Le DI est calculé ici sur des données _historiques_.** Il ne prouve
> **pas** qu'un futur modèle sera discriminant : il indique seulement que les
> données reflètent **déjà** des disparités qu'il faudra **surveiller**.
> Confondre « biais dans les données » et « modèle discriminant » est l'erreur
> la plus fréquente à ce stade. En M2 on **alerte**, on ne **conclut** pas.

## Exemple minimal qui tourne

```python
# pandas==2.2.2
import pandas as pd

df = pd.read_csv("data/german_credit_raw.csv")

# DI sur foreign_worker (oui = majoritaire ~96%, non = minoritaire ~4%)
positif = "good_credit"
groupe = "foreign_worker"

selection_rate = df.groupby(groupe)["credit_risk"].apply(
    lambda x: (x == positif).mean()
)
print(selection_rate)
# foreign_worker
# no     0.892   ← non-étrangers
# yes    0.693   ← étrangers (minoritaire en termes de bon score)

# Le groupe minoritaire est celui avec le SR le plus bas
sr_min = selection_rate.min()
sr_max = selection_rate.max()
di = sr_min / sr_max
print(f"DI = {di:.3f}")  # → 0.777
print(f"Verdict 4/5 : {'⚠️ signal (DI < 0.8)' if di < 0.8 else '✅ OK'}")
```

Verdict : **DI = 0.777 < 0.80** → les travailleurs étrangers sont environ
**22 % moins susceptibles** d'être classés `good_credit`. À documenter,
à alerter le DPO. Pas à mitiger ici (c'est M7).

## Exercice guidé

Calcule le DI sur **2 variables sensibles** de `german_credit_raw.csv` :

1. `foreign_worker` (binaire facile)
2. `personal_status_sex` (multi-modalités — on agrège)

Pour `personal_status_sex` qui a 5 modalités, agrège d'abord en 2 groupes
binaires (`female_*` vs `male_*`) :

```python
df["sex_binary"] = df["personal_status_sex"].apply(
    lambda s: "female" if s.startswith("female") else "male"
)

selection_rate = df.groupby("sex_binary")["credit_risk"].apply(
    lambda x: (x == "good_credit").mean()
)
di = selection_rate.min() / selection_rate.max()
print(f"DI sex = {di:.3f}")
```

**Solution attendue** (verdicts approximatifs) :

- `foreign_worker` : DI ~0.78 → **signal**
- `sex_binary` : DI ~0.90 → **pas de signal au sens 4/5** (mais la
  composition `personal_status_sex` mélange genre et statut civil — bug de
  conception à signaler dans l'audit éthique)

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Définir le "positif" du mauvais côté | DI inversé, verdict opposé à la réalité |
| Calculer DI sans s'assurer du sens métier | "Étrangers ont moins bon score" ≠ "le modèle discrimine" → corrélation ≠ causalité |
| Comparer 2 modalités sans en agréger | DI sur 5 modalités pris isolément → bruit, pas de signal stable |
| Confondre DI et statistical parity difference | DI = ratio (sans unité), SPD = différence (en points) — choisis ton outil |
| Sauter la mitigation alors que c'est M7 | En M2, on **documente** et **alerte**, on ne **mitige pas** |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| DI > 5 ou < 0.05 | Une des cellules de la crosstab est très petite (peu d'observations dans un groupe) — DI peu fiable, à signaler |
| DI = 1.0 pile | Trop beau pour être vrai : vérifie que tu n'as pas calculé sur le mauvais groupage |
| Erreur `'good_credit'` non trouvé | Tu lis la cible avant mapping — utilise la chaîne brute du CSV ou la version mappée, mais sois cohérent |
| `selection_rate.min() / selection_rate.max()` donne 0 | Un groupe a 0 % de sélection — DI = 0, indéfini : à signaler comme bug de données ou échantillon trop petit |
| Verdict 4/5 sur 1 sample = comportement modèle | Le DI est sur le **dataset**, pas sur le modèle. C'est un audit de **données**, pas de prédictions (qui viendrait après entraînement) |

## Pour aller plus loin

- **EEOC — 4/5 rule** : [Employment Tests & Selection Procedures](https://www.eeoc.gov/laws/guidance/employment-tests-and-selection-procedures)
  (source US de la règle des 4/5)
- **Fairlearn** : [User Guide — Common fairness metrics](https://fairlearn.org/main/user_guide/assessment/common_fairness_metrics.html)
  (équivalents Fairlearn du calcul Pandas)
- **Mitchell et al. — *Model Cards for Model Reporting*** (2019) — préfigure
  M7, en lien avec datasheet Gebru
- **CNIL — Recommandations IA et données personnelles** (2024) — cadre
  réglementaire français/européen
- **Article de référence** : Barocas, Hardt, Narayanan — [*Fairness and Machine
  Learning*](https://fairmlbook.org/) (livre gratuit en ligne, chap. 1 et 2)

## Vérification (checklist apprenant)

- [ ] J'ai calculé le DI sur au moins 2 variables sensibles du dataset
- [ ] J'ai correctement identifié le groupe minoritaire (le SR le plus bas
      pour l'outcome positif)
- [ ] J'ai interprété mon DI avec le seuil 4/5 (0.8 ou 1.25)
- [ ] J'ai documenté mes 2 verdicts dans le notebook (chiffres + 1 phrase
      d'interprétation chacun)
- [ ] J'ai compris que le DI est un **signal**, pas un verdict absolu — il
      faut compléter par d'autres mesures (M7)
- [ ] J'ai écrit dans `audit.md` les 2-3 alertes éthiques pour Klaus Eichmann