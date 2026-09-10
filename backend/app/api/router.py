from fastapi import APIRouter

from app.api.routes.audit import router as audit_router
from app.api.routes.auth import router as auth_router
from app.api.routes.events import router as events_router
from app.api.routes.evidence import router as evidence_router
from app.api.routes.health import router as health_router
from app.api.routes.incidents import router as incidents_router
from app.api.routes.investigations import router as investigations_router
from app.api.routes.telemetry import router as telemetry_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(telemetry_router, prefix="/telemetry", tags=["telemetry"])
api_router.include_router(audit_router, prefix="/audit", tags=["audit"])
api_router.include_router(events_router, prefix="/incidents", tags=["events"])
api_router.include_router(evidence_router, prefix="/incidents", tags=["evidence"])
api_router.include_router(investigations_router, prefix="/incidents", tags=["investigations"])
api_router.include_router(incidents_router, prefix="/incidents", tags=["incidents"])
