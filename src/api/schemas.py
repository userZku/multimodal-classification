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
    departement_insee: str | None = None
    synthese_entretien: str


class PredictResponse(BaseModel):
    prediction: int
    confidence: float
    status: str
    model_version: str
    request_id: str


class TrainRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "dataset_path": "data/raw/dataset_trajectoire_emploi_Sujet Examen CISIA - Promo Upskilling Atlas - mai-oct2026 (Session-00279143).csv",
                "trigger": "manual",
                "mlflow_experiment": "multimodal-classification",
            }
        },
    )

    dataset_path: str | None = None
    trigger: str = "manual"
    mlflow_tracking_uri: str | None = None
    mlflow_experiment: str | None = None


class TrainResponse(BaseModel):
    status: str
    event_id: str
    model_version: str
    run_id: str | None = None
    metrics: dict


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
    run_id: str | None = None
