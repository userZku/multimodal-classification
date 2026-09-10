# Risques RGPD multi-sources — Mini-cours

> Brief associé : M3-B1
> Durée de lecture + pratique : ~20 min
> Pré-requis : avoir vu l'audit éthique M2-B1 (mini-cours 02 disparate impact).

## Pourquoi cette techno ?

En M2, tu as audité un **dataset propre** où les variables sensibles
étaient **directes** : `sex`, `race`, `marital_status`. C'est facile à
repérer — tu vois la colonne, tu sais.

En M3, tu travailles sur **plusieurs sources hétérogènes** (capteurs,
ERP, logs). Aucune de ces sources n'a de variable sensible **directe**.
Mais croisées, elles peuvent **ré-identifier** un individu :

- `ouvrier_id` (ERP) seul = pseudonyme, peu identifiant
- `ouvrier_id` + `planning_RH` externe = **identité réelle révélée**
- `timestamp` + `site` + `line` (logs) + `ouvrier_id` (ERP) = qui était
  au poste à 14h32 le 12 avril → **identifié à 99 %**

C'est ça la **ré-identification indirecte**. Le RGPD la couvre
explicitement (considérant 26 : *« il y a lieu de prendre en compte tous
les moyens raisonnablement susceptibles d'être utilisés [...] pour
identifier directement ou indirectement »*).

Ton job en M3-B1 : **identifier ces risques de croisement** avant que
quelqu'un les exploite par accident.

**Alternatives à connaître :**

| Approche | Quand l'utiliser ? |
|---|---|
| **Cartographie qualitative + recommandation** | Notre M3-B1 — proportionné, lisible décideur |
| **AIPD (Analyse d'Impact à la Protection des Données)** | Document juridique formel — obligatoire pour traitements à risque élevé. Pas notre tâche M3. |
| **k-anonymity, l-diversity** (métriques) | Très techniques, utiles en M7 (audit complet) |
| **Differential privacy** | Très avancé — recherche / cas extrêmes |

## Concepts clés

- **Variable sensible directe** : `sex`, `race`, `religion`, `opinions
  politiques`, `données de santé`. Listée dans **RGPD art. 9**.
- **Variable sensible indirecte / quasi-identifiant** : champ qui, **seul**,
  ne révèle rien, mais **croisé** avec d'autres révèle un individu.
  Exemples typiques : `ouvrier_id`, `code_postal + date_naissance +
  genre`, `IP`, `device_id`, `MAC`.
- **Pseudonymisation** vs **anonymisation** :
  - **Pseudonymisation** : on remplace l'identité par un alias
    (`EMP-5317`). Le lien direct est cassé, mais **réversible** avec une
    table de correspondance. **Toujours RGPD-soumise.**
  - **Anonymisation** : irréversible, plus aucun lien possible. **Sort
    du RGPD** (mais très difficile à garantir en multi-sources).
- **Ré-identification indirecte** : reconstitution d'identité par
  **croisement** de plusieurs sources, même pseudonymisées.
- **Principe de proportionnalité** : ne collecter / conserver que **ce
  qui est strictement nécessaire** à la finalité déclarée.
- **Recommandation** vs **prescription** : en M3-B1, tu **alertes** sur
  un risque et tu **proposes** une posture. Tu **ne décides pas** à la
  place du DPO client.

## Exemple minimal — Acerox

Sur les 3 sources Acerox :

| Source | Variable potentiellement sensible | Type de risque |
|---|---|---|
| `capteurs_iot.csv` | aucune directe | Faible (mais croisé avec `ouvrier_id` ERP : peut révéler qui a manipulé telle machine à tel moment) |
| `erp_export.json` | `ouvrier_id` | **Moyen** — pseudonymisé mais **identifiable par croisement** avec un planning RH externe |
| `logs_machines.log` | aucune directe | Faible (mais `timestamp + site + line` croisé avec planning RH = identification) |

**Recommandations type** :

- **`ouvrier_id`** : ne le conserver dans la BDD pivot que **si
  nécessaire** à la finalité (prédire les défauts qualité **n'exige
  pas** de connaître l'opérateur — le retirer ou le hasher au moment de
  l'ingestion).
- Si conservation justifiée → **pseudonymiser plus fort** (hash salé,
  rotation du sel — cf. M2-B2 mini-cours 04 anonymisation).
- **Documenter** dans la datasheet la **finalité** de chaque variable
  semi-sensible conservée.

## Exercice guidé (tâche 3 du brief)

Pour chaque source du tableau d'inventaire `identification_sources.md`,
remplis la colonne **« Risques RGPD »** avec :

1. Le **type** de risque (direct / indirect par croisement)
2. La **variable** concernée
3. Une **recommandation** opérationnelle en 1 phrase

**Solution attendue type** (à toi de l'écrire dans ta propre note) :

> ⚠️ **Risque RGPD indirect** : `ouvrier_id` (ERP) est un pseudonyme, mais
> croisé avec un planning RH externe il permet de ré-identifier la
> personne au poste. Recommandation : ne le retenir dans la BDD pivot que
> si nécessaire au modèle ; sinon, hash + sel rotatif au moment de
> l'ingestion.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Dire "pas de RGPD ici" parce que pas de `sex`/`race` | Tu rates les risques indirects — toujours chercher les quasi-identifiants |
| Confondre pseudonymisation et anonymisation | Tu rassures le DPO à tort |
| Proposer une mitigation sans la justifier | Sébastien te demandera *« pourquoi »* — anticipe |
| Sur-réagir (« on supprime tout ») | Le client a aussi besoin d'utiliser ses données — propose proportionné |
| Sous-réagir (« on laisse, ça ira ») | RGPD = obligation de moyens. *« On a oublié »* n'est pas une défense |
| Vouloir faire l'AIPD complète | Hors-périmètre M3 — escalade au DPO Acerox |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| Tu n'as identifié que 0 ou 1 risque RGPD | Tu n'as pas cherché les croisements possibles — refais l'exercice en pensant *« comment ré-identifier ? »* |
| Tes recommandations sont trop vagues (*« il faudrait faire attention »*) | Reformule en action concrète (*« hasher avec sel rotatif »*) |
| Le DPO Acerox te demande une AIPD | Tu as **trop** alerté — la note M3-B1 doit signaler, pas décider AIPD |

## Pour aller plus loin

- **CNIL — *L'anonymisation des données personnelles*** : <https://www.cnil.fr/fr/technologies/lanonymisation-de-donnees-personnelles>
- **CNIL — *Quels sont les principes fondamentaux du RGPD ?*** : <https://www.cnil.fr/fr/comprendre-le-rgpd>
- **AI Act européen** (synthèse) : <https://artificialintelligenceact.eu/the-act/>
- **EDPB — Guidelines on Anonymisation Techniques** (anglais) : référence
  réglementaire européenne

## Vérification (checklist apprenant)

- [ ] J'ai identifié au moins **1 risque indirect par croisement** sur
      les 3 sources (pas juste des variables sensibles directes)
- [ ] Chaque risque RGPD listé a une **variable** identifiée et une
      **recommandation** opérationnelle
- [ ] Je sais distinguer **pseudonymisation** et **anonymisation**
- [ ] Je n'ai **pas** rédigé d'AIPD (hors périmètre M3)
- [ ] Mes recommandations sont **proportionnées** (ni sur-réaction, ni
      sous-réaction)
