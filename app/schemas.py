from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class DeploymentCreate(BaseModel):
    service_name: str = Field(min_length=3, max_length=80, description="Service name")
    environment: str = Field(min_length=2, max_length=32, description="Deployment environment")
    change_summary: str = Field(min_length=20, max_length=4000, description="Change summary")
    issue_refs: list[str] = Field(min_length=1, description="Issue references")


class DeploymentResponse(DeploymentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime


class ReleaseNoteDraftPayload(BaseModel):
    headline: str = Field(min_length=5, max_length=120, description="Release headline")
    audience_summary: str = Field(
        min_length=10, max_length=400, description="Audience facing summary"
    )
    rollback_plan: str = Field(min_length=10, max_length=400, description="Rollback plan")
    risk_level: str = Field(min_length=2, max_length=16, description="Risk level")


class ReleaseNoteDraftResponse(ReleaseNoteDraftPayload):
    model_config = ConfigDict(from_attributes=True)

    id: str
    deployment_record_id: str
    created_at: datetime
