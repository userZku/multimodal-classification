"""Generate synthetic traffic against the API to populate Prometheus/Grafana.

Sends a mix of /predict, /health and /history requests (plus occasional
malformed payloads and an optional /retrain trigger) so the Grafana
dashboards have realistic data to display (latency, status codes, counters).

Valid payloads are drawn from the held-out test split (never seen during
training) or generated synthetically, so the observed confidence distribution
is not optimistically biased.

Usage:
    python scripts/generate_traffic.py --url http://localhost:8000 --requests 300
    python scripts/generate_traffic.py --duration 120 --rps 2 --error-rate 0.05
"""

from __future__ import annotations

import argparse
import json
import random
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
TARGET_COL = "classe_retour_emploi"
RANDOM_STATE = 42

TEXT_SAMPLES = [
    "Compétences à réactualiser sur les outils numériques. Motivation correcte.",
    "Cumul de difficultés. Pas de moyen de transport et garde d'enfants complexe.",
    "Excellente présentation, compétences techniques à jour. Reprise rapide visée.",
    "Candidat très dynamique, mobilité nationale validée. Projet clair.",
    "Profil autonome, recherche active, aucun frein périphérique identifié.",
    "Problème ponctuel de mobilité géographique. Zone mal desservie.",
    "Perte de confiance importante. Risque d'exclusion, barrière de la langue.",
    "Freins périphériques majeurs. Situation d'illettrisme numérique constatée.",
]
DIPLOMAS = ["Sans diplôme", "Bac", "Bac+2", "Bac+5"]
ROME_CODES = ["M1805", "G1302", "M1705", "A1203", "N1301", "K1304", "D1503", "J1506"]


def _load_reference_rows() -> pd.DataFrame | None:
    """Return only the held-out test split, so the model scores unseen profiles."""
    csv_files = sorted(DATA_RAW_DIR.glob("*.csv"))
    if not csv_files:
        return None

    df = pd.read_csv(csv_files[0])
    if TARGET_COL not in df.columns:
        return df

    _, holdout = train_test_split(
        df,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=df[TARGET_COL],
        shuffle=True,
    )
    return holdout.reset_index(drop=True)


def _random_payload(reference: pd.DataFrame | None, real_ratio: float) -> dict:
    if reference is not None and random.random() < real_ratio:
        row = reference.sample(1).iloc[0]
        return {
            "usager_id": f"TRAFFIC_{random.randint(1, 999999)}",
            "age": None if pd.isna(row.get("age")) else float(row["age"]),
            "niveau_diplome": None
            if pd.isna(row.get("niveau_diplome"))
            else str(row["niveau_diplome"]),
            "anciennete_poste_ans": None
            if pd.isna(row.get("anciennete_poste_ans"))
            else float(row["anciennete_poste_ans"]),
            "code_rome_vise": None
            if pd.isna(row.get("code_rome_vise"))
            else str(row["code_rome_vise"]),
            "est_allocataire": None
            if pd.isna(row.get("est_allocataire"))
            else int(row["est_allocataire"]),
            "departement_insee": None
            if pd.isna(row.get("code_insee_commune"))
            else str(row["code_insee_commune"])[:2],
            "synthese_entretien": str(row["synthese_entretien"]),
        }

    return {
        "usager_id": f"TRAFFIC_{random.randint(1, 999999)}",
        "age": round(random.uniform(18, 62), 1),
        "niveau_diplome": random.choice(DIPLOMAS),
        "anciennete_poste_ans": round(random.uniform(0, 20), 1),
        "code_rome_vise": random.choice(ROME_CODES),
        "est_allocataire": random.choice([0, 1]),
        "departement_insee": f"{random.randint(1, 95):02d}",
        "synthese_entretien": random.choice(TEXT_SAMPLES),
    }


def _malformed_payload() -> dict:
    # Missing the required synthese_entretien field or wrong types on purpose.
    choices = [
        {"usager_id": "BAD_REQUEST", "age": "not_a_number"},
        {"usager_id": "BAD_REQUEST", "synthese_entretien": 123},
        {"usager_id": "BAD_REQUEST", "synthese_entretien": "test", "age": 200},
        {"usager_id": "BAD_REQUEST", "extra_unknown_field": "x", "synthese_entretien": "test"},
    ]
    return random.choice(choices)


def _post(url: str, path: str, payload: dict, timeout: float) -> tuple[int, float]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{url}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status_code = response.status
    except urllib.error.HTTPError as exc:
        status_code = exc.code
    except urllib.error.URLError as exc:
        print(f"  connection error on {path}: {exc}")
        return 0, time.perf_counter() - start
    elapsed = time.perf_counter() - start
    return status_code, elapsed


def _get(url: str, path: str, timeout: float) -> tuple[int, float]:
    request = urllib.request.Request(f"{url}{path}", method="GET")
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status_code = response.status
    except urllib.error.HTTPError as exc:
        status_code = exc.code
    except urllib.error.URLError as exc:
        print(f"  connection error on {path}: {exc}")
        return 0, time.perf_counter() - start
    elapsed = time.perf_counter() - start
    return status_code, elapsed


def run(
    url: str,
    total_requests: int | None,
    duration: float | None,
    rps: float,
    error_rate: float,
    real_ratio: float,
    retrain_every: int | None,
    timeout: float,
) -> None:
    reference = _load_reference_rows()
    if reference is None:
        print("No CSV found in data/raw, using fully synthetic payloads.")
    else:
        print(f"Sampling from {len(reference)} held-out rows (test split).")

    sent = 0
    start_time = time.perf_counter()

    while True:
        if total_requests is not None and sent >= total_requests:
            break
        if duration is not None and (time.perf_counter() - start_time) >= duration:
            break

        if random.random() < error_rate:
            payload = _malformed_payload()
        else:
            payload = _random_payload(reference, real_ratio)

        status_code, elapsed = _post(url, "/predict", payload, timeout)
        print(f"[{sent + 1}] POST /predict -> {status_code} ({elapsed * 1000:.0f} ms)")

        # occasionally hit the other endpoints so their metrics move too.
        if sent % 5 == 0:
            status_code, elapsed = _get(url, "/health", timeout)
            print(f"    GET /health -> {status_code} ({elapsed * 1000:.0f} ms)")
        if sent % 8 == 0:
            status_code, elapsed = _get(url, "/history?limit=20", timeout)
            print(f"    GET /history -> {status_code} ({elapsed * 1000:.0f} ms)")

        if retrain_every and sent > 0 and sent % retrain_every == 0:
            status_code, elapsed = _post(url, "/retrain", {"trigger": "traffic_script"}, timeout=60.0)
            print(f"    POST /retrain -> {status_code} ({elapsed:.1f} s)")

        sent += 1
        time.sleep(max(0.0, 1.0 / rps))

    print(f"Done. Sent {sent} requests in {time.perf_counter() - start_time:.1f}s.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://localhost:8000", help="Base API URL.")
    parser.add_argument("--requests", type=int, default=None, help="Total number of /predict calls.")
    parser.add_argument("--duration", type=float, default=None, help="Run duration in seconds instead of a fixed count.")
    parser.add_argument("--rps", type=float, default=2.0, help="Target requests per second.")
    parser.add_argument("--error-rate", type=float, default=0.1, help="Fraction of requests sent as malformed payloads (0-1).")
    parser.add_argument("--real-ratio", type=float, default=0.5, help="Fraction of valid payloads drawn from the held-out test split (rest is synthetic).")
    parser.add_argument("--retrain-every", type=int, default=None, help="Trigger /retrain every N predict requests.")
    parser.add_argument("--timeout", type=float, default=5.0, help="Per-request timeout in seconds.")
    args = parser.parse_args()

    if args.requests is None and args.duration is None:
        args.requests = 200

    run(
        url=args.url.rstrip("/"),
        total_requests=args.requests,
        duration=args.duration,
        rps=args.rps,
        error_rate=args.error_rate,
        real_ratio=args.real_ratio,
        retrain_every=args.retrain_every,
        timeout=args.timeout,
    )


if __name__ == "__main__":
    main()
