# Boucle de Feedback Complète

**Statut:** ✅ Implémentée, testée et branchée sur `/retrain`  
**Date:** 2026-09-14

---

## Vue d'ensemble

La boucle de feedback automatise le cycle d'amélioration continue du modèle. Le
**même cycle** (`scripts/retrain_feedback.py::run_retrain_cycle`) est utilisé à
la fois par le cron et par le déclenchement manuel (`POST /retrain` / bouton
UI) — seul le seuil de garde change (200 pour le cron, 0 pour un appel manuel) :

```
Utilisateurs en production
        ↓
  Prédictions API + request_id loggés
        ↓
Annotations collectées (POST /feedback, request_id validé par prédiction loguée)
        ↓
  SQLite feedbacks.db (used_for_training)
        ↓
Cron toutes les 6h (≥200 feedbacks) OU clic manuel /retrain (0 feedback suffit)
        ↓
  Jointure feedbacks ⋈ logs de /predict -> features + vraie classe
        ↓
  Réentraîner un modèle candidat (historique - reference_set + feedbacks joints)
        ↓
  Évaluer candidat ET production sur le même reference_set figé (section 4.1 du notebook)
        ↓
  decide_promotion() : recall_class_2 prioritaire, f1_macro tolérant
        →      →
  PROMU   REJETÉ
   ↓        ↓
 Remplace  Log +
model.joblib rien (normal)
```

---

## 1. Endpoints Feedback

### `POST /feedback` — Enregistrer une annotation

**Endpoint:** `POST /feedback`

**Payload:**
```json
{
  "request_id": "req_20260914_120000_abc123",
  "true_label": 1,
  "comments": "Usager embauché après 30 jours"
}
```

**Réponses:**
- `201 Created` : feedback stocké (ou idempotent si identique)
- `404 Not Found` : `request_id` inconnu — aucune prédiction loguée ne lui correspond
- `409 Conflict` : même request_id avec label différent → arbitrage humain requis
- `422 Unprocessable Entity` : label hors {0, 1, 2} ou champ manquant

**Exemple:**
```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_20260914_120000_abc123",
    "true_label": 1,
    "comments": "Embauche confirmée"
  }'
```

### `GET /feedback/count` — Comptage des feedbacks

**Endpoint:** `GET /feedback/count`

**Réponse:**
```json
{
  "total": 250,
  "new": 47
}
```

- `total` : tous les feedbacks stockés
- `new` : ceux pas encore consommés par un réentraînement

### `GET /feedback/health` — Santé de l'endpoint

**Endpoint:** `GET /feedback/health`

**Réponse:**
```json
{
  "status": "ok",
  "total_feedbacks": 250,
  "unconsumed_feedbacks": 47
}
```

---

## 2. Stockage SQLite

**Fichier:** `data/feedbacks.db`

**Schéma:**
```sql
CREATE TABLE feedbacks (
    request_id TEXT PRIMARY KEY,
    true_label INTEGER NOT NULL CHECK (true_label IN (0, 1, 2)),
    comments TEXT,
    created_at TEXT NOT NULL,
    used_for_training INTEGER NOT NULL DEFAULT 0
);
```

**Clés:**
- `request_id` (PK) : identifie la prédiction associée
- `true_label` : classe réelle (0, 1 ou 2)
- `comments` : annotation optionnelle
- `created_at` : timestamp ISO 8601
- `used_for_training` : 0/1, marqué après réentraînement réussi

**Politique de doublon:**
- Même request_id + **même** label → idempotent (rejeu réseau OK)
- Même request_id + label **différent** → 409 Conflict (vérité terrain contradictoire)

**Implémentation:** `src/api/feedback_store.py` (classe `FeedbackStore`), utilisée
directement par `src/api/main.py` (pas de package/routeur séparé, pour rester
cohérent avec l'organisation existante de l'API).

---

## 3. Trigger Cron (Réentraînement)

**Fichier:** `infra/cron/retrain.crontab`

**Expression:** `0 */6 * * * ...` (toutes les 6 heures)

**Vérifier sur:** https://crontab.guru/

**Guard-rail :** Le script `retrain_feedback.py` sort en **succès (exit 0)** s'il y a < 200 feedbacks non consommés. Ce n'est pas une erreur — c'est une garde-seuil normale.

### Installer sur Linux/macOS
```bash
crontab -e
# Copier/coller les lignes de infra/cron/retrain.crontab
```

### Sur Windows
Utiliser Task Scheduler avec une action PowerShell :
```powershell
cd C:\Users\YourUser\multimodal-classification
.venv\Scripts\python scripts\retrain_feedback.py --min-feedback 200
```

### Dans Docker Compose

Le cron hôte ci-dessus ne s'applique pas tel quel à l'intérieur des conteneurs
(pas de daemon cron, pas de `.venv` dans l'image `python:3.12-slim`). La stack
(`docker-compose.yml`) inclut donc un service dédié `retrain-cron` qui exécute
une boucle `sh` (`while true; do python scripts/retrain_feedback.py ...; sleep
21600; done`) toutes les 6h, avec la même image que le service `api`.

**Prérequis pour que ça fonctionne** :
- `infra/docker/Dockerfile` doit copier `scripts/` dans l'image (`COPY scripts
  ./scripts`) — sans ça, `src/api/main.py` (qui importe
  `scripts.retrain_feedback`) ne démarre même pas.
- `api` et `retrain-cron` doivent partager les mêmes volumes `./data`,
  `./models`, `./logs` pour voir les mêmes feedbacks, le même
  `reference_set.csv` et le même modèle en production.

**⚠️ Limite connue — rechargement du modèle non automatique entre conteneurs :**
si `retrain-cron` promeut un candidat, il écrase bien
`models/best_model/model.joblib` sur le volume partagé, mais le conteneur
`api` a chargé `PIPELINE` **en mémoire au démarrage** et ne surveille pas ce
fichier. Une promotion effectuée par `retrain-cron` n'est donc **pas prise en
compte par l'API tant qu'on n'a pas** :
- soit redémarré le conteneur `api` (`docker compose restart api`),
- soit appelé manuellement `POST /retrain` sur l'API (qui, lui, appelle
  `reload_artifacts()` après une promotion).

Aucun mécanisme de rechargement automatique (watcher de fichier, signal inter-
conteneurs) n'est implémenté à ce stade — c'est un TODO explicite, pas un bug
silencieux.

---

## 4. Réentraînement Automatique

**Script:** `scripts/retrain_feedback.py` — fonction centrale `run_retrain_cycle()`,
appelée aussi bien par le cron (`retrain_with_feedbacks`, seuil ≥200) que par
`POST /retrain` dans `src/api/main.py` (seuil = 0, déclenchement manuel).

**Flux:**
1. Charger les feedbacks non consommés (`used_for_training = 0`).
2. Les joindre à leurs features via `logs/inference/api_predict_requests.jsonl`
   (`join_feedbacks_to_features` : un feedback sans log correspondant est
   ignoré, pas planté — il reste disponible pour un prochain cycle).
3. Charger/créer le `reference_set` figé (`ensure_reference_set`, cf. section 5)
   et l'historique d'entraînement expurgé de ces lignes (`load_training_base`).
4. Entraîner un candidat (même pipeline que `src/modeling/train.py`) sur
   historique + feedbacks joints.
5. Évaluer candidat **et** production sur le **même** `reference_set`.
6. `decide_promotion()` tranche ; la décision est **toujours** journalisée.
7. Si promu : remplacer `models/best_model/model.joblib` (ancien sauvegardé en
   `model_previous.joblib`) et marquer les feedbacks joints comme consommés.
   Si rejeté : ne rien changer, marquer quand même consommé (anti-boucle).

**Commande manuelle (CLI/cron) :**
```bash
python scripts/retrain_feedback.py --min-feedback 200
```

**Déclenchement via l'API (pas de seuil, utilise les feedbacks déjà là) :**
```bash
curl -X POST http://localhost:8000/retrain -H "Content-Type: application/json" -d '{"trigger": "ui_manual"}'
# -> {"status": "promoted"|"rejected"|"skipped", "event_id": ..., "metrics": {...}, "reason": "..."}
```

**Générer des feedbacks de test à partir du trafic réel :**
```bash
python scripts/generate_traffic.py --requests 300      # remplit les logs de /predict
python scripts/generate_feedback.py --count 220         # annote 220 prédictions réellement loguées
python scripts/retrain_feedback.py --min-feedback 200
```

**Logs:** `logs/retraining/retrain.log`

**MLflow:** chaque cycle (promu ou rejeté) crée un run `retrain-feedback` dans
la même expérience que `src/modeling/train.py` — params (`trigger`,
`training_rows`, `feedbacks_joined`, `promoted`), métriques
(`candidate_*`/`production_*`), et le fichier modèle en artefact si promu. Une
indisponibilité de MLflow est journalisée en warning mais ne bloque jamais la
décision de promotion.

---

## 5. Politique de Promotion

**Document de référence:** `docs/runbooks/decision-log.md` (DEC-027/028)

### Règle (en français d'abord)

> **On promeut le candidat si :**
> 1. `recall_class_2` candidat ≥ `recall_class_2` production - 0.005 (tolérance 0.5%)
> 2. **ET** perte en `f1_macro` ≤ 0.01 (tolérance 1%), sauf si le gain de
>    `recall_class_2` dépasse 0.01 (il compense alors la perte de F1).
>
> **Sinon : rejet.**

`recall_class_2` est la métrique critique du projet (classe 2 = risque de
retour à l'emploi > 12 mois, cf. `config.CRITICAL_CLASS`) — un défaut de
détection sur cette classe coûte plus cher métier qu'un faux positif.

### Métriques clés

| Métrique | Rôle | Tolérance |
|---|---|---|
| `recall_class_2` | **CRITIQUE** : détecter les risques de longue durée | -0.005 |
| `f1_macro` | Équilibre général | -0.01 |

### Exemple

```python
from scripts.promotion import decide_promotion

prod = {"f1_macro": 0.6138, "recall_class_2": 0.6426}
cand = {"f1_macro": 0.6070, "recall_class_2": 0.6540}

decision = decide_promotion(cand, prod)
print(f"Promu: {decision.promote}")
print(f"Raison:\n{decision.reason}")
# Résultat : PROMU (recall gagne +1.14%, f1 perd -0.68% mais dans la tolérance)
```

### Historique et rollback

Chaque promotion **archive** le modèle qu'elle remplace dans
`models/best_model/history/` (`model_<timestamp>.joblib` +
`metadata_<timestamp>.json`), borné aux `MODEL_HISTORY_LIMIT` (10) snapshots
les plus récentes. Un rollback archive lui-même l'état courant avant de
restaurer une snapshot — un rollback peut donc être annulé (roll-forward) en
rappelant la commande avec le timestamp voulu.

```bash
# Lister les snapshots disponibles
curl http://localhost:8000/models/history

# Revenir à la snapshot la plus récente
curl -X POST http://localhost:8000/rollback -H "Content-Type: application/json" -d "{}"

# Revenir à une snapshot précise
curl -X POST http://localhost:8000/rollback -H "Content-Type: application/json" -d "{\"timestamp\": \"20260914T120000123456Z\"}"

# Équivalent en CLI (hors API)
python scripts/retrain_feedback.py --rollback
python scripts/retrain_feedback.py --rollback 20260914T120000123456Z
```

Un bouton **"Rollback modèle"** dans l'UI (`app/ui`) appelle `POST /rollback`
(confirmation requise, restaure la snapshot la plus récente).

---

## 6. Tests

### Tester la politique de promotion
```bash
.venv\Scripts\python -m pytest tests/test_feedback_loop.py::TestPromotionPolicy -v
```
**Résultat:** 6/6 ✅

### Tester les endpoints feedback
```bash
.venv\Scripts\python -m pytest tests/test_feedback_loop.py::TestFeedbackEndpoint -v
```
**Résultat:** 7/7 ✅ (inclut le cas `request_id` inconnu → 404)

### Tests d'intégration (jointure, reference_set, cycle complet)
```bash
.venv\Scripts\python -m pytest tests/integration/test_feedback_integration.py -v
```
**Résultat:** 5/5 ✅

### Tous les tests du projet
```bash
.venv\Scripts\python -m pytest tests/ -v
```
**Résultat:** 30/30 ✅

---

## 7. Intégration GitHub Actions

**Fichier:** `.github/workflows/retrain.yml`

**Workflow:**
- Trigger manuel (`workflow_dispatch`, paramètre `min_feedback`) pour démo
- Trigger cron (planifié quotidien)
- Exécute les tests puis `scripts/retrain_feedback.py`
- Détecte un tag Git créé (candidat promu) pour déclencher build + push GHCR
- Notifications Slack (promu / rejeté / erreur) si `SLACK_WEBHOOK` est configuré

---

## 8. Checklist Déploiement

- [x] Endpoints `/feedback` créés et testés (404/409/422/201)
- [x] SQLite `feedbacks.db` schéma + politique de doublon
- [x] Script `retrain_feedback.py` opérationnel (`run_retrain_cycle` réutilisé par le cron ET par `POST /retrain`)
- [x] Politique de promotion écrite + testée (`recall_class_2` prioritaire)
- [x] Crontab `retrain.crontab` documentée + service Docker `retrain-cron`
- [x] Tests unitaires et d'intégration (30/30 ✅)
- [x] GitHub Actions workflow de retrain (`retrain.yml`)
- [x] Script `generate_feedback.py` pour tester la boucle sans annotation manuelle
- [ ] Rechargement automatique du modèle entre conteneurs (`api` vs `retrain-cron`) — TODO, cf. section 3
- [ ] Monitoring des feedbacks (panel Grafana dédié, optionnel)

---

## 9. Exemple Complet

### Simuler du trafic + feedbacks + retrain

```bash
# 1. Générer du trafic (remplit logs/inference/api_predict_requests.jsonl)
python scripts/generate_traffic.py --requests 300

# 2. Générer des feedbacks à partir des prédictions réellement loguées
#    (simule un accord expert à 80% avec la classe prédite)
python scripts/generate_feedback.py --count 220 --agreement 0.8

# 3. Vérifier le comptage
curl http://localhost:8000/feedback/count
# -> {"total": 220, "new": 220}

# 4. Déclencher le retrain (cron/CLI, gateé par le seuil)
python scripts/retrain_feedback.py --min-feedback 200

# ... ou via l'API (pas de seuil, utilise les feedbacks déjà disponibles)
curl -X POST http://localhost:8000/retrain -H "Content-Type: application/json" -d '{"trigger": "ui_manual"}'

# 5. Consulter le log
Get-Content logs/retraining/retrain.log -Tail 50
```

---

## 10. Troubleshooting

| Symptôme | Cause | Solution |
|---|---|---|
| `/feedback` retourne 404 | `request_id` jamais logué par `/predict` | Vérifier `logs/inference/api_predict_requests.jsonl`, ou appeler `/predict` avant `/feedback` |
| `/feedback` retourne 409 sur feedbacks valides | Conflit de request_id / label | Vérifier les annotations existantes avec `sqlite3 data/feedbacks.db "SELECT * FROM feedbacks WHERE request_id = '...'"` |
| Retrain démarre à chaque cron | `used_for_training` pas marqué | Vérifier que `mark_as_used()` est appelé après le cycle (promu ou rejeté) |
| Candidat toujours promu | Pas de comparaison à production | Vérifier que `BEST_MODEL_PATH` pointe vers le modèle en place |
| Candidat toujours rejeté | Jeu d'entraînement plus pauvre que celui de la production (le `reference_set` est exclu du train) | Comparer `len(training_df)` vs la taille de l'historique d'origine |
| `ModuleNotFoundError: No module named 'scripts'` en lançant le script directement | Exécution hors du répertoire projet | Le script insère déjà `PROJECT_ROOT` dans `sys.path` ; vérifier que `infra/docker/Dockerfile` copie bien `scripts/` si le problème apparaît en conteneur |
| Une promotion de `retrain-cron` n'apparaît pas dans l'API (Docker) | Le conteneur `api` ne recharge pas le modèle automatiquement | Redemarrer `api` (`docker compose restart api`) ou appeler `POST /retrain` |

---

## Références

- **Détection de dérive** : `docs/cours/M6-B1/` — dérive, calibration, recommandation
- **Boucle de feedback** : `docs/cours/M6-B2/` — feedback, stockage, trigger, réentraînement, promotion
- **Politique écrite** : `docs/runbooks/decision-log.md` (DEC-027/028)
- **Décisions tracées** : `docs/runbooks/decision-log.md` (DEC-026/027/028)
- **Notebook de certif** : section 4.1 (split figé = `reference_set`), section 9.2/9.3 (protocole documenté)
- **Implémentation API** : `src/api/main.py` (endpoints `/feedback*` et `/retrain`), `src/api/feedback_store.py` (stockage SQLite)
- **Implémentation cycle** : `scripts/retrain_feedback.py` (`run_retrain_cycle`), `scripts/promotion.py` (fonction pure testable)
- **Génération de trafic/feedback de test** : `scripts/generate_traffic.py`, `scripts/generate_feedback.py`

---

**Prochaines étapes:**
1. [ ] Rechargement automatique du modèle côté API après une promotion effectuée par `retrain-cron` (watcher de fichier ou signal inter-conteneurs)
2. [ ] Ajouter un panel Grafana dédié au volume de feedbacks
3. [ ] Itérer sur les seuils (`min-feedback`, tolérances de `decide_promotion`) après plusieurs cycles réels
