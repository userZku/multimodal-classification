from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PredictRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "usager_id": "U_TEST_001",
                "age": 36,
                "niveau_diplome": "bac+2",
                "anciennete_poste_ans": 4.0,
                "code_rome_vise": "M1805",
                "est_allocataire": 1,
                "nationalite_hors_ue": 0,
                "departement_insee": "75",
                "synthese_entretien": "Motivation stable, projet coherent, recherche active.",
            }
        },
    )

    usager_id: str | None = None
    age: float | None = Field(default=None, ge=16, le=100)
    niveau_diplome: str | None = None
    anciennete_poste_ans: float | None = Field(default=None, ge=0)
    code_rome_vise: str | None = None
    code_insee_commune: str | None = None
    est_allocataire: int | None = Field(default=None, ge=0, le=1)
    nationalite_hors_ue: int | None = Field(default=None, ge=0, le=1)
    departement_insee: str | None = None
    synthese_entretien: str


class PredictResponse(BaseModel):
    prediction: int
    confidence: float
    status: str
    model_version: str
    request_id: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
