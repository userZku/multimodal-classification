# Prédiction du délai de retour à l'emploi

J'ai développé une solution IA multimodale pour prédire le délai de retour à l'emploi à partir de données tabulaires et textuelles.

L'objectif de ce dépôt est simple : montrer un projet de bout en bout, depuis la modélisation jusqu'à l'industrialisation (API, qualité, conteneurisation et déploiement).

## Vue rapide

- Problème : classification multiclasse du délai de retour à l'emploi.
- Données : variables structurées + texte d'entretien.
- Stack : Python, scikit-learn, XGBoost/LightGBM, FastAPI, Pytest, GitHub Actions.
- Cible : passer d'un notebook de recherche à une application ML testée, documentée et déployable.

## Architecture

```mermaid
flowchart LR
   A[data/raw CSV] --> B[Preprocessing tabulaire + texte]
   B --> C[Entraînement + évaluation]
   C --> D[Artefacts modèles + vectorizers]
   D --> E[API FastAPI]
   E --> F[Conteneur Docker]
   F --> G[Déploiement]
   E --> H[Monitoring: health, logs, métriques]
```

## Modèle

- Tâche : classification à 3 classes.
- Approche : comparaison de scénarios tabulaire seul vs multimodal tabulaire + texte.
- Familles de modèles explorées : baseline scikit-learn + candidats tree-based (XGBoost, LightGBM).
- Priorité métier : réduire les erreurs critiques sur la classe la plus risquée.

Référence de travail : notebooks/multimodal-classification.ipynb

## Résultats et métriques

Le projet suit aujourd'hui :

- F1 macro pour la qualité globale multiclasse.
- Recall de la classe critique pour l'alignement métier.
- Matrice de confusion pour analyser les erreurs à fort impact.

Seuils cibles définis dans le notebook :

- F1 macro >= 0.70
- Recall classe critique >= 0.80

Publication portfolio prévue :

- Tableau comparatif final des modèles dans reports/metrics/
- Figure de matrice de confusion dans reports/figures/
- Synthèse des arbitrages dans docs/runbooks/decision-log.md

## API

Statut : en cours d'implémentation.

Surface cible :

- GET /health : vérifier la disponibilité du service
- POST /predict : inférer la classe de délai de retour à l'emploi
- GET /metrics : exposer des indicateurs techniques

Objectif portfolio : documentation Swagger exploitable, avec des exemples de requêtes et de réponses.

## Docker et déploiement

Statut : structure prête, finalisation en cours.

- Dossiers cibles : infra/docker/, infra/compose/, infra/deployment/
- Étape suivante : exécution locale en une commande puis déploiement cloud (Render, Azure, Railway ou VM)

## Captures d'écran à inclure

Pour rendre la valeur visible en 30 secondes pour un recruteur :

- Swagger UI de l'API
- Exemple de réponse POST /predict
- Pipeline CI GitHub Actions au vert
- Écran du service déployé

Emplacement recommandé : reports/figures/

## État actuel

- Notebook principal de modélisation disponible
- Environnement Python 3.12 et dépendances ML/API préconfigurées
- CI GitHub Actions présente
- Documentation de gouvernance déjà structurée

### Avancement du projet

- [x] Structuration projet (data, src, tests, infra, docs, reports)
- [x] Base CI sur GitHub Actions
- [x] Gouvernance (decision log, conventions)
- [ ] Extraction complète du code notebook vers src/
- [ ] API FastAPI opérationnelle
- [ ] Tests exécutés en CI
- [ ] Docker / Docker Compose finalisés
- [ ] Déploiement cible

## Installation locale

Prérequis : Python 3.12

```bash
uv venv --python 3.12
uv pip install -r requirements.txt
```

## Structure du dépôt

- brief/: sujet et consignes
- data/: données brutes, intermédiaires et préparées
- src/: modules Python (data, features, modeling, evaluation, api, monitoring, utils)
- models/: artefacts modèles et vectorizers
- tests/: tests unitaires, intégration, API
- infra/: conteneurisation et déploiement
- docs/: architecture, model cards, RGPD/éthique, runbooks
- reports/: journal, métriques, soutenance
- .github/workflows/: CI

## Livrables certification conservés

Le projet conserve les livrables attendus pour la certification CISIA :

- Notebook final : notebooks/multimodal-classification.ipynb
- Support de soutenance : reports/soutenance/presentation-plan.md
- Journal de bord : reports/journal/journal-de-bord.ipynb
- Journal de décisions : docs/runbooks/decision-log.md

## Roadmap portfolio

1. Industrialiser le pipeline d'entraînement dans src/ (fit, evaluation, serialization).
2. Exposer le modèle via FastAPI (predict, health, metrics).
3. Ajouter tests Pytest (payload, inference, regression métriques).
4. Dockeriser l'API et documenter un run local one-command.
5. Publier résultats, captures et démo déployée.

## Note

Certains dossiers contiennent encore des .gitkeep : ils représentent des zones prévues, qui seront remplies au fur et à mesure de la finalisation.
