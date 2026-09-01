# Carte de modele - xgboost-s2-multimodal

## En deux phrases
Ce modele predit une classe de delai de retour a l'emploi (0, 1 ou 2) a partir de donnees tabulaires et d'un texte de synthese.

Il sert a aider un conseiller a prioriser les dossiers, pas a rendre une decision automatique.

## Identite du modele

| Champ | Valeur |
|---|---|
| Nom | xgboost-s2-multimodal |
| Scenario | S2 - multimodal sans variable sensible directe |
| Algorithme | XGBoost (classification multiclasse) |
| Sortie | Probabilites par classe + classe predite |
| Artefact | `models/best_model/model.joblib` |
| Metadonnees | `models/best_model/metadata.json` |
| Service d'inference | `src/api/main.py` |

## Donnees et features

Le modele utilise des signaux numeriques, categoriels et le texte libre `synthese_entretien` vectorise en TF-IDF.

Les gardes-fous de production sont les suivants:
- `nationalite_hors_ue` est exclue avant l'entrainement et absente du contrat API;
- tout payload qui contient cette variable est refuse par l'API;
- `usager_id` est reserve a la tracabilite et retire avant inference;
- `code_insee_commune` est transforme en `departement_insee`, puis retire du frame modele.

S1 est conserve uniquement dans le notebook comme comparaison experimentale pour mesurer l'ecart de performance lie a l'exclusion de la variable sensible.

## Entrainement et evaluation

1. Chargement des donnees et separation cible/features.
2. Exclusion des identifiants techniques et de `nationalite_hors_ue`.
3. Preprocessing multimodal (imputation, scaling, encodage, TF-IDF).
4. Entrainement XGBoost sur split stratifie.
5. Sauvegarde du pipeline et des metadonnees.
6. Tracking du run dans MLflow (params, metriques, artefacts).

Les metriques de reference sont `accuracy`, `f1_macro`, `recall_class_2`, `critical_2_to_0` et la matrice de confusion.

## Risques et garde-fous

| Risque | Impact possible | Garde-fou actuel |
|---|---|---|
| Faux negatifs critiques (`2 -> 0`) | Sous-priorisation de profils vulnerables | Suivi de `critical_2_to_0` + revue humaine |
| Biais indirects via des proxys | Iniquite de traitement | Audit par sous-population et suivi des variables proxy |
| Signaux sensibles dans le texte | Decision influencee par le verbatim | Revue des termes influents et escalade des cas incertains |
| Sur-confiance dans l'outil | Mauvaise decision operationnelle | Positionnement explicite en aide a la decision |

## Exploitation

- Metriques exposees sur `/metrics` (Prometheus).
- Tableau de bord Grafana pour le suivi API.
- Logs JSONL pour inference et retrain.
- MLflow pour l'historique des runs.

## References projet

- `docs/runbooks/decision-log.md`
- `docs/rgpd_ethique/rgpd-ethique.md`
- `notebooks/multimodal-classification.ipynb`