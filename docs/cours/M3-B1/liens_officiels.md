# Liens officiels — M3-B1

Dernière vérification : 2026-06-10

## Documentation officielle

- **pandas — IO tools** : <https://pandas.pydata.org/docs/user_guide/io.html>
  - État : ✅ vérifié le 2026-05-26
- **Mermaid — Flowchart syntax** : <https://mermaid.js.org/syntax/flowchart.html>
  - État : ✅ vérifié le 2026-05-26
- **Mermaid Live Editor** : <https://mermaid.live>
  - État : ✅ vérifié le 2026-05-26
- **GitHub — Creating diagrams in Markdown** : <https://docs.github.com/fr/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams>
  - État : ✅ vérifié le 2026-05-26

## Cadres réglementaires

- **CNIL — L'anonymisation des données personnelles** : <https://www.cnil.fr/fr/technologies/lanonymisation-de-donnees-personnelles>
- **CNIL — Comprendre le RGPD** : <https://www.cnil.fr/fr/comprendre-le-rgpd>
- **CNIL — Pseudonymisation** : <https://www.cnil.fr/fr/tag/pseudonymisation>
- **RGPD considérant 26** : <https://gdpr-info.eu/recitals/no-26/>
  (définit ce qu'est "anonyme" vs "pseudonymisé")
- **AI Act européen** : <https://artificialintelligenceact.eu/the-act/>

## Articles de référence

- **Erika Hall — Just Enough Research** : <https://www.mulebooks.com/just-enough-research>
  (intro entretien utilisateur)
- **Steve Portigal — Interviewing Users** : référence métier UX
- **Atlassian — Writing meaningful technical documents** : <https://www.atlassian.com/work-management/knowledge-sharing/documentation>

## Outils optionnels

- **DuckDB** (interroger CSV/Parquet sans tout charger) : <https://duckdb.org/docs/api/python/overview>
- **ydata-profiling** (rapport HTML auto — overkill ici, à connaître) : <https://github.com/ydataai/ydata-profiling>

## Bonus RAG — préparation (mission étoile M3-B1)

- **ChromaDB** : <https://docs.trychroma.com/>
- **sentence-transformers** (embeddings locaux, aucune clé API) : <https://www.sbert.net/>
- **all-MiniLM-L6-v2** (modèle d'embedding) : <https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2>
  - Préparation seulement (loader **fait main**, pas de LangChain ; corpus `.md`, pas de pypdf). RAG complet en M7-B2.
