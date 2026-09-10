import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog

logger = logging.getLogger("opspilot.services.audit")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def log_audit(
    session: AsyncSession,
    user_id: str,
    username: str,
    user_role: str,
    action: str,
    resource_type: str,
    resource_id: str,
    outcome: str = "success",
    metadata: dict | None = None,
) -> AuditLog:
    audit_id = f"aud-{uuid.uuid4().hex[:12]}"
    record = AuditLog(
        id=audit_id,
        user_id=user_id,
        username=username,
        user_role=user_role,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        outcome=outcome,
        metadata_json=metadata or {},
        created_at=utcnow(),
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    logger.info(
        "audit log recorded",
        extra={
            "audit_id": record.id,
            "username": username,
            "role": user_role,
            "action": action,
            "resource": f"{resource_type}:{resource_id}",
            "outcome": outcome,
        },
    )
    return record


async def query_audit_logs(
    session: AsyncSession,
    incident_id: str | None = None,
    user_id: str | None = None,
    action: str | None = None,
    outcome: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AuditLog]:
    stmt = select(AuditLog)
    if user_id:
        stmt = stmt.where(AuditLog.user_id == user_id)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if outcome:
        stmt = stmt.where(AuditLog.outcome == outcome)
    if incident_id:
        stmt = stmt.where(
            (AuditLog.resource_id == incident_id) |
            (AuditLog.metadata_json["incident_id"].astext == incident_id)
        )
    if start_date:
        stmt = stmt.where(AuditLog.created_at >= start_date)
    if end_date:
        stmt = stmt.where(AuditLog.created_at <= end_date)

    stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
    res = await session.execute(stmt)
    return list(res.scalars().all())
