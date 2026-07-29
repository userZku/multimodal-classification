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

## DEC-011 - Imposer un protocole anti-fuite pour le préprocessing
- Date : 2026-07-16
- Section notebook : 4.1 / 4.2 / 4.3
- Statut : accepted
- Contexte : la section 4 introduit des transformations apprenantes (imputation, encodage, TF-IDF) sensibles au risque de fuite de données.
- Décision : appliquer `fit_transform` uniquement sur train et `transform` sur test pour tous les scénarios.
- Alternatives considérées : ajuster le préprocessing sur l'ensemble des données avant split.
- Justification : garantir une estimation honnête des performances et une comparaison équitable des 4 scénarios.
- Impact : protocole d'évaluation robuste, reproductible et défendable en soutenance.
- Risques / limites : complexité de code légèrement supérieure (objets de préprocessing par scénario).
- Suivi / action : conserver ce protocole dans toutes les étapes de modélisation et validation croisée (section 5).

## DEC-012 - Clôturer la section 4 avec un contrôle qualité exécutable
- Date : 2026-07-16
- Section notebook : 4.5
- Statut : accepted
- Contexte : la section 4 doit être validée avant modélisation pour éviter d'embarquer des incohérences dans la section 5.
- Décision : finaliser 4.5 avec des assertions exécutables couvrant intégrité cible, split, features, préprocessing et scénarios.
- Alternatives considérées : conserver uniquement des assertions commentées (non exécutées).
- Justification : rendre la clôture de section objective, vérifiable et reproductible.
- Impact : section 4 fermée avec une preuve d'exécution explicite (assertions validées).
- Risques / limites : maintenance nécessaire si la structure de données évolue.
- Suivi / action : exécuter la cellule 4.5 après toute modification de pipeline/scénario.

## DEC-013 - Retenir le ML classique comme famille principale
- Date : 2026-07-24
- Section notebook : 5.0 / 5.0.1
- Statut : accepted
- Contexte : plusieurs familles de solutions étaient envisageables (ML classique, deep learning, SLM local, LLM API, architecture agentique).
- Décision : retenir le ML classique comme famille principale pour le cas d'usage.
- Alternatives considérées : deep learning tabulaire/texte, SLM local, LLM API + RAG, architecture agentique.
- Justification : meilleur ratio entre performance attendue, coût, explicabilité minimale et sobriété d'industrialisation sur un dataset de 2 500 lignes.
- Impact : périmètre technique plus clair, stack plus légère et plus défendable en soutenance.
- Risques / limites : certaines approches plus complexes ne sont pas explorées expérimentalement.
- Suivi / action : documenter explicitement ce choix dans la section 5.0 avant la comparaison des modèles concrets.

## DEC-014 - Comparer les modèles sur F1 macro, recall classe 2 et matrice de confusion
- Date : 2026-07-24
- Section notebook : 5.2 / 5.3 / 5.4
- Statut : accepted
- Contexte : le score global seul ne suffit pas à couvrir l'enjeu métier des faux négatifs critiques.
- Décision : piloter la comparaison des modèles avec F1 macro, recall de la classe 2, accuracy en complément et matrice de confusion pour l'analyse finale.
- Alternatives considérées : sélection uniquement sur accuracy ou sur F1 macro sans métrique métier dédiée.
- Justification : équilibre entre lecture globale des performances et suivi du risque le plus coûteux (2 -> 0).
- Impact : comparaison plus robuste des scénarios et base d'arbitrage plus alignée avec le cadrage métier.
- Risques / limites : arbitrage multi-métriques plus nuancé à expliquer qu'un classement sur un score unique.
- Suivi / action : conserver cette grille de lecture dans la section 6 et dans le monitoring futur.

## DEC-015 - Limiter le tuning au couple classé rang 1
- Date : 2026-07-24
- Section notebook : 5.5
- Statut : accepted
- Contexte : une recherche d'hyperparamètres large sur tous les scénarios et modèles aurait alourdi le notebook et la narration.
- Décision : restreindre le tuning au seul couple classé rang 1 après comparaison CV.
- Alternatives considérées : absence de tuning, ou tuning exhaustif sur l'ensemble des couples scénario-modèle.
- Justification : compromis pragmatique entre amélioration mesurable et simplicité de lecture/exécution.
- Impact : gain de performance local sans transformer la section 5 en benchmark trop lourd.
- Risques / limites : possibilité de manquer un couple moins bien classé initialement mais meilleur après tuning.
- Suivi / action : signaler explicitement dans la section 5.7 que le tuning reste ciblé et non exhaustif.

## DEC-016 - Retenir S1 + XGBoost comme baseline assistive sous garde-fous
- Date : 2026-07-24
- Section notebook : 5.6 / 5.7 / 6.1 / 6.2 / 6.3
- Statut : accepted
- Contexte : le scénario S1 avec XGBoost obtient la meilleure performance globale, mais le rappel de la classe 2 reste insuffisant et des erreurs critiques 2 -> 0 subsistent.
- Décision : retenir S1 + XGBoost comme baseline de production assistive, avec escalade humaine et suivi explicite des erreurs critiques.
- Alternatives considérées : retenir S2 par prudence éthique, ou privilégier S3/S4 pour des raisons de simplicité/explicabilité.
- Justification : meilleur compromis global observé en test, tout en reconnaissant que le modèle ne doit pas être utilisé de façon autonome sur les cas sensibles.
- Impact : trajectoire d'industrialisation clarifiée et arbitrage final défendable devant le jury.
- Risques / limites : risque métier résiduel encore significatif sur la classe 2, plus exposition au biais car la variable sensible est présente dans S1.
- Suivi / action : compléter ensuite la section 7 avec une stratégie d'abstention ou d'escalade basée sur la confiance prédictive.

## DEC-017 - Encadrer la baseline par une politique d'escalade basée sur la confiance
- Date : 2026-07-27
- Section notebook : 7.2 / 7.2.1 / 7.4
- Statut : accepted
- Contexte : malgré de bons scores globaux, des erreurs critiques 2 -> 0 subsistent et imposent un garde-fou opérationnel.
- Décision : retenir une logique d'usage assistif avec escalade humaine des cas incertains, calibrée par seuil de confiance et comparée à une variante combinée orientée risque classe 2.
- Alternatives considérées : usage autonome sans abstention, ou escalade fixe non calibrée.
- Justification : réduire le risque de faux négatifs critiques en ciblant les dossiers les plus ambigus, avec un arbitrage explicite entre charge manuelle et sécurité métier.
- Impact : stratégie de fallback opérationnalisable, plus défendable en soutenance et compatible avec un déploiement progressif.
- Risques / limites : gain parfois modeste de la règle combinée selon le seuil retenu ; surcharge potentielle de reprise manuelle si calibration trop prudente.
- Suivi / action : fixer un seuil cible avec les parties prenantes (capacité opérationnelle) et suivre mensuellement le couple taux d'escalade / erreurs critiques résiduelles.

## DEC-018 - Documenter la faible diversité textuelle comme limite structurante
- Date : 2026-07-27
- Section notebook : 3.7 / 5.7 / 7.4
- Statut : accepted
- Contexte : le corpus contient peu de verbatims réellement distincts au regard du volume total, ce qui fragilise le signal NLP.
- Décision : considérer explicitement la faible diversité du texte comme une limite méthodologique majeure et interpréter prudemment les gains liés aux variables textuelles.
- Alternatives considérées : traiter le texte comme un signal pleinement robuste sans réserve particulière.
- Justification : réduire le risque de sur-interprétation et mieux cadrer le risque de sur-apprentissage sur des formulations répétitives.
- Impact : discours analytique plus honnête, meilleure gestion du risque en soutenance, priorisation future d'un enrichissement de la collecte texte.
- Risques / limites : perception de moindre maturité NLP à court terme ; amélioration de performance potentiellement limitée sans nouvelles données textuelles.
- Suivi / action : intégrer un plan d'amélioration data (qualité/diversité des verbatims) avant toute montée en autonomie du modèle.

## DEC-019 - Expliciter le mapping des features et traiter est_allocataire en catégorielle
- Date : 2026-07-27
- Section notebook : 4.1 / 4.2 / 4.3 / 5.2
- Statut : accepted
- Contexte : la sélection automatique par dtype rendait le pipeline moins lisible et pouvait faire varier le traitement de certaines colonnes selon le typage observé.
- Décision : fixer des listes explicites de variables numériques et catégorielles, avec `est_allocataire` traité en catégorielle binaire, puis réutiliser ce mapping dans les scénarios et la validation croisée.
- Alternatives considérées : conserver la détection automatique par type (`select_dtypes`) pour construire les blocs num/cat.
- Justification : renforcer la cohérence métier du préprocessing, limiter les effets de bord liés aux dtypes, et améliorer l'auditabilité du notebook en soutenance.
- Impact : pipeline plus déterministe et plus lisible ; amélioration observée de la couverture de la classe 2 sur test (recall 0,544) avec baisse des erreurs critiques 2 -> 0 (7 au lieu de 8), à performance globale quasi stable.
- Risques / limites : maintenance manuelle du mapping requise si le schéma évolue ; risque d'oubli d'une nouvelle colonne sans assertions de contrôle.
- Suivi / action : conserver les assertions de features non mappées et mettre à jour le mapping explicite à chaque évolution du dataset.

## DEC-020 - Exposer une API minimaliste avec retrain contrôlé et observabilité native
- Date : 2026-07-29
- Section notebook : 8.2 / 8.3 / 8.4 / 9.1
- Statut : accepted
- Contexte : besoin d'une industrialisation démontrable en local avec un service d'inférence simple, un point de retrain et des indicateurs techniques visibles pour la soutenance.
- Décision : conserver une API FastAPI centrée sur `/predict`, `/retrain` (et alias `/train`), `/health` et `/metrics`, instrumentée Prometheus et déployée via Docker Compose avec Prometheus + Grafana.
- Alternatives considérées : API plus riche (versioning avancé, batch, auth) dès maintenant, ou exposition de l'inférence sans stack de monitoring.
- Justification : prioriser la lisibilité architecture + preuve d'exploitabilité, tout en gardant un coût de maintenance adapté au périmètre certif.
- Impact : démonstration bout en bout plus crédible (train, serving, métriques, dashboard), et base opérationnelle pour suivre le taux d'escalade et les erreurs critiques en section 9.
- Risques / limites : absence d'authentification et de gouvernance multi-utilisateurs ; couverture limitée aux métriques techniques et applicatives de base.
- Suivi / action : compléter ensuite avec gestion des accès, alerting et runbook d'exploitation en contexte réel.

## DEC-021 - Activer le tracking MLflow sur l'entraînement et le retrain API
- Date : 2026-07-29
- Section notebook : 8.4 / 9.2
- Statut : accepted
- Contexte : la traçabilité des runs n'était pas active de bout en bout dans le flux de training/retraining.
- Décision : intégrer MLflow directement dans `train.py` (params, métriques, features, artifacts, run_id) et propager les paramètres de tracking (`tracking_uri`, `experiment`) via l'endpoint `/retrain`.
- Alternatives considérées : conserver uniquement les artefacts locaux (joblib + metadata JSON), ou connecter un registre de modèles complet dès cette itération.
- Justification : améliorer la reproductibilité et la comparabilité des runs sans alourdir immédiatement la stack avec un registre distant.
- Impact : chaque entraînement est historisé, corrélable aux métriques métier et exploitable dans l'UI MLflow ; la metadata du modèle contient désormais les identifiants de run.
- Risques / limites : backend filesystem MLflow en mode maintenance (nécessite `MLFLOW_ALLOW_FILE_STORE=true`) et absence de workflow de promotion de modèle.
- Suivi / action : planifier la migration vers un backend SQL (sqlite au minimum), puis définir une politique de sélection/promotion des runs gagnants.

## DEC-022 - Simplifier l'UI de saisie ROME et clarifier le rôle de `usager_id`
- Date : 2026-07-29
- Section notebook : 8.2 / 8.8
- Statut : accepted
- Contexte : la saisie du code ROME via liste déroulante + logique "autre" dégradait l'UX, et la documentation pouvait laisser penser que `usager_id` entrait dans le modèle.
- Décision : remplacer la sélection ROME par un champ texte simple (placeholder `Ex. Mxxxxx`) et préciser dans la documentation/API que `usager_id` reste optionnel pour traçabilité mais est exclu des features de prédiction.
- Alternatives considérées : conserver le menu déroulant avec option "autre", ou supprimer `usager_id` du schéma d'entrée dès maintenant.
- Justification : réduire la friction en démo, garder un payload API compatible avec la traçabilité, et lever l'ambiguïté fonctionnelle côté jury.
- Impact : formulaire plus fluide, meilleure lisibilité du contrat API, et cohérence renforcée entre code de préprocessing et documentation section 8.
- Risques / limites : la validation métier des codes ROME saisis librement reste limitée (pas de référentiel contrôlé en ligne dans cette version).
- Suivi / action : ajouter ultérieurement une table de correspondance ROME (code/libellé) et un contrôle de validité côté backend si besoin d'usage opérationnel renforcé.
