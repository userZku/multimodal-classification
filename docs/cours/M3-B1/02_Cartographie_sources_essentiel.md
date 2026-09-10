# Cartographie des sources hétérogènes — Mini-cours

> Brief associé : M3-B1
> Durée de lecture + pratique : ~20 min
> Pré-requis : entretien fictif fait, 3 sources fournies dans `data/`.

## Pourquoi cette techno ?

Après l'entretien, tu as 3 fichiers dans `data/` : un CSV, un JSON, un
fichier texte. Avant de plonger dans la pipeline, tu dois **comprendre
ce que tu as** sous la main : format, volume, fréquence, qualité, risques.

C'est une **cartographie**, pas un audit EDA fouillé. L'objectif n'est
**pas** de produire des stats descriptives complètes (M2 c'était ça) —
c'est de pouvoir **dire à un décideur** :

> *« On a 51 000 mesures IoT sur 1 mois, format CSV, qualité globale OK
> sauf 1 capteur défaillant sur Roubaix line 3. Risque RGPD : faible.
> Recommandation : à ingérer en priorité. »*

En 1 ligne par source. C'est ça la cartographie.

**Alternatives à connaître :**

| Approche | Quand l'utiliser ? |
|---|---|
| **Cartographie pandas + tableau** | Notre M3-B1 — rapide, transparent, lisible |
| **ydata-profiling** (rapport HTML) | Audit exhaustif M2 — overkill pour de la cartographie M3 |
| **Outils de data catalog** (DataHub, Amundsen) | Industrialisation M5+ — pas notre besoin |
| **DuckDB sur le folder** (interroger sans charger) | Bonus si tu te sens — sinon pandas suffit |

## Concepts clés

- **Schéma de la source** : colonnes / champs disponibles + leur type
  apparent. À lire avant tout `describe`.
- **Volume** : nombre de lignes (CSV / JSON) ou de lignes texte (logs).
  Donne aussi la taille fichier (parlante pour un décideur).
- **Fréquence** : à quelle cadence cette source est mise à jour ? Si tu
  ne sais pas, demande au client (ou note "à clarifier").
- **Qualité observée à l'œil nu** : manquants évidents, doublons, valeurs
  aberrantes, encodage chelou. Pas de stats fouillées — juste *« il y a
  un problème ici »*.
- **Risques RGPD** : variables sensibles directes (sex, race, age) **OU**
  identifiants pseudonymisés qui peuvent ré-identifier par croisement
  (cf. mini-cours 03).
- **Pertinence métier** : cette source répond-elle à la **demande
  reformulée** issue de l'entretien ? Si non, écarte-la (et argumente
  l'écart).

## Exemple minimal qui tourne

### Source 1 — CSV (capteurs IoT)

```python
import pandas as pd

df_iot = pd.read_csv("data/capteurs_iot.csv")
print(f"Volume : {len(df_iot):,} lignes × {len(df_iot.columns)} colonnes")
print(f"Période : {df_iot['timestamp'].min()} → {df_iot['timestamp'].max()}")
df_iot.info()
df_iot.describe()
print(df_iot.isna().sum())
print(df_iot['site'].value_counts())
```

### Source 2 — JSON (ERP)

```python
import json

with open("data/erp_export.json") as f:
    orders = json.load(f)

df_erp = pd.DataFrame(orders)
print(f"Volume : {len(df_erp):,} ordres")
df_erp.info()
print(df_erp['statut'].value_counts())
print(df_erp['ouvrier_id'].isna().sum())  # ⚠️ RGPD-sensible
```

### Source 3 — Texte (logs)

```python
from pathlib import Path

log_path = Path("data/logs_machines.log")
n_lines = sum(1 for _ in log_path.open())
print(f"Volume : {n_lines:,} lignes (~{log_path.stat().st_size / 1024:.0f} Ko)")

# Aperçu 5 lignes
with log_path.open() as f:
    for i, line in enumerate(f):
        if i >= 5:
            break
        print(line.rstrip())
```

**Pas besoin de parser** les logs en M3-B1 — juste observer leur format
et estimer la difficulté de parsing pour M3-B2.

## Exercice guidé (tâche 3 du brief)

Sur les 3 sources fournies, remplis le **tableau d'inventaire** suivant
dans `identification_sources.md` :

| Source | Format | Volume | Fréquence | Qualité observée | Risques RGPD | Pertinence métier |
|---|---|---|---|---|---|---|
| `capteurs_iot.csv` | ? | ? | ? | ? | ? | ? |
| `erp_export.json` | ? | ? | ? | ? | ? | ? |
| `logs_machines.log` | ? | ? | ? | ? | ? | ? |

**Solution attendue** (format type) :

| Source | Format | Volume | Fréquence | Qualité observée | Risques RGPD | Pertinence métier |
|---|---|---|---|---|---|---|
| `capteurs_iot.csv` | CSV | 51 k lignes (3.5 Mo) | continue (1 mois échantillonné) | 1 capteur défaillant Roubaix L3, ~1.5 % NaN, ~2 % doublons | Faible (pas de données perso) | **Haute** — alimente directement le modèle défauts qualité |
| `erp_export.json` | JSON | 2 k ordres (540 Ko) | par batch (1 export/jour ?) | 5 % `ouvrier_id` null, structure cohérente | **Moyen — `ouvrier_id` pseudonymisé** | **Haute** — contexte ordres de fabrication |
| `logs_machines.log` | Texte non structuré | 30 k lignes (1.8 Mo) | continue | Format `[ISO] SITE LINE EVENT: MSG`, parsing nécessaire | Faible | **Moyenne** — corroboration des erreurs capteurs |

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Faire un EDA fouillé (graphes, corrélations) | Tu sors du périmètre M3-B1 — c'est M3-B2 ou M4 |
| Vouloir parser les logs en regex complète | Tu y passes 3 h. Sur M3-B1, décris-les, c'est tout |
| Charger le CSV sans `low_memory=False` ou dtypes | Pandas devine mal — pas critique en cartographie, mais à noter pour M3-B2 |
| Ne pas regarder la période couverte | Tu rates si la source est obsolète ou trop fraîche |
| Lister les colonnes sans les comprendre | "Volume : 22 colonnes" → quoi ? Précise les 3-5 colonnes pertinentes |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| Tu n'arrives pas à charger le JSON | Probablement un JSON-lines (1 dict par ligne) — utilise `pd.read_json(path, lines=True)` |
| Le CSV charge avec tous les types `object` | Pandas n'a pas inféré — pas grave en cartographie, à fixer en M3-B2 |
| Les logs ont des encodage chelous | Spécifie `encoding="utf-8"` à l'ouverture |
| Tu sors avec un seul tableau de schéma au lieu d'une fiche par source | Tu confonds cartographie (par source) et inventaire schéma technique |

## Pour aller plus loin

- **Doc pandas — *IO tools*** : <https://pandas.pydata.org/docs/user_guide/io.html>
  (lecture CSV, JSON, fichiers texte)
- **Datacatalog d'industrie (concept)** : <https://en.wikipedia.org/wiki/Data_catalog>
- **DuckDB** (bonus pour requêter du Parquet/CSV sans charger) :
  <https://duckdb.org/docs/api/python/overview>

## Vérification (checklist apprenant)

- [ ] J'ai chargé les 3 sources avec pandas / file open
- [ ] Je sais le **volume**, le **format** et la **période** de chaque source
- [ ] J'ai repéré au moins **2 défauts qualité** sur les 3 sources
- [ ] J'ai identifié au moins **1 risque RGPD** sur les 3 sources
- [ ] J'ai rempli le **tableau d'inventaire** dans `identification_sources.md`
- [ ] **Je n'ai pas fait de feature engineering** (interdit en M3-B1)
