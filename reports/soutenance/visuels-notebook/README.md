# Visuels exportés du notebook

Ces 13 PNG proviennent des sorties déjà enregistrées dans `notebooks/multimodal-classification.ipynb`. Ils sont prêts à être examinés et réutilisés dans le PowerPoint ; les chiffres doivent rester cohérents avec le notebook.

| Fichier(s) | Contenu |
|---|---|
| `qualite-donnees.png`, `qualite-donnees-2.png` | Contrôles de qualité et de complétude des données. |
| `distributions-variables.png`, `distributions-variables-2.png` | Distributions de variables explorées. |
| `distribution-classes.png` | Répartition des trois classes cibles. |
| `relations-variables-cible.png` et suffixes `-2` à `-4` | Relations entre variables et cible. À commenter sans interprétation causale. |
| `matrice-confusion-S2-XGBoost.png` | Matrice du modèle final S2 + XGBoost sur le test : 10 erreurs 2→0 et 3 erreurs 0→2. |
| `importance-features-XGBoost.png` | `feature_importances_` XGBoost, avec vues par variable et famille. **Ce n'est pas SHAP.** |
| `analyse-erreurs.png` | Analyse exploratoire des erreurs et d'une règle simple de revue. Vérifier son seuil avant réutilisation. |
| `seuil-revue-OOF.png` | Comparaison des taux d'escalade et de couverture critique selon le seuil sur OOF. |

Avant publication, vérifier lisibilité, dénominateurs, légendes et cohérence avec les résultats courants. Les graphiques agrégés ne prouvent ni causalité, ni absence de biais, ni correction effective par un conseiller.