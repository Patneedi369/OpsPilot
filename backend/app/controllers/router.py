from fastapi import APIRouter

# pyrefly: ignore [missing-import]
from app.controllers.audit import router as audit_router
from app.controllers.auth import router as auth_router
from app.controllers.events import router as events_router
from app.controllers.evidence import router as evidence_router
from app.controllers.health import router as health_router
from app.controllers.incidents import router as incidents_router
from app.controllers.investigations import router as investigations_router
from app.controllers.telemetry import router as telemetry_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(telemetry_router, prefix="/telemetry", tags=["telemetry"])
api_router.include_router(audit_router, prefix="/audit", tags=["audit"])
api_router.include_router(events_router, prefix="/incidents", tags=["events"])
api_router.include_router(evidence_router, prefix="/incidents", tags=["evidence"])
api_router.include_router(investigations_router, prefix="/incidents", tags=["investigations"])
api_router.include_router(incidents_router, prefix="/incidents", tags=["incidents"])
