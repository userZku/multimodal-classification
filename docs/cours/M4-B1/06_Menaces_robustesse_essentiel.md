# Menaces sur une solution d'IA & robustesse — Mini-cours

> Brief associé : M4-B1
> Durée de lecture : ~20 min
> Pré-requis : avoir un modèle entraîné (le benchmark).

## Pourquoi cette techno ?

Un modèle d'IA a des **failles que les tests classiques ne voient pas**. Il peut
donner une excellente MAE sur ton jeu de test **et** se faire complètement
berner par une entrée légèrement modifiée, ou délirer sur une donnée qu'il n'a
jamais vue. Au moment de **choisir** un modèle (C4), un pro ne regarde pas que
la performance : il se demande *« à quoi ce modèle est-il vulnérable ? »*.

Ce mini-cours est une **acculturation** (le syllabus y consacre un bloc
« menaces », distinct des compétences). On apprend à **nommer** les menaces et à
poser un **réflexe de robustesse en conception**. Le traitement complet (threat
model, attaques, mitigation, audit sécurité) viendra en **M7**, et le monitoring
du *drift* en production en **M6**.

> ⚠️ **Cadrage compétences** : cette activité **ne relève pas de C2**
> (éthique / sociétal / réglementaire / confidentialité). C'est une
> **ouverture** — un **complément à ta décision C4** (« au-delà de la
> performance, ce modèle est-il fiable ? ») et une **préparation à M7**
> (menaces sur les systèmes d'IA). L'analyse C2, elle, porte sur les risques
> éthiques et réglementaires du cas (cf. `decision_card.md`, section dédiée).

## Concepts clés

- **Exemple adversarial (adversarial example)** — *ouverture culturelle, à
  connaître de nom* : une perturbation **minuscule et souvent invisible** de
  l'entrée, calculée pour tromper le modèle. L'exemple iconique : une image de
  panda + un bruit imperceptible → le modèle voit un gibbon avec 99 % de
  confiance. Existe aussi sur le tabulaire (modifier 2-3 features dans les marges
  pour changer une décision de scoring). En M4, retiens **l'idée** (une entrée
  peut être fabriquée pour tromper), pas la technique.
- **Hors-distribution (OOD) — la menace à vraiment intégrer en M4** : voir plus
  bas ; c'est celle que tu peux **repérer et gérer dès maintenant** sur Bike
  Sharing (une valeur jamais vue à l'entraînement).
- **Empoisonnement (data poisoning)** : l'attaque a lieu **à l'entraînement** —
  on injecte des données truquées pour que le modèle apprenne une faille (une
  « porte dérobée »).
- **Hors-distribution (OOD / distribution shift)** : l'entrée est *légale* mais
  **hors du domaine** vu à l'entraînement (une température jamais observée). Le
  modèle **extrapole** sans le dire — souvent n'importe comment.
- **Atténuation (état de l'art)** : on ne « corrige » pas une fois pour toutes.
  On combine **robustesse** (entraînement adversarial, augmentation), **détection
  OOD** (refuser de prédire hors domaine), **abstention** (un seuil de confiance
  en dessous duquel on renvoie à un humain — HITL), et plus tard du **monitoring**.

> 🧭 **Réflexe « conception vs exploitation »** : en M4 (conception), on prévoit
> un **mode de repli** (seuil d'abstention, garde-fou sur les entrées). La
> détection de *drift*, la calibration et le suivi en prod, c'est **l'exploitation**
> (M6). Ne mélange pas les deux.

## Exemple minimal qui tourne

Deux tests rapides de robustesse sur **ton** modèle de benchmark :

```python
# scikit-learn — sur le modèle retenu du benchmark
import joblib

model = joblib.load("models/mistral_tarif_v2.joblib")   # ton meilleur modèle
x = X_test.iloc[[0]].copy()
base = model.predict(x)[0]
print(f"Prédiction normale : {base:.0f}")

# 1) Entrée HORS-DISTRIBUTION : une valeur normalisée aberrante (jamais vue)
x_ood = x.copy()
x_ood["temperature_norm"] = 5.0          # censé être ~0-1
print(f"Prédiction OOD     : {model.predict(x_ood)[0]:.0f}  ← extrapolation ?")

# 2) SENSIBILITÉ : une petite perturbation change-t-elle beaucoup la sortie ?
x_pert = x.copy()
x_pert["humidity_norm"] *= 1.05          # +5 %
delta = model.predict(x_pert)[0] - base
print(f"Écart sous +5% humidité : {delta:+.0f}")
```

Tu observes que le modèle **prédit quand même** sur l'entrée OOD (sans alerter) —
c'est précisément le risque à signaler.

## Exercice guidé

Sur le modèle que tu retiens dans le benchmark :

1. Fais varier **une feature** au-delà de sa plage d'entraînement (OOD) et
   regarde si la prédiction reste plausible.
2. Applique une **petite perturbation** (±5 %) sur 2-3 features et mesure
   l'amplitude du changement de sortie (stabilité).
3. Propose **un garde-fou de conception** en 2 lignes : un seuil ? un contrôle
   des bornes d'entrée ? une abstention si l'entrée est OOD ?

**Attendu** : tu ajoutes à ta `decision_card` une ligne **« robustesse / menace
identifiée + garde-fou proposé »** — pas une mitigation complète (c'est M7),
juste le **réflexe** de ne pas livrer un modèle aveugle à ses propres failles.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Confondre « bon score test » et « robuste » | Un modèle peut exceller sur le test et casser sur une entrée OOD ou adversariale |
| Vouloir tout mitiger en M4 | La mitigation/audit complet, c'est M7 — en M4 on **identifie** et on pose un garde-fou |
| Traiter le *drift* ici | Le drift est un sujet d'**exploitation** (M6), pas de conception |
| Croire l'adversarial réservé à la vision | Existe aussi sur le tabulaire (scoring, fraude) |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| Le modèle prédit une valeur absurde sur une entrée bizarre | Aucune détection OOD ni contrôle des bornes d'entrée |
| Deux entrées quasi identiques donnent des sorties très différentes | Modèle instable / surajusté → fragile à de petites perturbations |

## Pour aller plus loin

- **MITRE ATLAS** (taxonomie des menaces sur l'IA) : <https://atlas.mitre.org/>
- **OWASP Machine Learning Security Top 10** : <https://owasp.org/www-project-machine-learning-security-top-10/>
- **Goodfellow et al. (2014) — *Explaining and Harnessing Adversarial Examples*** : <https://arxiv.org/abs/1412.6572> (l'article fondateur, exemple du panda)
- En M7 : threat model structuré + audit sécurité complet. En M6 : monitoring du drift en production.

## Vérification (checklist apprenant)

- [ ] Je sais nommer 3 menaces sur un modèle (adversarial, poisoning, OOD).
- [ ] J'ai testé mon modèle sur une entrée hors-distribution.
- [ ] J'ai mesuré sa sensibilité à une petite perturbation.
- [ ] J'ai ajouté une ligne « robustesse + garde-fou » à ma `decision_card`.
- [ ] Je sais ce qui relève de la **conception** (M4) vs **exploitation** (M6) vs **audit** (M7).
