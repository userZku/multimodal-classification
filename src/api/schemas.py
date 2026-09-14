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
    reason: str | None = None


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
    run_id: str | None = None


class RollbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: str | None = Field(
        default=None,
        description="Timestamp de la snapshot à restaurer (défaut: la plus récente)",
    )


class RollbackResponse(BaseModel):
    status: str
    restored_timestamp: str
    metrics: dict


class ModelHistoryEntry(BaseModel):
    timestamp: str
    trained_at: str | None = None
    archived_at: str | None = None
    archive_reason: str | None = None
    metrics: dict


class ModelHistoryResponse(BaseModel):
    count: int
    items: list[ModelHistoryEntry]


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "request_id": "req_20260914_120000_abc123",
                "true_label": 1,
                "comments": "L'usager a été embauché après 30 jours.",
            }
        },
    )

    request_id: str
    true_label: int = Field(..., ge=0, le=2)
    comments: str | None = None


class FeedbackResponse(BaseModel):
    status: str
    message: str
    feedback_id: str | None = None


class FeedbackCountResponse(BaseModel):
    total: int
    new: int
