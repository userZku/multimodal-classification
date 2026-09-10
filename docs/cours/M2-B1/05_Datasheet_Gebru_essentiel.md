# Datasheet Gebru (datasheets for datasets) — Mini-cours

> Brief associé : M2-B1
> Durée de lecture + pratique : ~20 min
> Pré-requis : audit qualité fait, dataset propre prêt à livrer.

## Pourquoi cette techno ?

> 📅 **Mars 2027. Tu quittes FastIA.** Un nouveau consultant récupère ton
> dataset. Il ne sait pas d'où viennent les données, quelles colonnes sont
> sensibles, ni quelles transformations tu as appliquées. Il repart de zéro —
> ou pire, il bâtit un modèle sur des données qu'il ne comprend pas. **La
> datasheet sert exactement à éviter ça.**

Une **datasheet de dataset** est l'équivalent, pour des données, d'une
fiche technique de composant électronique : elle accompagne le dataset et
**permet à un utilisateur tiers** (data scientist, DPO, juriste, métier)
de :

- **Comprendre l'origine** des données (qui, quand, pourquoi)
- **Évaluer l'adéquation** à son cas d'usage (avant de bâtir dessus)
- **Anticiper les risques** (biais, manquants, dérives)
- **Documenter ses propres transformations** pour la prochaine personne

Sans datasheet, un dataset est une **boîte noire**. Avec datasheet, c'est
un **artefact maintenable**.

Le standard de facto vient de **Gebru et al. (2018)** — *Datasheets for
Datasets* — paper Google fondateur. Format adopté par Hugging Face
(*dataset cards*), Microsoft, le AI Act européen, etc.

**Alternatives à connaître :**

| Standard | Quand l'utiliser ? |
|---|---|
| **Datasheet Gebru (7 sections)** | Notre M2 — standard universel, format markdown |
| **Hugging Face Dataset Card** | Si tu publies un dataset sur HF Hub — surcouche de Gebru |
| **Model Card (Mitchell 2019)** | Pour documenter un **modèle**, pas un dataset — équivalent côté modèle, central en M7 |
| **W3C Dataset Description** (DCAT) | Standard sémantique web pour catalogues de datasets ouverts — overkill ici |

## Concepts clés — les 7 sections Gebru (version courte M2)

### 1. **Motivation**
Pourquoi ce dataset existe ? Qui l'a créé ? Pour quel objectif initial ?

### 2. **Composition**
Combien d'observations ? Quelles colonnes ? Quels types ? Distribution de
la cible ? Variables sensibles **signalées explicitement** ?

> 💡 En M2, **le schéma technique des colonnes** vit dans cette section
> (pas dans un `schema.yaml` séparé) — un seul livrable, c'est plus simple
> à maintenir et plus facile à lire pour un non-technicien.

### 3. **Processus de collecte**
Connu / inconnu ? Période de collecte ? Quelles personnes sont représentées ?
Quel biais de sélection probable ?

### 4. **Preprocessing appliqué**
Ce que **TOI** as fait dans ton pipeline. Imputation, encodage,
normalisation, exclusions. Liste concise.

### 5. **Usages prévus / à éviter**
Pour quoi ce dataset doit-il être utilisé ? Pour quoi il ne **doit pas** ?

### 6. **Distribution**
À qui ce dataset est-il transmis ? Sous quelle forme ? Avec quelles
contraintes (RGPD, NDA, licences) ?

### 7. **Maintenance**
Qui maintient ? Comment signaler un problème ? Quelle version ?

## Exemple minimal qui tourne

Voici une datasheet minimale (mais valable) pour le German Credit Eckmühl :

```markdown
# Datasheet — German Credit (Eckmühl v1.0.0)

## 1. Motivation
Collecté par UCI Statlog (1994), à l'origine pour benchmarks ML
académiques. Version Eckmühl 2026 : utilisé en production pour le scoring
crédit conso interne. Dataset historique stable, 1 000 dossiers anonymisés.

## 2. Composition
- 1 000 observations × 20 features + 1 cible binaire `credit_risk`
- Distribution cible : 70 % `good_credit`, 30 % `bad_credit`
- Variables sensibles : `age`, `personal_status_sex` ⚠️ composite,
  `foreign_worker`

| Colonne | Type | Modalités / range | Note |
|---|---|---|---|
| `duration_months` | int | 4 — 72 | Durée du prêt |
| `credit_amount` | int | 250 — 18 424 | En DM (deutsche mark, post-conversion) |
| `personal_status_sex` | str (5 modalités) | `male single`, `female divorced/...`... | ⚠️ Anti-pattern composite |
| `foreign_worker` | str | `yes`, `no` | Protected attribute |
| ... | ... | ... | ... |

## 3. Processus de collecte
Inconnu (dataset UCI hérité). Date originale : 1994. Pays : Allemagne.
Vraisemblablement collecté par un organisme bancaire historique, données
anonymisées. **Biais probable** : reflète la composition socio-économique
allemande de 1994.

## 4. Preprocessing appliqué (par M. Arrué, FastIA, 2026-05-26)
- Imputation manquants : médiane (numériques), modalité la plus fréquente
  (catégorielles)
- Encodage `savings_account` : OrdinalEncoder avec ordre `< 100 DM <
  100-500 DM < 500-1000 DM < ≥ 1000 DM < unknown`
- OneHotEncoder sur `purpose`, `housing`, `telephone`
- StandardScaler sur les numériques

## 5. Usages
**Prévus** : scoring crédit conso Eckmühl, pipeline réutilisable pour
nouveaux dossiers de même schéma.
**À éviter** : utilisation directe en production sans audit de drift,
extrapolation hors-Allemagne, marketing direct (RGPD).

## 6. Distribution
Livré à Banque Eckmühl (Klaus Eichmann, DPO), via dépôt sécurisé. Format
Parquet snappy. Pas de re-distribution autorisée. Licence : usage interne
Eckmühl uniquement.

## 7. Maintenance
Mainteneur·euse : M. Arrué, FastIA (marrue@fastia.example).
Version : v1.0.0 — 2026-05-26.
Signaler un problème : ticket interne FastIA-XYZ.
```

Tu vois : **1 page**, lisible par un non-technicien (Klaus Eichmann, DPO),
contient toute l'info nécessaire pour évaluer le dataset.

## Exercice guidé

Rédige ta propre datasheet pour `german_credit_clean.parquet`, en remplissant
le template fourni dans `datasheet.md` à la racine du repo.

**Solution attendue** : 7 sections présentes, ~1 page max, format markdown,
contient au minimum :
- Distribution cible (chiffres)
- 3 variables sensibles listées avec mention de leur risque
- Tes choix de prétraitement (listés, pas détaillés)
- Au moins 1 usage à éviter mentionné
- Mainteneur·euse + version + date

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Datasheet écrite en jargon ML | Inutile pour le DPO ou le métier — réécris en langage courant |
| Section *Composition* sans variables sensibles signalées | Le DPO doit chercher lui-même — datasheet ratée |
| 5 pages pour 1 dataset de 1 000 lignes | Disproportionné — vise la concision |
| Oublier la section *Maintenance* | Le dataset devient orphelin dès que tu pars |
| Pas de version + date | Impossible de tracer quelle version a été utilisée par quel projet |
| Confondre datasheet (dataset) et model card (modèle) | Ce sont 2 documents distincts. En M2, datasheet. En M7, model card |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| Le DPO te demande "et qui a collecté ça ?" | Section 3 *Processus de collecte* manquante ou imprécise |
| Un data scientist tiers utilise mal le dataset | Section 5 *Usages à éviter* manquante ou trop vague |
| Tu ne sais plus quelles transformations tu as appliquées 6 mois après | Section 4 *Preprocessing* pas tenue à jour |
| Une vulnérabilité RGPD apparaît | Section 6 *Distribution* sans contraintes claires + section 2 sans signalement variables sensibles |

## Pour aller plus loin

- **Paper Gebru et al. 2018** — [*Datasheets for Datasets*](https://arxiv.org/abs/1803.09010)
  (court, lisible, le standard)
- **Hugging Face — Dataset cards** : [doc officielle](https://huggingface.co/docs/datasets/dataset_card)
  (template prêt à l'emploi pour HF Hub)
- **AI Act européen (2024)** — exige une documentation des données
  d'entraînement pour les systèmes à haut risque. Datasheet ≈ format
  pré-compatible.
- **Model Cards (Mitchell et al. 2019)** — [paper original](https://arxiv.org/abs/1810.03993)
  — l'équivalent côté modèle. À garder en tête pour M7.

## Vérification (checklist apprenant)

- [ ] J'ai rempli les **7 sections** Gebru de `datasheet.md`
- [ ] La datasheet tient en **1 page** markdown rendue
- [ ] J'ai documenté **le schéma** dans la section *Composition* (types,
      modalités, variables sensibles signalées)
- [ ] J'ai listé **mes choix de prétraitement** concis dans *Preprocessing*
- [ ] J'ai mentionné **au moins 1 usage à éviter**
- [ ] J'ai une **version + date + mainteneur·euse**
- [ ] Un non-technicien (le DPO) peut **lire et comprendre** ma datasheet
      sans me poser de question technique