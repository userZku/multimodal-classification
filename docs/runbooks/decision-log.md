# Decision Log - Notebook de rendu final

Ce document sert à tracer les choix réalisés au fil du notebook de certification.
Il doit être mis à jour à chaque décision importante (méthode, métrique, éthique, industrialisation).

## Règle de mise à jour

- Ajouter une entrée dès qu'un choix est validé.
- Référencer la section du notebook concernée.
- Justifier le choix en 2 à 4 lignes maximum.
- Documenter l'impact attendu et le risque résiduel.
- En cas de changement d'avis, ne pas supprimer l'ancienne décision : ajouter une nouvelle entrée qui annule/remplace.

## Format d'entrée

```markdown
## DEC-XXX - Titre court
- Date : YYYY-MM-DD
- Section notebook : Sx.y
- Statut : proposed | accepted | rejected | superseded
- Contexte :
- Décision :
- Alternatives considérées :
- Justification :
- Impact :
- Risques / limites :
- Suivi / action :
```

---

## Index rapide par section

- Section 0 / 0.5 : environnement, traçabilité, reproductibilité
- Section 1 : cadrage métier, critères de succès
- Section 2 : source et qualité initiale des données
- Section 3 : constats EDA et biais détectés
- Section 4 : préprocessing, scénarios, assertions
- Section 5 : choix de modèles, métriques, tuning
- Section 6 : arbitrage final entre scénarios
- Section 7 : explicabilité et stratégie de fallback
- Section 8 : API, CI/CD, monitoring, architecture cible
- Section 9 : suivi production et amélioration continue

---

## DEC-001 - Utiliser un dépôt structuré en support du livrable
- Date : 2026-07-16
- Section notebook : 0.5
- Statut : accepted
- Contexte : le rendu officiel est centré sur notebook + soutenance, mais le projet couvre aussi API, monitoring et CI/CD.
- Décision : conserver une structure de dépôt complète (data/src/models/reports/docs/tests/infra) pour industrialiser la démarche.
- Alternatives considérées : travailler uniquement dans un notebook monolithique.
- Justification : meilleure traçabilité, maintenance plus simple, démonstration claire des compétences C6-C9.
- Impact : meilleure lisibilité projet, préparation soutenance facilitée.
- Risques / limites : dispersion possible si la structure n'est pas tenue à jour.
- Suivi / action : garder le notebook final comme source principale pour le jury.

## DEC-002 - Cibler Python 3.12 et uv
- Date : 2026-07-16
- Section notebook : 0
- Statut : accepted
- Contexte : besoin d'un environnement stable pour les dépendances ML (xgboost, lightgbm, mlflow).
- Décision : standardiser l'environnement sur Python 3.12 avec uv.
- Alternatives considérées : Python 3.14.
- Justification : compatibilité plus robuste des bibliothèques ML à ce stade.
- Impact : installation plus fiable pour exécution locale et CI.
- Risques / limites : nécessité d'aligner la CI et la documentation.
- Suivi / action : conserver .python-version et README à jour.

## DEC-003 - Ne pas exposer de chemins absolus
- Date : 2026-07-16
- Section notebook : 0.5
- Statut : accepted
- Contexte : dépôt public, risque d'exposition d'informations locales via les sorties notebook.
- Décision : afficher uniquement des chemins relatifs projet pour le dataset.
- Alternatives considérées : afficher le chemin système complet.
- Justification : confidentialité, portabilité, reproductibilité.
- Impact : notebook publiable sans fuite d'information locale.
- Risques / limites : aucun impact fonctionnel majeur.
- Suivi / action : conserver cette règle dans toutes les cellules d'affichage de chemins.

## DEC-004 - Tenir un journal de bord en notebook dédié
- Date : 2026-07-16
- Section notebook : Annexes D
- Statut : accepted
- Contexte : besoin de tracer la démarche de façon continue et fusionnable au rendu final.
- Décision : maintenir reports/journal/journal-de-bord.ipynb + cette fiche de décisions en Markdown.
- Alternatives considérées : journal uniquement en Markdown.
- Justification : format attendu compatible Jupyter et fusion finale simplifiée.
- Impact : meilleure continuité entre travail quotidien et rendu final.
- Risques / limites : double maintenance (journal + decision log) si discipline insuffisante.
- Suivi / action : mettre à jour les deux supports à chaque session.

## DEC-005 - Prioriser les erreurs critiques classe 2 -> 0
- Date : 2026-07-16
- Section notebook : 1.3 / 1.4
- Statut : accepted
- Contexte : dans le cas d'usage emploi, une sous-estimation des profils les plus à risque dégrade la prise en charge.
- Décision : faire de la réduction des erreurs 2 -> 0 un critère métier prioritaire, en complément du F1 macro.
- Alternatives considérées : optimisation unique du score global (accuracy/F1 global) sans pondération métier.
- Justification : le coût social et opérationnel d'un faux négatif critique est supérieur à une légère baisse de score global.
- Impact : orienter le choix de métriques vers recall classe 2 + suivi d'une matrice de confusion métier.
- Risques / limites : possible dégradation de la précision sur les autres classes.
- Suivi / action : confirmer les seuils cibles après EDA et validation de la distribution des classes.

## DEC-006 - Imposer un scénario sans variable sensible
- Date : 2026-07-16
- Section notebook : 1.2 / 1.5
- Statut : accepted
- Contexte : la variable `nationalite_hors_ue` peut introduire un risque de biais ou de discrimination directe/indirecte.
- Décision : intégrer explicitement un scénario comparatif sans variable sensible dans l'évaluation finale.
- Alternatives considérées : conserver toutes les variables et corriger uniquement en post-analyse.
- Justification : rendre l'arbitrage explicite, traçable et défendable sur le plan éthique/réglementaire.
- Impact : meilleure gouvernance des choix de features, discussion transparente en soutenance.
- Risques / limites : baisse de performance potentielle si la variable porte un signal prédictif non substituable.
- Suivi / action : documenter l'écart de performance et l'arbitrage retenu en section 6.

## DEC-007 - Distinguer cible initiale et cible révisée
- Date : 2026-07-16
- Section notebook : 1.4
- Statut : accepted
- Contexte : les seuils métier fixés avant EDA peuvent être irréalistes selon l'équilibre des classes et la qualité des données texte.
- Décision : formaliser deux colonnes de pilotage : cible initiale client puis cible révisée après EDA.
- Alternatives considérées : conserver une seule cible figée dès le cadrage.
- Justification : évite les engagements non réalistes et clarifie la logique d'ajustement méthodologique.
- Impact : pilotage plus robuste, transparence accrue sur les hypothèses et leur révision.
- Risques / limites : perception de "déplacement du but" si la justification est insuffisante.
- Suivi / action : expliciter les raisons de toute révision en section 3 et section 6.

## DEC-008 - Définir une acquisition minimale mais traçable
- Date : 2026-07-16
- Section notebook : 2.1 / 2.2 / 2.4
- Statut : accepted
- Contexte : le dataset est fourni en local dans le cadre du sujet, sans connecteur externe à maintenir.
- Décision : documenter une acquisition simple (lecture CSV locale) avec traçabilité forte déjà posée en section 0.5.
- Alternatives considérées : sur-ingénierie d'une couche d'ingestion dédiée (script ETL/API) dès cette étape.
- Justification : proportionner l'effort au besoin certif tout en gardant la reproductibilité (source, version, hash).
- Impact : section 2 claire, rapide à auditer et cohérente avec le livrable notebook.
- Risques / limites : couverture limitée des cas d'ingestion multi-sources.
- Suivi / action : enrichir l'industrialisation en section 8 si le cas d'usage évolue vers de nouvelles sources.

## DEC-009 - Conserver une EDA orientée décision métier
- Date : 2026-07-16
- Section notebook : 3.2 / 3.3 / 3.4 / 3.5
- Statut : accepted
- Contexte : l'EDA peut devenir un inventaire de sorties difficilement exploitable en soutenance.
- Décision : structurer l'EDA autour de questions décisionnelles (qualité, déséquilibre cible, relations avec risques) avec graphiques ciblés.
- Alternatives considérées : approche exhaustive sans hiérarchisation des visualisations.
- Justification : meilleure lisibilité pour le jury et lien direct avec les critères métier de section 1.
- Impact : passage plus fluide vers les sections 4 à 6 et argumentaire renforcé en arbitrage.
- Risques / limites : certains signaux faibles peuvent être manqués à ce niveau de synthèse.
- Suivi / action : compléter au besoin par des analyses ad hoc dans des cellules annexes non centrales.

## DEC-010 - Activer un mode d'affichage compact pour les catégorielles
- Date : 2026-07-16
- Section notebook : 3.3
- Statut : accepted
- Contexte : l'affichage complet des top modalités catégorielles prenait trop de place et nuisait à la lisibilité.
- Décision : garder un affichage compact par défaut (synthèse cardinalité/manquants + graphique diplôme) et rendre le détail optionnel.
- Alternatives considérées : conserver l'affichage détaillé permanent pour toutes les variables catégorielles.
- Justification : compromis entre transparence analytique et lisibilité du récit de notebook.
- Impact : section 3 plus concise, meilleure expérience de lecture en revue/soutenance.
- Risques / limites : le détail n'apparaît pas sans activation explicite.
- Suivi / action : basculer le flag de détail sur True uniquement lors d'investigations ciblées.
