import json
import logging
import re
from datetime import datetime, timezone

import httpx

from app.core.config import get_settings
from app.schemas.investigation import InvestigationResult, RemediationOption
from app.services.ai.context import InvestigationContext
from app.services.ai.fallback import development_fallback

logger = logging.getLogger("opspilot.ai")

SYSTEM_PROMPT = """You are the root-cause analysis agent inside OpsPilot, an SRE incident-intelligence platform.
Analyze the structured evidence and respond with ONLY a single valid JSON object (no markdown fences) with this shape:
{
  "summary": "one paragraph",
  "probable_root_cause": "one precise sentence",
  "reasoning": "2-4 sentences for an on-call engineer",
  "confidence": 0-100 integer,
  "expected_impact_if_unresolved": "short phrase",
  "affected_users_estimate": "short phrase",
  "evidence": [{"id": "evd-1", "source": "metrics|logs|deployment|database|topology", "summary": "short bullet"}],
  "remediations": [
    {"id": "rem-1", "title": "action", "description": "1-2 sentences", "risk": "low|medium|high", "etaMinutes": 5, "recommended": true, "kind": "rollback|infrastructure|forward_fix"}
  ]
}
Give exactly 2 remediations and mark exactly one recommended=true. Ground every field in the evidence. Do not invent facts.
"""


class AnthropicInvestigator:
    async def investigate(self, context: InvestigationContext) -> InvestigationResult:
        settings = get_settings()
        try:
            payload = await self._complete(settings.anthropic_api_key, settings.ai_model, context)
            return self._to_result(context, payload, settings.ai_model)
        except Exception:
            logger.exception("anthropic investigation failed; using development fallback")
            return development_fallback(context, settings.ai_model)

    async def _complete(self, api_key: str, model: str, context: InvestigationContext) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 1200,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": context.to_prompt_block()}],
                },
            )
            response.raise_for_status()
        body = response.json()
        chunks = body.get("content") or []
        text = "".join(str(chunk.get("text") or "") for chunk in chunks).strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            raise ValueError("AI response was not a JSON object")
        return parsed

    def _to_result(self, context: InvestigationContext, payload: dict, model: str) -> InvestigationResult:
        remediations = [RemediationOption.model_validate(item) for item in payload.get("remediations") or []]
        recommended = next((item for item in remediations if item.recommended), remediations[0] if remediations else None)
        if recommended is None:
            raise ValueError("AI response omitted remediations")
        confidence = int(payload.get("confidence") or 0)
        cause = str(payload.get("probable_root_cause") or "")
        return InvestigationResult.model_validate(
            {
                "id": f"inv-{context.incident_id}",
                "incidentId": context.incident_id,
                "status": "complete",
                "summary": payload.get("summary") or cause,
                "probableRootCause": cause,
                "evidence": payload.get("evidence") or [],
                "affectedService": context.service_name,
                "severity": context.severity,
                "confidence": confidence,
                "recommendedRemediation": recommended.model_dump(by_alias=True),
                "investigatedAt": datetime.now(timezone.utc).isoformat(),
                "reasoning": payload.get("reasoning") or "",
                "rootCause": {
                    "summary": cause,
                    "confidence": confidence,
                    "expectedImpactIfUnresolved": payload.get("expected_impact_if_unresolved") or "",
                    "affectedUsersEstimate": payload.get("affected_users_estimate") or "",
                    "model": model,
                },
                "remediations": [item.model_dump(by_alias=True) for item in remediations],
                "model": model,
                "provider": "anthropic",
            }
        )
