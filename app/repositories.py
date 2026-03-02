from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


class DeploymentRecordRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, record: models.DeploymentRecord) -> models.DeploymentRecord:
        self.db.add(record)
        return record

    def get_by_id(self, record_id: str) -> models.DeploymentRecord | None:
        statement = select(models.DeploymentRecord).where(models.DeploymentRecord.id == record_id)
        return self.db.scalar(statement)


class ReleaseNoteDraftRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, record: models.ReleaseNoteDraft) -> models.ReleaseNoteDraft:
        self.db.add(record)
        return record

    def get_by_deployment_record_id(self, record_id: str) -> models.ReleaseNoteDraft | None:
        statement = select(models.ReleaseNoteDraft).where(
            models.ReleaseNoteDraft.deployment_record_id == record_id,
        )
        return self.db.scalar(statement)
