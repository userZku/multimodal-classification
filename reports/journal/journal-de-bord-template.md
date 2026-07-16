# Journal de bord - Certification CISIA

## Mode d'utilisation
- Ajouter une entrée par session de travail.
- Garder des traces factuelles : décisions, alternatives, raisons du choix.
- Mentionner explicitement les impacts métier, éthique et technique.

## Entrée type (copier-coller)

### Session
- Date :
- Durée :
- Objectif de la session :

### Actions réalisées
-
-
-

### Résultats observables
- Métriques / constats :
- Figures / tableaux produits :
- Fichiers modifiés :

### Décisions prises
- Décision 1 :
- Justification :
- Risque associé :

### Difficultés et résolutions
- Problème :
- Cause probable :
- Résolution appliquée :

### Éthique / RGPD / biais
- Point de vigilance identifié :
- Impact potentiel :
- Mesure de mitigation :

### Suite prévue
- Prochaine étape 1 :
- Prochaine étape 2 :

---

## Première entrée - Session du 16/07/2026

### Session
- Date : 16/07/2026
- Durée : environ 1h30
- Objectif de la session : structurer le dépôt pour la certification et préparer les livrables notebook + soutenance.

### Actions réalisées
- Lecture du brief en Markdown et vérification du contenu du DOCX.
- Vérification rapide du dataset (schéma, colonnes, présence de valeurs manquantes).
- Création d'une arborescence de travail complète : data, src, models, reports, docs, tests, infra, logs.
- Création de fichiers socle : README, plan notebook final, plan de présentation, workflow CI minimal, Makefile, .env.example.
- Insertion d'une cellule de sommaire de rendu certification en tête du notebook final.
- Création du template de journal de bord.

### Résultats observables
- Constats : structure de projet claire et prête pour l'exécution du cas d'usage de bout en bout.
- Figures / tableaux produits : aucun à ce stade (phase de cadrage et d'initialisation).
- Fichiers modifiés :
	- README.md
	- notebooks/PLAN_NOTEBOOK_FINAL.md
	- reports/soutenance/presentation-plan.md
	- .github/workflows/ci.yml
	- Makefile
	- .env.example
	- notebooks/multimodal-classification.ipynb
	- reports/journal/journal-de-bord-template.md

### Décisions prises
- Décision 1 : travailler avec un dépôt structuré, même si le rendu officiel reste notebook + PowerPoint.
- Justification : meilleure traçabilité, meilleure qualité de démarche, préparation plus simple de la soutenance.
- Risque associé : dispersion possible entre trop d'artefacts techniques et le livrable final.

### Difficultés et résolutions
- Problème : extraction directe du DOCX impossible via Expand-Archive sur extension .docx.
- Cause probable : contrainte de l'outil qui accepte explicitement le format .zip.
- Résolution appliquée : copie du .docx en .zip temporaire puis extraction et lecture XML.

### Éthique / RGPD / biais
- Point de vigilance identifié : présence d'une variable sensible (nationalité hors UE) pouvant induire un biais.
- Impact potentiel : discrimination algorithmique et non-conformité si usage non justifié.
- Mesure de mitigation : prévoir une comparaison explicite avec scénario sans variable sensible et argumenter le choix final.

### Suite prévue
- Prochaine étape 1 : démarrer l'EDA et le préprocessing documentés dans le notebook final.
- Prochaine étape 2 : entraîner les modèles sur les 4 scénarios et comparer les métriques demandées.

---

## Trace minimale attendue pour le jury
- Cadrage métier
- Qualité des données et preprocessing
- Comparaison des 4 scénarios
- Réduction des erreurs critiques (2 -> 0)
- Arbitrages finaux et limites
- Proposition d'industrialisation
