import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import event_bus, utcnow_iso
from app.persistence.session import get_db
from app.repositories.incident_repository import incident_repository
from app.repositories.investigation_repository import investigation_repository

router = APIRouter()
logger = logging.getLogger("opspilot.api.events")


@router.get("/{incident_id}/events/stream")
async def stream_incident_events(
    incident_id: str,
    session: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    incident = await incident_repository.get_by_id(session, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found.",
        )

    latest_run = await investigation_repository.get_latest_run_for_incident(session, incident_id)

    async def event_generator() -> AsyncGenerator[str, None]:
        # 1. Yield initial sync state event to immediately populate client state
        initial_payload = {
            "id": f"evt-sync-{incident_id}",
            "type": "sync_state",
            "timestamp": utcnow_iso(),
            "incident_id": incident_id,
            "run_id": latest_run.id if latest_run else None,
            "status": incident.status,
            "payload": {
                "incident_status": incident.status,
                "workflow_stage": incident.workflow_stage,
                "run_status": latest_run.status if latest_run else None,
                "current_step": latest_run.current_step if latest_run else None,
                "execution_result": latest_run.execution_result if latest_run else None,
                "verification_result": latest_run.verification_result if latest_run else None,
            },
        }
        yield f"id: evt-sync-{incident_id}\nevent: sync_state\ndata: {json.dumps(initial_payload, default=str)}\n\n"

        # 2. Subscribe and stream live events
        async for sse_event in event_bus.subscribe(incident_id):
            yield sse_event

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
