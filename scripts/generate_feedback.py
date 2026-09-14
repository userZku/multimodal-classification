"""Génère des feedbacks de test à partir des prédictions réellement loguées.

Lit `logs/inference/api_predict_requests.jsonl` (rempli par /predict, par
exemple via scripts/generate_traffic.py), puis simule des annotations
d'expert : le label envoyé est la classe prédite avec une probabilité
`--agreement`, sinon une autre classe (simule un désaccord/erreur du modèle).

Cela permet de tester la boucle complète sans attendre de vraies annotations :
    python scripts/generate_traffic.py --requests 300
    python scripts/generate_feedback.py --count 250
    python scripts/retrain_feedback.py --min-feedback 200

Usage:
    python scripts/generate_feedback.py --url http://localhost:8000 --count 250
    python scripts/generate_feedback.py --agreement 0.7 --count 100
"""

from __future__ import annotations

import argparse
import json
import random
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PREDICT_LOG_PATH = PROJECT_ROOT / "logs" / "inference" / "api_predict_requests.jsonl"


def _load_predict_events() -> list[dict]:
    if not PREDICT_LOG_PATH.exists():
        return []
    events = []
    with PREDICT_LOG_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def _simulate_true_label(predicted_class: int, agreement: float) -> int:
    if random.random() < agreement:
        return predicted_class
    other_classes = [c for c in (0, 1, 2) if c != predicted_class]
    return random.choice(other_classes)


def _post_feedback(url: str, request_id: str, true_label: int, timeout: float) -> int:
    payload = {
        "request_id": request_id,
        "true_label": true_label,
        "comments": "Feedback simulé (scripts/generate_feedback.py)",
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{url}/feedback",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except urllib.error.URLError as exc:
        print(f"  connection error: {exc}")
        return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Générer des feedbacks de test")
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--count", type=int, default=250, help="Nombre de feedbacks à envoyer")
    parser.add_argument(
        "--agreement",
        type=float,
        default=0.8,
        help="Probabilité que le feedback confirme la classe prédite (défaut: 0.8)",
    )
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    events = _load_predict_events()
    if not events:
        print(f"Aucun événement trouvé dans {PREDICT_LOG_PATH}.")
        print("Lancez d'abord: python scripts/generate_traffic.py --requests 300")
        return

    # Ne garder que les prédictions valides (status ok/a_revoir), avec request_id.
    valid_events = [
        e for e in events if e.get("output", {}).get("prediction") is not None and e.get("request_id")
    ]
    if not valid_events:
        print("Aucune prédiction valide trouvée dans les logs.")
        return

    random.shuffle(valid_events)
    sample = valid_events[: args.count]

    print(f"{len(sample)} feedbacks à envoyer (agreement={args.agreement})...")

    stats = {"created": 0, "conflict": 0, "error": 0}
    for event in sample:
        request_id = event["request_id"]
        predicted_class = event["output"]["prediction"]
        true_label = _simulate_true_label(predicted_class, args.agreement)

        status = _post_feedback(args.url, request_id, true_label, args.timeout)
        if status == 201:
            stats["created"] += 1
        elif status == 409:
            stats["conflict"] += 1
        else:
            stats["error"] += 1

    print(f"\nRésultat: {stats['created']} créés, {stats['conflict']} conflits, {stats['error']} erreurs")

    # Afficher le comptage final
    try:
        request = urllib.request.Request(f"{args.url}/feedback/count", method="GET")
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            counts = json.loads(response.read())
            print(f"Comptage feedbacks: {counts}")
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"Impossible de récupérer le comptage: {exc}")


if __name__ == "__main__":
    main()
