# Liens officiels — M2-B1

Dernière vérification : 2026-06-10

## Documentation officielle

- **scikit-learn — `ColumnTransformer`** : <https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html>
  - Sections recommandées : *Parameters*, *Examples* (mixed types)
  - État : ✅ vérifié le 2026-05-25
- **scikit-learn — `Pipeline`** : <https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html>
  - État : ✅ vérifié le 2026-05-25
- **scikit-learn — `OneHotEncoder`** : <https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html>
  - État : ✅ vérifié le 2026-05-25
- **scikit-learn — `OrdinalEncoder`** : <https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OrdinalEncoder.html>
  - État : ✅ vérifié le 2026-05-25
- **pandas — Parquet I/O** : <https://pandas.pydata.org/docs/user_guide/io.html#io-parquet>
  - État : ✅ vérifié le 2026-05-25
- **PyArrow — Parquet format** : <https://arrow.apache.org/docs/python/parquet.html>
  - État : ✅ vérifié le 2026-05-25
- **seaborn — tutorial** : <https://seaborn.pydata.org/tutorial.html>
  - État : ✅ vérifié le 2026-05-25

## Articles de référence

- **Gebru et al. (2018) — *Datasheets for Datasets*** : <https://arxiv.org/abs/1803.09010>
  - PDF court, lisible — le standard pour la datasheet.
- **Mitchell et al. (2019) — *Model Cards for Model Reporting*** : <https://arxiv.org/abs/1810.03993>
  - À garder en tête pour M7 (l'équivalent côté modèle).
- **Barocas, Hardt, Narayanan — *Fairness and Machine Learning*** : <https://fairmlbook.org/>
  - Livre gratuit en ligne. Chapitres 1-2 pour le contexte du
    disparate impact.

## Cadres réglementaires

- **CNIL — IA et données personnelles** : <https://www.cnil.fr/fr/intelligence-artificielle/ia-comment-etre-en-conformite-avec-le-rgpd>
  - Référentiel français RGPD appliqué à l'IA.
- **EEOC (US) — Employment Tests & Selection Procedures (règle des 4/5)** : <https://www.eeoc.gov/laws/guidance/employment-tests-and-selection-procedures>
  - Source de la règle des 4/5 (four-fifths rule).
- **AI Act européen** : <https://artificialintelligenceact.eu/the-act/>
  - Le texte de référence — sections sur les obligations de documentation
    pour les systèmes à haut risque.

## Datasets

- **UCI — German Credit Data (Statlog)** : <https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data>
  - Source officielle, doc en bas de page.

## Outils optionnels (bonus)

- **Fairlearn** : <https://fairlearn.org/main/user_guide/index.html>
  - Si tu veux pousser au-delà du calcul Pandas pour le DI.
- **ydata-profiling** : <https://github.com/ydataai/ydata-profiling>
  - Rapport HTML auto exhaustif d'un DataFrame — utile en démarrage, pas
    livrable tel quel à un client.

## Livres recommandés

- **Aurélien Géron — *Hands-On ML avec scikit-Learn (3ᵉ éd.)*** chapitre 2
  *End-to-end ML project* — section *Prepare the data for ML algorithms*.
- **Aggarwal — *Data Mining: The Textbook*** chapitre 2 *Data Preparation*
  (en anglais, plus académique).