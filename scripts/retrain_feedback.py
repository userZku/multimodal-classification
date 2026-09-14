"""
Script de réentraînement automatique avec garde-fous.

Flux :
1. Charger les feedbacks non consommés (used_for_training = 0).
2. Les joindre à leurs features via les logs de prédiction (request_id -> input).
3. Enrichir la base d'entraînement (historique - reference_set) avec ces lignes.
4. Entraîner un modèle candidat (même pipeline que src/modeling/train.py).
5. Évaluer candidat et production sur le même reference_set figé.
6. decide_promotion() tranche ; la décision est toujours journalisée.
7. Si promotion : remplacer models/best_model, marquer les feedbacks consommés.
   Si rejet : ne rien changer en production (marquer quand même consommé pour
   éviter de retraiter indéfiniment les mêmes feedbacks sans données nouvelles).

Sortie :
- exit 0 : skip (sous le seuil), rejet ou promotion (issues normales).
- exit 1 : erreur réelle (données manquantes, échec d'entraînement).
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import joblib
import pandas as pd
from sklearn.metrics import f1_score, recall_score
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import (
    BEST_MODEL_DIR,
    BEST_MODEL_METADATA_PATH,
    BEST_MODEL_PATH,
    CRITICAL_CLASS,
    DATA_DIR,
    PROJECT_ROOT,
    PRODUCTION_SCENARIO,
    RANDOM_STATE,
    TARGET_COL,
)
from src.features.preprocessing import build_model_frame
from src.modeling.train import build_training_pipeline, load_training_data
from src.api.feedback_store import FeedbackStore
from scripts.promotion import PromotionDecision, decide_promotion

LOG_DIR = PROJECT_ROOT / "logs" / "retraining"
LOG_DIR.mkdir(parents=True, exist_ok=True)
PREDICT_LOG_PATH = PROJECT_ROOT / "logs" / "inference" / "api_predict_requests.jsonl"
REFERENCE_SET_PATH = DATA_DIR / "reference_set.csv"

logger = logging.getLogger("retrain")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOG_DIR / "retrain.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())


def ensure_reference_set() -> pd.DataFrame:
    """Charge le reference_set figé, ou le crée à partir du holdout d'origine.

    Le reference_set n'entre JAMAIS dans l'entraînement (cf. DEC-027/028) :
    une fois créé, il est persisté et ne varie plus, même si le CSV source change.
    """
    if REFERENCE_SET_PATH.exists():
        return pd.read_csv(REFERENCE_SET_PATH)

    df = load_training_data()
    _, reference = train_test_split(
        df, test_size=0.2, random_state=RANDOM_STATE, stratify=df[TARGET_COL], shuffle=True
    )
    reference = reference.reset_index(drop=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    reference.to_csv(REFERENCE_SET_PATH, index=False)
    logger.info(f"reference_set.csv créé et figé ({len(reference)} lignes)")
    return reference


def load_training_base(reference_set: pd.DataFrame, dataset_path: str | None = None) -> pd.DataFrame:
    """Historique d'entraînement, expurgé des lignes déjà utilisées comme reference_set."""
    df = load_training_data(csv_path=dataset_path)
    if "usager_id" in df.columns and "usager_id" in reference_set.columns:
        df = df[~df["usager_id"].isin(reference_set["usager_id"])]
    return df.reset_index(drop=True)


def load_predict_log_inputs() -> dict[str, dict]:
    """Index request_id -> payload d'entrée, à partir des logs de /predict."""
    index: dict[str, dict] = {}
    if not PREDICT_LOG_PATH.exists():
        return index
    with PREDICT_LOG_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            request_id = event.get("request_id")
            input_payload = event.get("input")
            if request_id and input_payload:
                index[request_id] = input_payload
    return index


def join_feedbacks_to_features(
    feedbacks: list[dict], log_inputs: dict[str, dict]
) -> tuple[pd.DataFrame, list[str]]:
    """Jointure feedbacks ⋈ prod_scored (ici : logs de /predict) sur request_id.

    Retourne les lignes jointes avec succès (features + vraie classe) et la
    liste des request_id effectivement joints (seuls ceux-là seront marqués
    consommés : un feedback sans log correspondant reste disponible pour un
    prochain cycle, au cas où le log apparaîtrait plus tard).
    """
    rows = []
    joined_ids = []
    for fb in feedbacks:
        request_id = fb["request_id"]
        payload = log_inputs.get(request_id)
        if payload is None:
            logger.warning(f"Feedback {request_id} sans prédiction loguée correspondante — ignoré")
            continue
        row = dict(payload)
        row[TARGET_COL] = fb["true_label"]
        rows.append(row)
        joined_ids.append(request_id)

    if not rows:
        return pd.DataFrame(), []
    return pd.DataFrame(rows), joined_ids


def train_candidate(training_df: pd.DataFrame):
    """Entraîne un candidat avec la même pipeline que src/modeling/train.py."""
    y = training_df[TARGET_COL].copy()
    X_raw = training_df.drop(columns=[TARGET_COL]).copy()
    X_model = build_model_frame(X_raw)

    logger.info(f"Entraînement du candidat sur {len(X_model)} échantillons...")
    pipeline = build_training_pipeline(X_model.columns.tolist())
    pipeline.fit(X_model, y)
    return pipeline, X_model.columns.tolist()


def evaluate_model(pipeline, reference_set: pd.DataFrame, model_name: str) -> dict:
    """Évalue un pipeline sur le reference_set figé (f1_macro, recall_class_2)."""
    y_ref = reference_set[TARGET_COL].copy()
    X_ref_raw = reference_set.drop(columns=[TARGET_COL]).copy()
    X_ref_model = build_model_frame(X_ref_raw)

    y_pred = pipeline.predict(X_ref_model)
    f1_macro = f1_score(y_ref, y_pred, average="macro", zero_division=0)
    recall_class_2 = recall_score(
        y_ref, y_pred, labels=[CRITICAL_CLASS], average="macro", zero_division=0
    )
    logger.info(f"{model_name} — f1_macro={f1_macro:.4f}, recall_class_2={recall_class_2:.4f}")
    return {"f1_macro": float(f1_macro), "recall_class_2": float(recall_class_2)}


MODEL_HISTORY_DIR = BEST_MODEL_DIR / "history"
MODEL_HISTORY_LIMIT = 10
MIN_FEEDBACK_FOR_PROMOTION = 20


def _archive_current_model(reason: str) -> str:
    """Copie le modèle en production courant dans l'historique horodaté.

    Retourne le timestamp utilisé comme identifiant de la snapshot. Purge
    les entrées les plus anciennes au-delà de `MODEL_HISTORY_LIMIT`.
    """
    MODEL_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

    joblib.dump(joblib.load(BEST_MODEL_PATH), MODEL_HISTORY_DIR / f"model_{timestamp}.joblib")

    current_metadata = {}
    if BEST_MODEL_METADATA_PATH.exists():
        current_metadata = json.loads(BEST_MODEL_METADATA_PATH.read_text(encoding="utf-8"))
    current_metadata["archived_at"] = datetime.now(tz=timezone.utc).isoformat()
    current_metadata["archive_reason"] = reason
    (MODEL_HISTORY_DIR / f"metadata_{timestamp}.json").write_text(
        json.dumps(current_metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(f"Modèle en production archivé: history/model_{timestamp}.joblib ({reason})")

    _prune_model_history()
    return timestamp


def _prune_model_history() -> None:
    """Ne garde que les MODEL_HISTORY_LIMIT snapshots les plus récentes."""
    snapshots = sorted(MODEL_HISTORY_DIR.glob("model_*.joblib"))
    excess = len(snapshots) - MODEL_HISTORY_LIMIT
    for old_snapshot in snapshots[:max(excess, 0)]:
        timestamp = old_snapshot.stem.removeprefix("model_")
        old_snapshot.unlink(missing_ok=True)
        (MODEL_HISTORY_DIR / f"metadata_{timestamp}.json").unlink(missing_ok=True)


def list_model_history() -> list[dict]:
    """Liste les snapshots archivées, la plus récente en premier."""
    if not MODEL_HISTORY_DIR.exists():
        return []

    entries = []
    for snapshot in sorted(MODEL_HISTORY_DIR.glob("model_*.joblib"), reverse=True):
        timestamp = snapshot.stem.removeprefix("model_")
        metadata_path = MODEL_HISTORY_DIR / f"metadata_{timestamp}.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
        entries.append(
            {
                "timestamp": timestamp,
                "trained_at": metadata.get("trained_at"),
                "archived_at": metadata.get("archived_at"),
                "archive_reason": metadata.get("archive_reason"),
                "metrics": metadata.get("metrics", {}),
            }
        )
    return entries


def rollback_model(timestamp: str | None = None) -> dict:
    """Restaure une snapshot archivée comme modèle de production.

    Sans `timestamp`, restaure la snapshot la plus récente (rollback d'un
    cran). Le modèle actuellement en production est lui-même archivé avant
    la restauration, ce qui permet d'annuler un rollback (roll-forward) en
    rappelant cette fonction avec le timestamp voulu.

    Lève `FileNotFoundError` si aucune snapshot n'est disponible (ou si le
    `timestamp` demandé n'existe pas).
    """
    history = list_model_history()
    if not history:
        raise FileNotFoundError("Aucune snapshot disponible dans models/best_model/history/")

    target = history[0] if timestamp is None else next(
        (entry for entry in history if entry["timestamp"] == timestamp), None
    )
    if target is None:
        raise FileNotFoundError(f"Snapshot introuvable: {timestamp}")

    if BEST_MODEL_PATH.exists():
        _archive_current_model(reason="superseded_by_rollback")

    snapshot_path = MODEL_HISTORY_DIR / f"model_{target['timestamp']}.joblib"
    metadata_path = MODEL_HISTORY_DIR / f"metadata_{target['timestamp']}.json"

    joblib.dump(joblib.load(snapshot_path), BEST_MODEL_PATH)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["rolled_back_at"] = datetime.now(tz=timezone.utc).isoformat()
    metadata["rolled_back_from_timestamp"] = target["timestamp"]
    BEST_MODEL_METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(f"Rollback effectué vers la snapshot {target['timestamp']}")
    return {"restored_timestamp": target["timestamp"], "metrics": target["metrics"]}


def promote_candidate(pipeline, feature_columns: list[str], metrics: dict) -> None:
    """Remplace le modèle en production par le candidat promu.

    Le modèle actuellement en production (s'il existe) est archivé dans
    `models/best_model/history/` sous un nom horodaté avant d'être écrasé,
    ce qui permet un rollback ultérieur (cf. `rollback_model`). L'historique
    est borné à `MODEL_HISTORY_LIMIT` entrées pour éviter une croissance
    disque illimitée.
    """
    BEST_MODEL_DIR.mkdir(parents=True, exist_ok=True)

    if BEST_MODEL_PATH.exists():
        _archive_current_model(reason="superseded_by_promotion")

    joblib.dump(pipeline, BEST_MODEL_PATH)

    metadata = {
        "model_name": "xgboost",
        "scenario": PRODUCTION_SCENARIO,
        "trained_at": datetime.now(tz=timezone.utc).isoformat(),
        "features": feature_columns,
        "metrics": metrics,
        "promoted_from_feedback": True,
    }
    BEST_MODEL_METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(f"Modèle promu et sauvegardé: {BEST_MODEL_PATH}")


def _log_mlflow_retrain_run(
    *,
    trigger: str,
    training_rows: int,
    feedbacks_joined: int,
    candidate_metrics: dict,
    production_metrics: dict,
    decision,
    model_path: Path | None,
) -> str | None:
    """Journalise le cycle de retrain dans MLflow, promu ou rejeté.

    Ne doit jamais faire échouer le cycle de retrain : une indisponibilité du
    serveur MLflow est loggée en warning, pas propagée.
    """
    try:
        from src.modeling.train import _setup_mlflow

        mlflow, _ = _setup_mlflow()
        with mlflow.start_run(run_name="retrain-feedback") as run:
            mlflow.log_params(
                {
                    "trigger": trigger,
                    "training_rows": training_rows,
                    "feedbacks_joined": feedbacks_joined,
                    "promoted": decision.promote,
                }
            )
            mlflow.log_metrics({f"candidate_{k}": v for k, v in candidate_metrics.items()})
            mlflow.log_metrics({f"production_{k}": v for k, v in production_metrics.items()})
            mlflow.log_dict({"reason": decision.reason}, "decision.json")
            mlflow.set_tag("outcome", "promoted" if decision.promote else "rejected")
            if decision.promote and model_path is not None and model_path.exists():
                mlflow.log_artifact(str(model_path), artifact_path="model_artifacts")
            logger.info(f"Run MLflow enregistré: {run.info.run_id}")
            return run.info.run_id
    except Exception as exc:  # MLflow ne doit jamais bloquer la décision de retrain.
        logger.warning(f"MLflow indisponible, run non journalisé: {exc}")
        return None


def apply_sample_size_guard(decision: PromotionDecision, joined_count: int) -> PromotionDecision:
    """Rétrograde une promotion en rejet si trop peu de feedbacks l'appuient.

    Avec peu de feedbacks joints, un delta de métriques (recall_class_2
    mesuré sur ~18 échantillons de classe 2 dans le reference_set) reflète
    surtout le bruit d'échantillonnage/entraînement plutôt qu'un vrai signal
    apporté par les feedbacks. On ne fait confiance à une promotion qu'au-delà
    de MIN_FEEDBACK_FOR_PROMOTION feedbacks joints.
    """
    if not decision.promote or joined_count >= MIN_FEEDBACK_FOR_PROMOTION:
        return decision

    return PromotionDecision(
        promote=False,
        reason=(
            f"{decision.reason}\n"
            f"⚠ Promotion annulée par prudence : seulement {joined_count} feedback(s) joint(s) "
            f"< {MIN_FEEDBACK_FOR_PROMOTION} requis pour faire confiance à ce delta de métriques "
            f"(risque de bruit statistique/non-déterminisme d'entraînement, pas un vrai signal)."
        ),
    )


def run_retrain_cycle(
    min_feedback: int = 0,
    dataset_path: str | None = None,
    trigger: str = "manual",
) -> dict:
    """Exécute un cycle complet : jointure feedbacks, candidat, comparaison, décision.

    Utilisée à la fois par le cron (`min_feedback=200`, gate strict) et par
    l'endpoint `POST /retrain` (`min_feedback=0`, déclenchement manuel qui
    entraîne sur l'historique + les feedbacks déjà disponibles, sans attendre
    le seuil). Dans les deux cas, le candidat n'écrase la production que s'il
    est promu par `decide_promotion`.

    Retourne un dict {status, event_id, feedbacks_joined, candidate_metrics,
    production_metrics, reason} où status ∈ {"skipped", "promoted", "rejected"}.
    """
    event_id = f"retrain_{datetime.now(tz=timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"
    logger.info("=" * 70)
    logger.info(f"Début du cycle de réentraînement ({trigger}) — {event_id}")
    logger.info("=" * 70)

    store = FeedbackStore()
    counts = store.get_count()
    new_count = counts["new"]
    logger.info(f"Feedbacks: {counts['total']} total, {new_count} non consommés (seuil: {min_feedback})")

    if min_feedback > 0 and new_count < min_feedback:
        reason = f"{new_count} feedback(s) non consommé(s) < seuil {min_feedback}"
        logger.info(f"SKIP: {reason}. Rien à faire.")
        return {"status": "skipped", "event_id": event_id, "feedbacks_joined": 0, "reason": reason}

    reference_set = ensure_reference_set()
    training_base = load_training_base(reference_set, dataset_path=dataset_path)

    unconsumed = store.load_unconsumed()
    log_inputs = load_predict_log_inputs()
    feedback_df, joined_ids = join_feedbacks_to_features(unconsumed, log_inputs)

    if not joined_ids and dataset_path is None:
        reason = (
            "aucun nouveau feedback disponible et aucun dataset_path fourni : "
            "rien de nouveau à apprendre depuis le dernier entraînement"
        )
        logger.info(f"SKIP: {reason}.")
        return {"status": "skipped", "event_id": event_id, "feedbacks_joined": 0, "reason": reason}

    if joined_ids:
        logger.info(f"{len(joined_ids)}/{len(unconsumed)} feedbacks joints avec succès")
        training_df = pd.concat([training_base, feedback_df], ignore_index=True, sort=False)
    else:
        logger.info("Aucun feedback disponible — entraînement sur l'historique seul (dataset_path fourni).")
        training_df = training_base

    candidate, feature_columns = train_candidate(training_df)
    candidate_metrics = evaluate_model(candidate, reference_set, "Candidat")

    if BEST_MODEL_PATH.exists():
        production = joblib.load(BEST_MODEL_PATH)
        prod_metrics = evaluate_model(production, reference_set, "Production")
    else:
        logger.warning("Aucun modèle en production trouvé — le candidat sera comparé à zéro.")
        prod_metrics = {"f1_macro": 0.0, "recall_class_2": 0.0}

    decision = decide_promotion(candidate_metrics, prod_metrics)
    logger.info(f"Décision brute: {'PROMU' if decision.promote else 'REJETÉ'}\n{decision.reason}")

    decision = apply_sample_size_guard(decision, len(joined_ids))
    logger.info(f"Décision finale: {'PROMU' if decision.promote else 'REJETÉ'}\n{decision.reason}")

    if decision.promote:
        promote_candidate(candidate, feature_columns, candidate_metrics)
    else:
        logger.info("Candidat rejeté. Le modèle en production reste inchangé.")

    # Anti-spam : les feedbacks joints sont consommés qu'ils aient été promus ou
    # rejetés, sinon on retraiterait indéfiniment les mêmes données.
    if joined_ids:
        store.mark_as_used(joined_ids)

    mlflow_run_id = _log_mlflow_retrain_run(
        trigger=trigger,
        training_rows=len(training_df),
        feedbacks_joined=len(joined_ids),
        candidate_metrics=candidate_metrics,
        production_metrics=prod_metrics,
        decision=decision,
        model_path=BEST_MODEL_PATH,
    )

    result = {
        "status": "promoted" if decision.promote else "rejected",
        "event_id": event_id,
        "feedbacks_joined": len(joined_ids),
        "candidate_metrics": candidate_metrics,
        "production_metrics": prod_metrics,
        "reason": decision.reason,
        "mlflow_run_id": mlflow_run_id,
    }
    logger.info(f"Decision log:\n{json.dumps({**result, 'trigger': trigger}, indent=2, ensure_ascii=False)}")
    logger.info("=" * 70)
    logger.info("Fin du cycle de réentraînement")
    logger.info("=" * 70)
    return result


def retrain_with_feedbacks(min_feedback: int = 200) -> int:
    """Point d'entrée CLI (cron) : exit 0 sauf erreur réelle (skip/rejet compris)."""
    try:
        run_retrain_cycle(min_feedback=min_feedback, trigger="cron_feedback")
    except (FileNotFoundError, KeyError, ValueError, RuntimeError) as exc:
        logger.error(f"Erreur lors du réentraînement: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Réentraînement automatique avec feedbacks")
    parser.add_argument("--min-feedback", type=int, default=200)
    parser.add_argument(
        "--rollback",
        nargs="?",
        const="__latest__",
        default=None,
        metavar="TIMESTAMP",
        help="Restaure une snapshot archivée (la plus récente si aucun timestamp fourni)",
    )
    args = parser.parse_args()

    if args.rollback is not None:
        target = None if args.rollback == "__latest__" else args.rollback
        try:
            info = rollback_model(target)
            print(json.dumps(info, indent=2, ensure_ascii=False))
            raise SystemExit(0)
        except FileNotFoundError as exc:
            logger.error(f"Rollback impossible: {exc}")
            raise SystemExit(1)

    raise SystemExit(retrain_with_feedbacks(min_feedback=args.min_feedback))
