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
