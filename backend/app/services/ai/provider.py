from typing import Protocol

from app.core.config import get_settings
from app.schemas.investigation import InvestigationResult
from app.services.ai.anthropic_provider import AnthropicInvestigator
from app.services.ai.context import InvestigationContext
from app.services.ai.fallback import development_fallback


class AIInvestigator(Protocol):
    async def investigate(self, context: InvestigationContext) -> InvestigationResult: ...


class FallbackInvestigator:
    async def investigate(self, context: InvestigationContext) -> InvestigationResult:
        return development_fallback(context, get_settings().ai_model)


def get_investigator() -> AIInvestigator:
    settings = get_settings()
    if settings.anthropic_api_key.strip():
        return AnthropicInvestigator()
    return FallbackInvestigator()
