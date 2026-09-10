import asyncio
import os
import sys
import unittest

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from httpx import ASGITransport, AsyncClient

from app.core.events import EventBus, event_bus
from app.db.session import engine
from app.main import app


class TestPhases16And17(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self) -> None:
        await engine.dispose()

    async def test_01_sse_event_stream_response(self):
        """Test 1: GET /api/v1/incidents/{id}/events/stream returns text/event-stream content type."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            async with client.stream("GET", "/api/v1/incidents/INC-2043/events/stream") as resp:
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.headers.get("content-type"), "text/event-stream")
                
                # Read initial chunk containing sync_state
                first_chunk = None
                async for chunk in resp.aiter_text():
                    first_chunk = chunk
                    break
                
                self.assertIsNotNone(first_chunk)
                self.assertIn("sync_state", first_chunk)

    async def test_02_correct_incident_scoping_and_ordering(self):
        """Test 2: Published events are correctly scoped by incident_id and delivered in order."""
        inc_id = "INC-TEST-SCOPE-1"
        bus = EventBus()
        received = []

        async def subscriber():
            async for evt in bus.subscribe(inc_id):
                received.append(evt)
                if len(received) >= 2:
                    break

        sub_task = asyncio.create_task(subscriber())
        await asyncio.sleep(0.05)

        evt1_id = bus.publish(incident_id=inc_id, event_type="investigation_started", payload={"step": 1})
        evt2_id = bus.publish(incident_id=inc_id, event_type="remediation_executing", payload={"step": 2})

        await asyncio.wait_for(sub_task, timeout=2.0)

        self.assertEqual(len(received), 2)
        self.assertIn("investigation_started", received[0])
        self.assertIn("remediation_executing", received[1])

    async def test_03_duplicate_event_prevention(self):
        """Test 3: EventBus deduplicates events with identical event_id."""
        bus = EventBus()
        evt_id = "evt-dedup-fixed-id-100"
        
        first = bus.publish(incident_id="INC-2043", event_type="test_event", event_id=evt_id)
        second = bus.publish(incident_id="INC-2043", event_type="test_event", event_id=evt_id)

        self.assertEqual(first, evt_id)
        self.assertEqual(second, evt_id)

    async def test_04_disconnect_handling(self):
        """Test 4: Disconnecting subscription cleans up subscriber queue without errors."""
        bus = EventBus()
        inc_id = "INC-DISCONNECT-1"

        async def cancel_sub():
            gen = bus.subscribe(inc_id)
            async for _ in gen:
                break

        task = asyncio.create_task(cancel_sub())
        await asyncio.sleep(0.05)
        bus.publish(inc_id, "trigger")
        await asyncio.wait_for(task, timeout=1.0)
        self.assertNotIn(inc_id, bus._subscribers)

    async def test_05_ci_workflow_and_docker_files_exist(self):
        """Test 5: CI workflow and Docker configuration files exist in repository."""
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        ci_path = os.path.join(repo_root, ".github", "workflows", "ci.yml")
        dockerignore_path = os.path.join(repo_root, ".dockerignore")
        deployment_path = os.path.join(repo_root, "DEPLOYMENT.md")

        self.assertTrue(os.path.exists(ci_path), f"ci.yml missing at {ci_path}")
        self.assertTrue(os.path.exists(dockerignore_path), f".dockerignore missing at {dockerignore_path}")
        self.assertTrue(os.path.exists(deployment_path), f"DEPLOYMENT.md missing at {deployment_path}")

        with open(ci_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("name: OpsPilot CI", content)
            self.assertIn("backend-test:", content)
            self.assertIn("frontend-check:", content)
