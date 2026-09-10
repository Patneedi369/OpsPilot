from datetime import datetime
from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    id: str
    user_id: str
    username: str
    user_role: str
    action: str
    resource_type: str
    resource_id: str
    outcome: str
    metadata_json: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogQuery(BaseModel):
    incident_id: str | None = None
    user_id: str | None = None
    action: str | None = None
    outcome: str | None = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
