from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.session import get_db
from app.dependencies.auth import AuthenticatedUser, require_role
from app.schemas.audit import AuditLogResponse
from app.services.audit_service import query_audit_logs

router = APIRouter()


@router.get("/logs", response_model=list[AuditLogResponse])
async def get_audit_logs(
    incident_id: str | None = Query(None),
    user_id: str | None = Query(None),
    action: str | None = Query(None),
    outcome: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user: AuthenticatedUser = Depends(require_role(["Lead", "SRE"])),
    session: AsyncSession = Depends(get_db),
) -> list[AuditLogResponse]:
    return await query_audit_logs(
        session=session,
        incident_id=incident_id,
        user_id=user_id,
        action=action,
        outcome=outcome,
        limit=limit,
        offset=offset,
    )
