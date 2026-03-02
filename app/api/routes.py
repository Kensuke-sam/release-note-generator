from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas
from app.core.security import verify_internal_api_key
from app.db import get_db
from app.services.ai import ReleaseAiService
from app.services.domain import DeploymentService

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> DeploymentService:
    return DeploymentService(db=db, ai_service=ReleaseAiService())


@router.get("/healthz", response_model=schemas.HealthResponse)
def healthz() -> schemas.HealthResponse:
    return schemas.HealthResponse()


@router.post(
    "/deployments",
    response_model=schemas.DeploymentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_internal_api_key)],
)
def create_record(
    payload: schemas.DeploymentCreate,
    service: DeploymentService = Depends(get_service),
) -> schemas.DeploymentResponse:
    return service.create_deployment(payload)


@router.get(
    "/deployments/{record_id}",
    response_model=schemas.DeploymentResponse,
    dependencies=[Depends(verify_internal_api_key)],
)
def get_record(
    record_id: str,
    service: DeploymentService = Depends(get_service),
) -> schemas.DeploymentResponse:
    return service.get_deployment(record_id)


@router.post(
    "/deployments/{record_id}/draft-note",
    response_model=schemas.ReleaseNoteDraftResponse,
    dependencies=[Depends(verify_internal_api_key)],
)
def analyze_record(
    record_id: str,
    service: DeploymentService = Depends(get_service),
) -> schemas.ReleaseNoteDraftResponse:
    return service.draft_release_note(record_id)


@router.get(
    "/deployments/{record_id}/note",
    response_model=schemas.ReleaseNoteDraftResponse,
    dependencies=[Depends(verify_internal_api_key)],
)
def get_analysis(
    record_id: str,
    service: DeploymentService = Depends(get_service),
) -> schemas.ReleaseNoteDraftResponse:
    return service.get_note(record_id)
