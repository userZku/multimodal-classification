# Decision Log - Registre des décisions d'architecture et de modélisation

Ce document retrace l'ensemble des choix techniques, méthodologiques, éthiques et d'architecture réalisés tout au long du projet de classification multimodale.
Il garantit la traçabilité des arbitrages pour le jury et la maintenabilité future de la solution.

## Règle de tenue du registre

- Chaque décision importante fait l'objet d'une fiche formalisée.
- Les décisions annulées ou modifiées sont conservées avec le statut `superseded` pour préserver l'historique.
- Chaque fiche précise la section du notebook concernée, la justification métier/technique, l'impact et les risques résiduels.

## Format type

```markdown
## DEC-XXX - Titre explicite
- Date : AAAA-MM-JJ
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

## Index synthétique des décisions

- **Gouvernance & Dépôt** : DEC-001, DEC-002, DEC-003, DEC-004
- **Cadrage & Éthique** : DEC-005, DEC-006, DEC-007, DEC-016 (remplacée), DEC-023
- **Données & Préprocessing** : DEC-008, DEC-009, DEC-010, DEC-011, DEC-012, DEC-018, DEC-019
- **Modélisation & Évaluation** : DEC-013, DEC-014, DEC-015, DEC-017, DEC-024
- **Serving, MLOps & UI** : DEC-020, DEC-021, DEC-022, DEC-025

---

## DEC-001 - Utiliser un dépôt structuré en support du livrable
- Date : 2026-07-16
- Section notebook : 0.5 / Livrables
- Statut : accepted
- Contexte : Le rendu certifiant repose sur le notebook principal et la soutenance orale, mais le projet couvre également l'API, le suivi MLOps et l'infrastructure conteneurisée.
- Décision : Conserver une arborescence de projet complète (`data`, `src`, `models`, `reports`, `docs`, `tests`, `infra`, `app`) pour soutenir la démarche.
- Alternatives considérées : Travailler exclusivement dans un notebook monolithique.
- Justification : Garantit la lisibilité, la réutilisabilité du code et la preuve d'industrialisation (compétences C6 à C9).
- Impact : Séparation claire entre code de production (`src/`), interface (`app/`), artefacts (`models/`) et réflexions analytiques (`notebooks/`).
- Risques / limites : Nécessite de maintenir une stricte cohérence entre le code du dépôt et les explications du notebook.
- Suivi / action : Maintenir le notebook final comme le fil conducteur de la soutenance.

## DEC-002 - Cibler Python 3.12 et le gestionnaire uv
- Date : 2026-07-16
- Section notebook : 0.5
- Statut : accepted
- Contexte : Besoin d'un environnement d'exécution déterministe et performant pour la stack ML (scikit-learn, XGBoost, LightGBM, FastAPI, MLflow).
- Décision : Standardiser le projet sur Python 3.12 et utiliser `uv` pour la gestion de l'environnement virtuel.
- Alternatives considérées : Python 3.11 ou Python 3.14 (trop récent, risques de compatibilité avec certaines roues pré-compilées).
- Justification : Excellent compromis entre performance d'exécution et maturité de l'écosystème de bibliothèques.
- Impact : Installation rapide des dépendances et reproductibilité garantie entre l'environnement local et l'image Docker.
- Risques / limites : Nécessite de veiller à la présence de Python 3.12 sur la machine hôte.
- Suivi / action : Fichiers `.python-version` et `requirements.txt` verrouillés.

## DEC-003 - Proscrire l'exposition de chemins absolus
- Date : 2026-07-16
- Section notebook : 0.5 / 2.2
- Statut : accepted
- Contexte : Risque de fuite d'informations locales (noms d'utilisateurs, arborescence système) dans les sorties du notebook publiées sur GitHub.
- Décision : Résoudre et afficher systématiquement les chemins relatifs au `PROJECT_ROOT`.
- Alternatives considérées : Afficher le chemin système complet.
- Justification : Respect des bonnes pratiques de confidentialité, de propreté documentaire et de portabilité du code.
- Impact : Notebook directement publiable et réexécutable sur n'importe quel environnement sans modification.
- Risques / limites : Aucun.
- Suivi / action : Vérifié via les assertions de traçabilité en section 0.5.

## DEC-004 - Maintenir un journal de bord et un registre de décisions
- Date : 2026-07-16
- Section notebook : Annexes D / Livrables
- Statut : accepted
- Contexte : Besoin de tracer la chronologie des travaux, les échecs, les ajustements et les choix d'architecture tout au long du projet.
- Décision : Conserver deux supports complémentaires : `reports/journal/journal-de-bord.ipynb` (suivi chronologique par session) et `docs/runbooks/decision-log.md` (synthèse structurée des arbitrages).
- Alternatives considérées : Documenter uniquement dans les cellules texte du notebook principal.
- Justification : Évite de surcharger le notebook principal tout en garantissant un audit complet de la démarche.
- Impact : Traçabilité réflexive renforcée, utile pour valoriser l'autonomie et le recul critique lors de la soutenance.
- Risques / limites : Rigueur requise pour alimenter le journal à chaque session.
- Suivi / action : Mettre à jour les deux fiches à chaque étape majeure.

## DEC-005 - Prioriser la réduction des erreurs critiques (2 -> 0)
- Date : 2026-07-16
- Section notebook : 1.3 / 1.4
- Statut : accepted
- Contexte : Dans la classification du délai de retour à l'emploi, affecter à la classe 0 (retour rapide < 6 mois) une personne qui relève de la classe 2 (risque > 12 mois) provoque une perte de chance d'accompagnement renforcé précoce.
- Décision : Définir la réduction des erreurs `2 -> 0` comme le critère métier prioritaire, en complément du score global F1 macro.
- Alternatives considérées : Maximiser uniquement l'accuracy globale ou le F1-score moyen sans pondération des types d'erreurs.
- Justification : Le coût humain et social d'une sous-estimation de la vulnérabilité est largement supérieur à celui d'une surestimation prudente.
- Impact : Ajout d'une métrique sur-mesure `recall_class_2` et suivi systématique de la case (2, 0) de la matrice de confusion.
- Risques / limites : Risque d'augmenter le taux de faux positifs sur la classe 2, accepté au nom de la sécurité des usagers.
- Suivi / action : Intégré aux scorers de validation croisée et au suivi d'escalade.

## DEC-006 - Imposer un scénario d'évaluation sans variable sensible
- Date : 2026-07-16
- Section notebook : 1.2 / 1.5 / 4.3
- Statut : accepted
- Contexte : La variable `nationalite_hors_ue` présente un risque direct de biais discriminatoire et d'atteinte au principe d'égalité de traitement.
- Décision : Construire dès le cadrage un protocole comparatif intégrant un scénario multimodal nettoyé de cette variable sensible (scénario S2).
- Alternatives considérées : Conserver toutes les variables et tenter une correction a posteriori ou un lissage des probabilités.
- Justification : Démarche de "Fairness by Design" conforme aux principes de gouvernance algorithmique du service public.
- Impact : Évaluation objective du coût en performance de l'exclusion de la variable sensible.
- Risques / limites : Perte potentielle de pouvoir prédictif brut si la variable contient un signal corrélé à la cible.
- Suivi / action : Comparaison explicite S1 vs S2 en section 5 et arbitrage en section 6.

## DEC-007 - Distinguer cible initiale client et cible révisée après EDA
- Date : 2026-07-16
- Section notebook : 1.4 / 3.7
- Statut : accepted
- Contexte : Les cibles de performance exprimées par le client avant l'analyse des données peuvent s'avérer irréalistes au vu de la qualité du dataset ou du déséquilibre des classes.
- Décision : Organiser le tableau des critères de succès en deux étapes : la demande initiale du client, puis sa révision motivée à l'issue de l'analyse exploratoire (EDA).
- Alternatives considérées : Conserver une cible unique et figée du cadrage à la conclusion.
- Justification : Démarche professionnelle d'ingénierie de données qui ajuste les attentes aux réalités de la donnée.
- Impact : Transparence renforcée devant le jury sur la faisabilité réelle et les choix de recentrage.
- Risques / limites : Nécessite de bien justifier chaque écart pour éviter d'associer la révision à un renoncement.
- Suivi / action : Cibles révisées formalisées en section 3.7 et confirmées en section 6.

## DEC-008 - Adopter une stratégie d'acquisition CSV locale et traçable
- Date : 2026-07-16
- Section notebook : 2.1 / 2.2 / 2.4
- Statut : accepted
- Contexte : Le jeu de données est transmis sous forme de fichier CSV fixe dans le cadre du sujet d'examen.
- Décision : Charger le fichier depuis `data/raw/` avec calcul d'empreinte cryptographique SHA256 et vérification du schéma.
- Alternatives considérées : Importer le fichier via un script de téléchargement distant complexe.
- Justification : Simplicité, robustesse de l'exécution hors-ligne et garantie d'intégrité des données d'entrée.
- Impact : Ingestion rapide, reproductible et sans dépendance réseau externe.
- Risques / limites : Ne couvre pas la gestion de flux de données en temps réel.
- Suivi / action : Validé par les métadonnées de traçabilité en section 0.5.

## DEC-009 - Structurer l'EDA autour de décisions préparatoires
- Date : 2026-07-16
- Section notebook : 3.1 à 3.7
- Statut : accepted
- Contexte : Une analyse exploratoire peut vite se transformer en un catalogue passif de graphiques sans valeur décisionnelle.
- Décision : Chaque sous-section d'EDA doit se conclure par une implication explicite pour le préprocessing ou la modélisation.
- Alternatives considérées : Produire des visualisations génériques sans faire le lien avec les étapes suivantes.
- Justification : Maximise la pertinence de l'analyse et facilite la lecture du notebook par le jury.
- Impact : Passage fluide et argumenté de l'EDA (section 3) aux pipelines de transformation (section 4).
- Risques / limites : Exige un travail de synthèse rigoureux pour ne garder que les visualisations utiles.
- Suivi / action : Chaque constat (manquants, cardinalité, déséquilibre) est directement relié à son traitement.

## DEC-010 - Adopter un affichage compact pour les distributions catégorielles
- Date : 2026-07-16
- Section notebook : 3.3
- Statut : accepted
- Contexte : L'affichage individuel de tous les graphiques de modalités catégorielles rallongeait inutilement le notebook.
- Décision : Proposer une synthèse compacte (tableau de cardinalité et manquants) et un affichage détaillé paramétrable via un booléen (`SHOW_DETAILED_CATS`).
- Alternatives considérées : Afficher tous les histogrammes de modalités les uns après les autres.
- Justification : Compromis entre transparence analytique et lisibilité du récit de notebook.
- Impact : Rendu visuel plus professionnel.
- Risques / limites : Les modalités secondaires ne sont pas affichées sous forme de graphique par défaut.
- Suivi / action : Paramètre conservé dans le code de la section 3.3.

## DEC-011 - Verrouiller le protocole anti-fuite de données (Data Leakage)
- Date : 2026-07-16
- Section notebook : 4.1 / 4.2
- Statut : accepted
- Contexte : Les transformations apprenantes (imputation par médiane/mode, StandardScaler, OneHotEncoder, TF-IDF) doivent être ajustées sans jamais observer le jeu de test.
- Décision : Effectuer le split train/test en section 4.1 avant toute transformation, puis appliquer la règle stricte : `fit_transform` sur le train, `transform` uniquement sur le test.
- Alternatives considérées : Prépréparer l'ensemble du jeu de données avant d'effectuer le découpage train/test.
- Justification : Garantit l'absence totale de fuite de données et assure une mesure de performance réaliste.
- Impact : Validité scientifique des métriques obtenues en validation croisée et sur le jeu de test.
- Risques / limites : Impose une gestion rigoureuse des objets `ColumnTransformer` et `Pipeline`.
- Suivi / action : Contrôlé automatiquement par les assertions de la section 4.5.

## DEC-012 - Valider la préparation par des assertions de qualité exécutables
- Date : 2026-07-16
- Section notebook : 4.5
- Statut : accepted
- Contexte : Il est crucial de s'assurer que les données préparées respectent toutes les contraintes de structure avant de lancer les entraînements complexes.
- Décision : Insérer un bloc d'assertions automatisées à la fin de la section 4 (vérification des dimensions, absence de NaN, présence des cibles, cohérence des scénarios).
- Alternatives considérées : Se fier à un contrôle visuel manuel des premières lignes des matrices.
- Justification : Fournit une preuve d'exécution irréfutable et constitue un premier niveau de tests unitaires pour le pipeline.
- Impact : Sécurise le passage à la modélisation en stoppant l'exécution en cas d'anomalie.
- Risques / limites : Nécessite d'adapter les assertions si la définition d'un scénario évolue.
- Suivi / action : Cellule 4.5 exécutée et validée.

## DEC-013 - Sélectionner le Machine Learning classique comme famille prioritaire
- Date : 2026-07-24
- Section notebook : 5.0 / 5.0.1
- Statut : accepted
- Contexte : Plusieurs approches étaient envisageables pour ce problème multimodal (ML classique, Deep Learning, SLM local, LLM via API, architecture agentique).
- Décision : Sélectionner la famille du Machine Learning classique (régression logistique, Random Forest, XGBoost, LightGBM) et écarter les réseaux profonds et les LLM.
- Alternatives considérées : Réseau de neurones multimodal PyTorch, modèle de langage local Ollama ou API OpenAI + RAG.
- Justification : Avec 2 500 lignes de données, le ML classique offre le meilleur compromis entre sobriété computationnelle, rapidité d'inférence (< 300 ms), maîtrise des coûts et explicabilité.
- Impact : Architecture de production légère, entraînement rapide et absence de dépendance envers un fournisseur de LLM.
- Risques / limites : Capacité de représentation du texte plus limitée qu'un Transformer fine-tuné.
- Suivi / action : Comparaison détaillée des 4 modèles classiques en section 5.2.

## DEC-014 - Piloter la comparaison par une grille de métriques multi-axes
- Date : 2026-07-24
- Section notebook : 5.2 / 5.3 / 5.4
- Statut : accepted
- Contexte : Un modèle performant sur le score moyen peut s'avérer dangereux s'il manque les cas les plus graves ou s'il produit des probabilités mal calibrées.
- Décision : Évaluer chaque couple scénario-modèle selon une grille à 4 métriques : F1 macro (critère de classement principal), Recall classe 2 (priorité métier), ROC-AUC macro OVR (qualité du classement probabiliste) et Accuracy.
- Alternatives considérées : Classer les modèles uniquement sur l'Accuracy ou sur le F1 macro.
- Justification : Permet une vision à 360° combinant équilibre global, sécurité métier et fiabilité des scores de confiance.
- Impact : Sélection plus fine des candidats et justification solide pour le jury.
- Risques / limites : Analyse plus complexe à restituer qu'un classement sur une métrique unique.
- Suivi / action : Intégré dans le tableau comparatif 5.4.

## DEC-015 - Concentrer l'optimisation des hyperparamètres sur le meilleur candidat du scénario cible
- Date : 2026-07-24
- Section notebook : 5.5
- Statut : accepted
- Contexte : Lancer une recherche sur grille (GridSearch) exhaustive sur l'ensemble des 16 combinaisons (4 scénarios x 4 modèles) serait très lourd et peu lisible dans le notebook.
- Décision : Restreindre la phase de tuning (`ParameterGrid` + validation croisée) au meilleur algorithme du scénario de production retenu.
- Alternatives considérées : Ne faire aucun tuning ou exécuter une recherche d'hyperparamètres sur tous les scénarios.
- Justification : Démarche pragmatique qui améliore les performances du modèle retenu sans surcharger le temps d'exécution.
- Impact : Gain de performance ciblé et déroulé d'analyse fluide.
- Risques / limites : Risque théorique d'omettre un modèle secondaire qui aurait davantage profité du tuning.
- Suivi / action : Résultat du tuning validé en section 5.5.

## DEC-016 - (Remplacée) Proposition initiale de retenir S1 + XGBoost
- Date : 2026-07-24
- Section notebook : 5.6 / 6.2
- Statut : **superseded** (remplacée par DEC-023)
- Contexte : Lors de la première itération, le scénario S1 (complet avec `nationalite_hors_ue`) obtenait le F1 macro le plus élevé.
- Décision initiale : Proposer S1 comme baseline avec garde-fous.
- Motif du remplacement : L'usage direct d'une variable de nationalité dans un algorithme de décision publique contrevient aux exigences éthiques et réglementaires. S1 est donc relégué au rang de benchmark expérimental, et S2 devient le modèle officiel de production (voir DEC-023).

## DEC-017 - Encadrer les prédictions par un seuil de confiance et une revue humaine (HITL)
- Date : 2026-07-27
- Section notebook : 7.2 / 7.2.1 / 7.4
- Statut : accepted
- Contexte : Aucun modèle n'atteignant un rappel parfait sur la classe 2, une décision 100 % automatisée présenterait un risque inacceptable pour les usagers vulnérables.
- Décision : Instaurer une politique d'abstention contrôlée (`Human-in-the-Loop`) : les prédictions dont le score de confiance est inférieur à `0,55` sont orientées vers un statut `A_REVOIR` pour relecture par un conseiller.
- Alternatives considérées : Laisser le modèle décider de manière autonome sur tous les dossiers.
- Justification : Sécurise la prise en charge des cas ambigus et matérialise le rôle du modèle comme outil d'aide à la décision.
- Impact : Réduction mesurable des erreurs critiques résiduelles au prix d'un taux d'escalade humaine maîtrisé (~20 %).
- Risques / limites : Nécessite de calibrer le seuil en fonction de la capacité de traitement disponible des conseillers.
- Suivi / action : Seuil de confiance `0,55` configuré dans l'API et documenté dans le contrat d'interface.

## DEC-018 - Documenter la faible diversité du champ texte comme une limite structurante
- Date : 2026-07-27
- Section notebook : 3.7 / 7.4
- Statut : accepted
- Contexte : L'analyse de la colonne `synthese_entretien` révèle que le corpus repose sur seulement 9 phrases types répétées.
- Décision : Documenter explicitement cette pauvreté textuelle comme une limite méthodologique majeure et interpréter avec prudence les coefficients attribués aux n-grammes TF-IDF.
- Alternatives considérées : Traiter le champ texte comme un corpus riche sans mentionner cette spécificité.
- Justification : Honnêteté scientifique et prévention du risque de sur-apprentissage sur des formulations stéréotypées.
- Impact : Analyse critique appréciée en soutenance et recommandation d'enrichir la collecte textuelle future.
- Risques / limites : La contribution du canal texte reste limitée par la qualité de la donnée source.
- Suivi / action : Précisé dans la synthèse EDA (3.7) et le message client (7.3).

## DEC-019 - Fixer des listes de features explicites et isoler les variables ordinales
- Date : 2026-07-27
- Section notebook : 4.1 / 4.2
- Statut : accepted
- Contexte : La sélection automatique des colonnes par `select_dtypes` manquait de rigueur et risquait de traiter à tort des variables catégorielles comme numériques ou inverses.
- Décision : Définir des listes explicites : `NUMERIC_FEATURES`, `ORDINAL_FEATURES` et `CATEGORICAL_FEATURES`, en traitant notamment `est_allocataire` comme une variable catégorielle binaire.
- Alternatives considérées : Laisser la détection automatique par type Pandas.
- Justification : Garantit le déterminisme complet du préprocessing et évite les erreurs de casting lors du déploiement API.
- Impact : Code de préprocessing robuste et facile à auditer.
- Risques / limites : Nécessite de mettre à jour la configuration si de nouvelles colonnes apparaissent.
- Suivi / action : Intégré dans `src/config.py` et contrôlé par assertions.

## DEC-020 - Déployer une API FastAPI minimaliste avec observabilité native
- Date : 2026-07-29
- Section notebook : 8.1 / 8.2 / 8.4
- Statut : accepted
- Contexte : Nécessité de prouver la faisabilité de la mise en production du modèle avec un service REST performant et monitoré.
- Décision : Développer une API FastAPI exposant `/health`, `/predict`, `/retrain`, `/history` et `/metrics`, instrumentée avec `prometheus-client` et des journaux structurés JSONL.
- Alternatives considérées : API Flask ou architecture Microservices complexe.
- Justification : FastAPI offre la validation Pydantic native, des performances élevées, une génération de documentation OpenAPI (Swagger) automatique et une prise en main immédiate.
- Impact : Démonstration complète de l'inférence, de la journalisation et du rechargement à chaud du modèle.
- Risques / limites : API sans couche d'authentification complexes dans cette version de démonstration locale.
- Suivi / action : Service conteneurisé dans `docker-compose.yml`.

## DEC-021 - Activer le tracking MLflow sur l'entraînement et les retrains API
- Date : 2026-07-29
- Section notebook : 8.4 / 9.2
- Statut : accepted
- Contexte : Besoins de traçabilité des expérimentations, d'enregistrement des métriques et d'historisation des artefacts.
- Décision : Intégrer MLflow dans le script d'entraînement `src/modeling/train.py` pour enregistrer automatiquement paramètres, métriques, artefacts et identifiant de run (`run_id`).
- Alternatives considérées : Ne conserver que le fichier JSON de métadonnées local.
- Justification : Standard MLOps de l'industrie permettant la comparaison visuelle des runs et l'auditabilité des réentraînements.
- Impact : Chaque appel à `/retrain` génère un run MLflow consultable.
- Risques / limites : Nécessite de gérer la compatibilité du backend de stockage local.
- Suivi / action : Configuration du serveur MLflow conteneurisé (voir DEC-024).

## DEC-022 - Simplifier le formulaire IHM pour le code ROME et clarifier `usager_id`
- Date : 2026-07-29
- Section notebook : 8.2 / 8.7
- Statut : accepted
- Contexte : La sélection du code ROME par un menu déroulant à 50 entrées alourdissait la démo, et le statut de `usager_id` pouvait prêter à confusion.
- Décision : Remplacer le menu ROME par un champ texte libre (ex. `M1602`) et documenter explicitement que `usager_id` est conservé uniquement pour la traçabilité applicative mais systématiquement exclu des features prédictives (`build_model_frame`).
- Alternatives considérées : Supprimer totalement `usager_id` de la requête d'entrée.
- Justification : Expérience utilisateur fluide en démo et séparation nette entre identifiant métier et variables d'apprentissage.
- Impact : Formulaire épuré, contrat API clair et absence de fuite d'identifiant dans le modèle.
- Risques / limites : Pas de contrôle de validité en ligne de la nomenclature ROME saisie dans l'IHM de démo.
- Suivi / action : Documenté dans la section 8.2 du notebook.

## DEC-023 - Formaliser S2 comme modèle de production et encoder le diplôme en ordinal
- Date : 2026-09-01
- Section notebook : 4.1 / 4.2 / 5.5 / 5.6 / 6.2
- Statut : accepted
- Contexte : Confirmation de la règle éthique interdisant l'usage de la nationalité en production, et besoin de représenter fidèlement la hiérarchie des qualifications.
- Décision : Retenir définitivement le scénario **S2 (multimodal sans `nationalite_hors_ue`) + XGBoost** pour la production. Intégrer un `OrdinalEncoder` pour `niveau_diplome` avec l'ordre explicite : `Sans diplôme < Bac < Bac+2 < Bac+5`. Conserver le One-Hot Encoding pour les catégories nominales.
- Alternatives considérées : Conserver le One-Hot Encoding pour le diplôme ou maintenir S1 en production sous couvert d'avertissement.
- Justification : Respect strict des principes RGPD/éthiques et représentation sémantique exacte d'une variable ordonnée.
- Impact : Le modèle de production utilise 7 features clés. L'API refuse tout payload contenant `nationalite_hors_ue` (HTTP 422).
- Risques / limites : Légère baisse de performance par rapport à S1 (F1 macro ~0,713 vs 0,723 sur S1), assumée comme le prix de la conformité.
- Suivi / action : Carte de modèle mise à jour (`model-card-xgboost-s2.md`) et tests d'intégration alignés.

## DEC-024 - Activer le serveur MLflow dans Docker Compose et intégrer le ROC-AUC
- Date : 2026-09-04
- Section notebook : 5.2 / 5.3 / 5.4 / 8.1 / 8.4
- Statut : accepted
- Contexte : L'interface MLflow devait être directement accessible lors des démos conteneurisées, et la qualité du classement probabiliste nécessitait un indicateur dédié.
- Décision : Ajouter un service `mlflow` dans `docker-compose.yml` (port 5000) relié au volume `./mlruns` et configuré avec les hôtes autorisés. Ajouter le `roc_auc_ovr_macro` dans la grille d'évaluation scikit-learn.
- Alternatives considérées : Lancer MLflow séparément en ligne de commande locale hors Docker.
- Justification : Stack Docker Compose 100 % autonome (API + MLflow + Prometheus + Grafana) et évaluation probabiliste renforcée.
- Impact : Consultation immédiate des runs via `http://127.0.0.1:5000` et mesure complémentaire du classement des probabilités (~0,857 en CV sur S2).
- Risques / limites : Le stockage sur système de fichiers (`file:///mlruns`) requiert la variable `MLFLOW_ALLOW_FILE_STORE=true`.
- Suivi / action : Intégré à la stack Docker et validé par les tests de retrain.

## DEC-025 - Refondre l'IHM en tableau de bord d'administration et finaliser les livrables
- Date : 2026-09-07
- Section notebook : 8.1 / Livrables
- Statut : accepted
- Contexte : L'interface utilisateur initiale manquait de relief visuel et de lisibilité pour une présentation professionnelle devant un jury.
- Décision : Refondre l'IHM (`app/ui`) sous la forme d'un tableau de bord d'administration sombre (style console d'exploitation Debian), intégrant la navigation latérale, l'état du service en direct, des cartes d'indicateurs clés, le formulaire de prédiction, l'historique récent et des accès directs aux outils de supervision.
- Alternatives considérées : Conserver la mise en page simpliste initiale.
- Justification : Valorisation de la dimension MLOps et confort visuel lors de la démonstration orale.
- Impact : Expérience de démonstration fluide, professionnelle et cohérente avec la stack de supervision (Grafana/Prometheus).
- Risques / limites : Nécessite de veiller à la bonne réactivité responsive sur tous les écrans.
- Suivi / action : Captures d'écran rafraîchies et intégrées dans le README.
