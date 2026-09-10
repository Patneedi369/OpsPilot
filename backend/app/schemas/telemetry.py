from datetime import datetime
from pydantic import BaseModel, Field


class TelemetrySignalIngest(BaseModel):
    metric: str
    value: float
    threshold: float
    service_id: str
    source: str = "monitoring"
    metadata: dict | None = None


class TelemetrySignalResponse(BaseModel):
    id: str
    metric: str
    value: float
    threshold: float
    service_id: str
    source: str
    status: str
    incident_id: str | None = None
    metadata_json: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class DetectionEventResponse(BaseModel):
    id: str
    incident_id: str
    rule_name: str
    summary: str
    correlated_signals_count: int
    metadata_json: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class RunDetectionRequest(BaseModel):
    service_id: str | None = None
    auto_investigate: bool = True
