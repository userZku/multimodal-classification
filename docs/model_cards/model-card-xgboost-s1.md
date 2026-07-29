# Carte de modèle - xgboost-s1-multimodal

## En deux phrases
Ce modele predit une classe de delai de retour a l'emploi (0, 1 ou 2) a partir de donnees tabulaires et d'un texte de synthese.

Il sert a aider un conseiller a prioriser les dossiers, pas a rendre une decision automatique.

## Identite du modele

| Champ | Valeur |
|---|---|
| Nom | xgboost-s1-multimodal |
| Algorithme | XGBoost (classification multiclasse) |
| Sortie | Probabilites par classe + classe predite |
| Artefact | `models/best_model/pipeline.joblib` |
| Metadonnees | `models/best_model/metadata.json` |
| Service d'inference | `src/api/main.py` |

## Ce que le modele fait (et ne fait pas)

### Ce qu'on attend de lui
- Donner un premier niveau de priorisation.
- Signaler les cas potentiellement a risque.
- Aider la revue humaine, surtout sur les cas incertains.

### Ce qu'on ne lui demande pas
- Prendre une decision seul.
- Etre reutilise tel quel sur une autre population.
- Etre utilise hors du cadre metier decrit dans le projet.

## Sur quoi il est entraine
Le modele est entraine sur le CSV du projet, avec trois types de signaux:
- numerique;
- categoriel;
- texte libre (`synthese_entretien`, vectorise en TF-IDF).

Point important pour la gouvernance des donnees:
- `usager_id` peut etre present dans le payload API pour la tracabilite;
- `usager_id` est retire avant inference;
- `code_insee_commune` est transforme en `departement_insee`, puis exclu du frame modele.

## Comment il est entraine
1. Chargement des donnees et separation cible/features.
2. Preprocessing multimodal (imputation, scaling, encodage, TF-IDF).
3. Entrainement XGBoost sur split stratifie.
4. Sauvegarde du pipeline et des metadonnees.
5. Tracking du run dans MLflow (params, metriques, artefacts).

## Comment on l'evalue
Les metriques de reference sont:
- `accuracy`
- `f1_macro`
- `recall_class_2`
- `critical_2_to_0`
- matrice de confusion

Ces informations sont tracees dans `metadata.json` et dans MLflow.

## Comportement a l'inference
- L'API renvoie `prediction`, `confidence` et `status`.
- La prediction est basee sur l'argmax de `predict_proba`.
- Si `confidence < ABSTENTION_THRESHOLD`, la sortie passe a `a_revoir`.

## Limites connues
- Rappel plus fragile sur la classe critique.
- Signal texte parfois peu stable selon la qualite des verbatims.
- Sensibilite aux derives de donnees.
- Performance dependante du contexte de collecte local.

## Risques et garde-fous

| Risque | Impact possible | Garde-fou actuel |
|---|---|---|
| Faux negatifs critiques (`2 -> 0`) | Sous-priorisation de profils vulnerables | Suivi explicite de `critical_2_to_0` + revue humaine |
| Biais (variables sensibles/proxies) | Iniquite de traitement | Comparaison de scenarios avec/sans variable sensible |
| Sur-confiance dans l'outil | Mauvaise decision operationnelle | Positionnement explicite en aide a la decision |

## Exploitation
- Metriques exposees sur `/metrics` (Prometheus).
- Tableau de bord Grafana pour le suivi API.
- Logs JSONL pour inference et retrain.
- MLflow pour l'historique des runs.

## References projet
- `docs/runbooks/decision-log.md`
- `reports/journal/journal-de-bord.ipynb`
- `notebooks/multimodal-classification.ipynb`
