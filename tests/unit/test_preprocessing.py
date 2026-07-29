from __future__ import annotations

import pandas as pd

from src.features.preprocessing import build_model_frame, infer_departement_from_insee


def test_build_model_frame_drops_technical_columns() -> None:
    df = pd.DataFrame(
        [
            {
                "usager_id": "U_TEST_001",
                "code_insee_commune": "75056",
                "age": 36,
                "synthese_entretien": "Projet cohérent",
            }
        ]
    )

    out = build_model_frame(df)

    assert "usager_id" not in out.columns
    assert "code_insee_commune" not in out.columns
    assert "departement_insee" in out.columns
    assert out.loc[0, "departement_insee"] == "75"


def test_infer_departement_from_insee_handles_format_noise() -> None:
    values = pd.Series([" 75056", "2A004", "97123", None])

    out = infer_departement_from_insee(values)

    assert out.tolist() == ["75", "2A", "97", "00"]
