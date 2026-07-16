# Conventions de commit - Parcours IA ATOS

## Format

`type(scope): description`

- type : nature du changement
- scope : zone principale touchée
- description : imperative, <= 72 chars, in English, no trailing period

Exemple : `feat(api): add /predict endpoint with Pydantic validation`

## Types

- feat : nouvelle fonctionnalité
- fix : correction de bug
- docs : documentation
- refactor : réorganisation sans changement de comportement
- test : ajout/modification de tests
- chore : maintenance et configuration

## Scopes fréquents

- api
- model
- tests
- docker
- notebook
- eda
- training
- docs
- repo

## Règles de description

- utiliser l'impératif présent : add, fix, update, remove
- rester courte et explicite
- commencer en minuscule
- pas de point final
- rester en anglais

## Exemples

- `docs(readme): add uv setup commands`
- `chore(repo): initialize certification workspace structure`
- `feat(notebook): add session traceability section`
- `test(api): add health and predict endpoint tests`

## Anti-exemples

- `Update`
- `fix bug`
- `WIP`
- `feat: stuff`
- `feat(api): added new endpoint.`
