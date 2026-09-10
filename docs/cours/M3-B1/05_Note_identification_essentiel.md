# Rédaction de la note d'identification — Mini-cours

> Brief associé : M3-B1
> Durée de lecture + pratique : ~20 min
> Pré-requis : entretien fait, sources cartographiées, schéma Mermaid produit.

## Pourquoi cette techno ?

La **note d'identification des sources** est ton **livrable principal**
de M3-B1. C'est elle qui sera lue par **Sébastien Marchand** (et son DPO,
sa hiérarchie, peut-être son équipe IT). Elle doit :

- Tenir en **2-3 pages** (pas plus — un décideur lit en 5-10 min max)
- Être **lisible par un non-technicien** (pas de jargon scikit-learn, SQL, Python)
- **Distinguer** explicitement ce que tu sais (issu de l'entretien et de
  l'exploration) de ce que tu **interprètes**
- **Justifier** les sources retenues ET les sources écartées
- Lister les **questions restantes** (preuve de lucidité)

C'est l'exercice de **synthèse** central du brief — preuve C1 + C2 + CT5
+ CT6.

**Alternatives à connaître :**

| Format | Quand l'utiliser ? |
|---|---|
| **Note markdown 2-3 pages** | Notre M3-B1 — équilibré, versionnable Git |
| **Slides** | Restitution orale — préfigure M7 / M8 (mais pas encore en M3) |
| **Compte-rendu de réunion** | Trace d'une discussion — pas un livrable autonome |
| **Document Confluence / Notion** | Pour collaboration équipe — pas notre cible client externe |

## Concepts clés — la structure type d'une note d'identification

> Les **6 sections** ci-dessous sont la colonne vertébrale à reproduire dans
> `identification_sources.md`. Retiens surtout la **section 2** (distinguer
> *demande dite* / *besoin réel*) : c'est ce qui sépare un junior d'un pro.

### Structure type (à reproduire dans `identification_sources.md`)

### 1. Contexte (1 paragraphe)

> Qui est le client, qu'est-ce qu'il a, qu'est-ce qu'il demande à FastIA.

**Exemple** :
> Acerox Métallurgie est une PME française de transformation des métaux,
> ~800 salariés, 3 sites de production. Ils disposent déjà d'un modèle
> de prédiction de défauts qualité en production. Leur chef de projet
> industrialisation, Sébastien Marchand, nous a missionnés pour
> identifier les sources de données qui pourraient enrichir ce modèle
> existant.

### 2. Demande métier reformulée (1 paragraphe)

> Distingue **ce que Sébastien a dit** vs **ce qu'il cherche vraiment**.

**Exemple** :
> **Ce que Sébastien a demandé** : « enrichir notre modèle avec des nouvelles
> sources ». **Ce que je comprends qu'il cherche vraiment** : améliorer la
> capacité du modèle à **anticiper les défauts qualité 24h à l'avance**
> sur la ligne 3 du site de Roubaix (où il a actuellement le plus de
> non-conformités), pour déclencher des interventions de maintenance
> prédictive. Le KPI implicite : ramener le taux de non-conformité
> Roubaix L3 sous la moyenne des autres sites.

### 3. Inventaire des sources (tableau)

| Source | Format | Volume | Fréquence | Qualité observée | Risques RGPD | Pertinence métier |
|---|---|---|---|---|---|---|
| `capteurs_iot.csv` | CSV | 51 k / mois | continue | OK sauf Roubaix L3 (capteur défaillant) | Faible | **Haute** |
| `erp_export.json` | JSON | 2 k / mois | batch quotidien | ~5 % `ouvrier_id` null | **Moyen** (ouvrier_id pseudonymisé) | **Haute** |
| `logs_machines.log` | texte | 30 k / mois | continue | parsing à concevoir | Faible | Moyenne |

### 4. Recommandations (3-5 puces)

> Quelles sources ingérer en priorité ? Lesquelles écarter et pourquoi ?

**Exemple** :
- **Ingérer en priorité** : `capteurs_iot.csv` (corrélation directe avec
  les défauts qualité) et `erp_export.json` (contexte des ordres de
  fabrication)
- **Reporter à une 2ᵉ itération** : `logs_machines.log` — informatif mais
  parsing coûteux, à valoriser après preuve sur les 2 premières
- **Avant ingestion ERP** : déterminer si `ouvrier_id` est **nécessaire**
  au modèle (probablement non — le retirer / hasher au moment de
  l'ingestion)
- **Capteur défaillant Roubaix L3** : à signaler à l'équipe maintenance
  Acerox avant d'utiliser les données. Sinon on entraîne sur du bruit.

### 5. Points à clarifier avec Sébastien (3-5 puces)

> 3-5 questions ouvertes restantes — montre que tu **sais** ce que tu
> ne sais pas encore.

**Exemple** :
- À quelle fréquence le modèle existant est-il **réentraîné** ? (impacte
  notre stratégie d'ingestion)
- Y a-t-il un **dictionnaire de données** ERP officiel quelque part ?
- Le **planning RH** existe-t-il sous forme exploitable (pour évaluer le
  risque de ré-identification croisée) ?
- Le **capteur Roubaix L3** est-il défaillant depuis quand ? Les
  prédictions actuelles l'ignorent-elles déjà ?
- Quelle est la **fenêtre de tolérance** (latence acceptable) entre
  acquisition de la donnée et prédiction ?

### 6. Limites de cette note (3 puces max)

> Ce qu'on n'a **pas** fait et qu'il faudrait faire plus tard.

**Exemple** :
- Pas d'analyse statistique fouillée des sources (M3-B1 = identification, pas EDA)
- Pas d'AIPD juridique formelle (recommandation : escalader au DPO Acerox)
- Pas d'évaluation de l'impact du capteur défaillant sur le modèle actuel

## Exemple minimal — une note condensée

Si tu manques de temps, voici la **version la plus courte qui reste utile**
(à étoffer ensuite). Une demi-page de cette qualité vaut mieux que 3 pages floues :

> **Contexte** — Acerox (PME métallurgie, 3 sites) veut enrichir son modèle
> existant de prédiction de défauts.
>
> **Besoin réel** (≠ demande) — *dit* : « ajouter des sources » ; *réel* :
> anticiper 24 h à l'avance les non-conformités de Roubaix L3.
>
> **Sources** —
> | Source | Format | Pertinence | Risque RGPD |
> |---|---|---|---|
> | capteurs_iot.csv | CSV 51k/mois | Haute | Faible |
> | erp_export.json | JSON 2k/mois | Haute | Moyen (`ouvrier_id`) |
> | logs_machines.log | texte 30k/mois | Moyenne | Faible |
>
> **Reco** — ingérer capteurs + ERP (pseudonymiser `ouvrier_id`), reporter les logs.
>
> **À clarifier** — fréquence de réentraînement du modèle ? dictionnaire ERP ?

## Exercice guidé (tâche 5 du brief)

Rédige ta note `identification_sources.md` en suivant la structure
ci-dessus. **2-3 pages maximum**. Critères :

- Lisible par un **décideur métier non-technicien**
- **Pas** de mot comme `pandas`, `joblib`, `sklearn`, `SQL` (sauf à
  expliquer en parenthèse)
- Distinction *Ce que Sébastien a dit* vs *Ce que je comprends*

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| 5 pages de jargon technique | Le DPO décroche à la page 2 |
| Pas de distinction *dit* / *interprété* | Tu présentes ton interprétation comme une vérité — risqué |
| Recommandations vagues (*« il faudrait faire attention »*) | Pas actionnable — reformule en action concrète |
| Pas de "questions restantes" | Tu sembles tout savoir → suspect pour le client |
| Tableau d'inventaire sans la colonne "pertinence métier" | Le décideur ne sait pas par où commencer |
| Pas de section "limites" | Tu sembles infaillible → manque de lucidité |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| Ma note fait 4+ pages | Trop de détails techniques — déplace en notebook ou annexe |
| Sébastien me répond *« je ne comprends pas »* | Jargon non défini — relis avec œil de non-tech |
| Sébastien me dit *« tout est trivial »* | Tu n'as pas montré tes choix — explicite les trade-offs |
| Personne ne lit ma note | Manque de hiérarchie visuelle — titres, bullets, gras |

## Pour aller plus loin

- **Mike Ash — *Writing for Developers*** : <https://mikeash.com/pyblog/>
  (style d'écriture technique mais lisible)
- **Atlassian — *Writing meaningful technical documents*** : <https://www.atlassian.com/work-management/knowledge-sharing/documentation>
- **PWA — *Note de cadrage type*** : modèle utile pour s'inspirer du
  format consultant (recherche "note de cadrage projet IT")

## Vérification (checklist apprenant)

- [ ] Ma note a les **6 sections** (Contexte, Demande, Inventaire,
      Recommandations, Questions, Limites)
- [ ] Elle tient en **2-3 pages** markdown rendues
- [ ] Elle est lisible par un **non-technicien** (pas de jargon non défini)
- [ ] J'ai **distingué** *dit* vs *interprété* dans la section Demande
- [ ] Mes recommandations sont **chiffrées** et **actionnables**
- [ ] Mes questions restantes sont **3 à 5**, ouvertes, pas rhétoriques
- [ ] J'ai une **section Limites** explicite (preuve de lucidité)
