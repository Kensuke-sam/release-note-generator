from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.errors import NotFoundError, PersistenceError
from app.repositories import DeploymentRecordRepository, ReleaseNoteDraftRepository
from app.services.ai import ReleaseAiService


class DeploymentService:
    def __init__(self, db: Session, ai_service: ReleaseAiService) -> None:
        self.db = db
        self.ai_service = ai_service
        self.entities = DeploymentRecordRepository(db)
        self.analyses = ReleaseNoteDraftRepository(db)

    def create_deployment(self, payload: schemas.DeploymentCreate) -> schemas.DeploymentResponse:
        record = models.DeploymentRecord(
            service_name=payload.service_name,
            environment=payload.environment,
            change_summary=payload.change_summary,
            issue_refs=payload.issue_refs,
        )
        try:
            self.entities.create(record)
            self.db.commit()
            self.db.refresh(record)
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise PersistenceError("Failed to save デプロイ記録.") from exc
        return schemas.DeploymentResponse.model_validate(record)

    def get_deployment(self, record_id: str) -> schemas.DeploymentResponse:
        record = self.entities.get_by_id(record_id)
        if record is None:
            raise NotFoundError("デプロイ記録 not found.")
        return schemas.DeploymentResponse.model_validate(record)

    def draft_release_note(self, record_id: str) -> schemas.ReleaseNoteDraftResponse:
        record = self.entities.get_by_id(record_id)
        if record is None:
            raise NotFoundError("デプロイ記録 not found.")

        draft = self.ai_service.generate(record)
        existing = self.analyses.get_by_deployment_record_id(record_id)
        if existing is None:
            existing = models.ReleaseNoteDraft(
                deployment_record_id=record_id,
                **draft.model_dump(),
            )
            self.analyses.save(existing)
        else:
            existing.headline = draft.headline
            existing.audience_summary = draft.audience_summary
            existing.rollback_plan = draft.rollback_plan
            existing.risk_level = draft.risk_level

        try:
            self.db.commit()
            self.db.refresh(existing)
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise PersistenceError("Failed to save リリースノート草案.") from exc

        return schemas.ReleaseNoteDraftResponse.model_validate(existing)

    def get_note(self, record_id: str) -> schemas.ReleaseNoteDraftResponse:
        record = self.entities.get_by_id(record_id)
        if record is None:
            raise NotFoundError("デプロイ記録 not found.")

        analysis = self.analyses.get_by_deployment_record_id(record_id)
        if analysis is None:
            raise NotFoundError("リリースノート草案 not found.")
        return schemas.ReleaseNoteDraftResponse.model_validate(analysis)
