from __future__ import annotations

import pandas as pd

from src.features.preprocessing import (
    build_model_frame,
    build_preprocessor,
    infer_departement_from_insee,
    resolve_feature_spec,
)


def test_build_model_frame_drops_technical_columns() -> None:
    df = pd.DataFrame(
        [
            {
                "usager_id": "U_TEST_001",
                "code_insee_commune": "75056",
                "nationalite_hors_ue": 1,
                "age": 36,
                "synthese_entretien": "Projet cohérent",
            }
        ]
    )

    out = build_model_frame(df)

    assert "usager_id" not in out.columns
    assert "code_insee_commune" not in out.columns
    assert "nationalite_hors_ue" not in out.columns
    assert "departement_insee" in out.columns
    assert out.loc[0, "departement_insee"] == "75"


def test_infer_departement_from_insee_handles_format_noise() -> None:
    values = pd.Series([" 75056", "2A004", "97123", None])

    out = infer_departement_from_insee(values)

    assert out.tolist() == ["75", "2A", "97", "00"]


def test_niveau_diplome_uses_explicit_ordinal_encoding() -> None:
    frame = pd.DataFrame(
        {
            "niveau_diplome": ["Sans diplôme", "Bac", "Bac+2", "Bac+5"],
            "age": [20, 25, 30, 35],
            "anciennete_poste_ans": [0, 1, 2, 3],
            "code_rome_vise": ["M1602"] * 4,
            "est_allocataire": [0, 1, 0, 1],
            "departement_insee": ["75"] * 4,
            "synthese_entretien": ["Projet professionnel"] * 4,
        }
    )

    preprocessor = build_preprocessor(resolve_feature_spec(frame.columns))
    transformed = preprocessor.fit_transform(frame)

    assert preprocessor.transformers_[1][0] == "ord"
    assert transformed[:, 2].tolist() == [0.0, 1.0, 2.0, 3.0]
