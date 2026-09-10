import asyncio
import json
import logging
import uuid
from collections import defaultdict
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("opspilot.core.events")


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, set[asyncio.Queue[str]]] = defaultdict(set)
        self._seen_event_ids: set[str] = set()

    async def subscribe(self, incident_id: str) -> AsyncGenerator[str, None]:
        queue: asyncio.Queue[str] = asyncio.Queue()
        self._subscribers[incident_id].add(queue)
        logger.info("SSE client subscribed", extra={"incident_id": incident_id, "active_subscribers": len(self._subscribers[incident_id])})

        try:
            while True:
                # Wait for next event string
                event_data = await queue.get()
                yield event_data
        except asyncio.CancelledError:
            logger.info("SSE client disconnected", extra={"incident_id": incident_id})
        finally:
            self._subscribers[incident_id].discard(queue)
            if not self._subscribers[incident_id]:
                del self._subscribers[incident_id]

    def publish(
        self,
        incident_id: str,
        event_type: str,
        payload: dict[str, Any] | None = None,
        run_id: str | None = None,
        status: str | None = None,
        event_id: str | None = None,
    ) -> str:
        evt_id = event_id or f"evt-{uuid.uuid4().hex[:12]}"
        
        # Deduplication check
        if evt_id in self._seen_event_ids:
            return evt_id
            
        self._seen_event_ids.add(evt_id)
        if len(self._seen_event_ids) > 10000:
            self._seen_event_ids.clear()

        event_payload = {
            "id": evt_id,
            "type": event_type,
            "timestamp": utcnow_iso(),
            "incident_id": incident_id,
            "run_id": run_id,
            "status": status,
            "payload": payload or {},
        }

        sse_formatted = f"id: {evt_id}\nevent: {event_type}\ndata: {json.dumps(event_payload, default=str)}\n\n"

        queues = self._subscribers.get(incident_id, set())
        for q in list(queues):
            try:
                q.put_nowait(sse_formatted)
            except asyncio.QueueFull:
                pass

        logger.info(
            "incident event published",
            extra={"incident_id": incident_id, "event_type": event_type, "subscribers": len(queues)},
        )
        return evt_id


event_bus = EventBus()
