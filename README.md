# Multimodal Classification - Certification CISIA

## Objectif
Concevoir une solution IA de classification à 3 classes pour prédire le délai de retour à l'emploi à partir de données tabulaires et textuelles.

## Livrables officiels
- Notebook final : notebooks/multimodal-classification.ipynb
- Support de soutenance : reports/soutenance/presentation-plan.md

## Organisation du dépôt
- brief/ : sujet et consignes de certification
- data/ : données brutes, intermédiaires et préparées
   - data/raw/ : données sources non modifiées
   - data/interim/ : sorties de transformations intermédiaires
   - data/processed/ : jeux prêts pour l'entraînement et l'évaluation
- notebooks/ : notebook final et documents de cadrage
- reports/journal/ : journal de bord au format notebook
- reports/soutenance/ : éléments de préparation de la présentation
- src/ : code réutilisable (data, features, modeling, evaluation, api, monitoring, utils)
- models/ : artefacts modèles et vectorizers
- tests/ : tests unitaires, intégration, API
- infra/ : docker, compose, déploiement
- docs/ : architecture SI, RGPD/éthique, model cards, runbooks
- .github/workflows/ : configuration CI/CD

## Environnement
Le projet est configuré pour Python 3.12.

### Installation avec uv
1. Créer l'environnement

```bash
uv venv --python 3.12
```

2. Installer les dépendances

```bash
uv pip install -r requirements.txt
```

## Fichiers clés
- Notebook de rendu : notebooks/multimodal-classification.ipynb
- Journal de bord : reports/journal/journal-de-bord.ipynb
- Fiche de décisions : docs/runbooks/decision-log.md
- Workflow CI : .github/workflows/ci.yml
- Dépendances : requirements.txt

## Remarque
Ce dépôt sert d'espace de travail structuré. Le rendu attendu pour la certification reste centré sur le notebook final et le support de soutenance.

## Arborescence Git
Des fichiers .gitkeep sont placés dans les dossiers vides pour conserver la structure du dépôt tant que les artefacts n'ont pas encore été générés.
