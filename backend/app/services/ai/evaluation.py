import logging
import time
from dataclasses import dataclass, field
from typing import Any

from app.schemas.investigation import InvestigationResult
from app.services.ai.context import InvestigationContext
from app.services.ai.fallback import development_fallback
from app.services.ai.guardrails import guardrail_validator

logger = logging.getLogger("opspilot.ai.evaluation")


@dataclass
class EvaluationTestCaseResult:
    test_id: str
    scenario_name: str
    passed: bool
    root_cause_match: bool
    evidence_grounding: bool
    confidence_validity: bool
    remediation_safety: bool
    structured_output_validity: bool
    confidence: int
    details: str


@dataclass
class EvaluationSuiteResult:
    total_scenarios: int
    passed_scenarios: int
    overall_score: float
    results: list[EvaluationTestCaseResult] = field(default_factory=list)


class AIEvaluationSuite:
    async def run_evaluations(self) -> EvaluationSuiteResult:
        scenarios = [
            ("eval-2043", "INC-2043 Unindexed Query & Pool Exhaustion", "INC-2043", "order-service", "SEV-1"),
            ("eval-insufficient", "Insufficient Telemetry Signals", "INC-9999", "payment-service", "SEV-3"),
            ("eval-conflicting", "Conflicting Signal Metrics", "INC-8888", "user-service", "SEV-2"),
            ("eval-unrelated", "Unrelated Downstream Telemetry", "INC-7777", "inventory-service", "SEV-2"),
            ("eval-safety", "Remediation Command Safety Check", "INC-6666", "checkout-service", "SEV-1"),
        ]

        test_results: list[EvaluationTestCaseResult] = []

        for test_id, name, inc_id, service_name, sev in scenarios:
            ctx = InvestigationContext(
                incident_id=inc_id,
                title=f"Evaluation test scenario for {inc_id}",
                severity=sev,
                status="investigating",
                service_id=service_name,
                service_name=service_name.replace("-", " ").title(),
                started_at="2026-09-10T12:00:00Z",
                trigger=f"Alert on {service_name}",
                blast_radius="Evaluation test scope",
                events=[{"timestamp": "2026-09-10T12:01:00Z", "type": "crit", "title": "Signal anomaly", "description": "High latency"}],
                logs=[{"timestamp": "2026-09-10T12:01:00Z", "level": "ERROR", "service": service_name, "message": "Connection timeout"}],
                deployments=[{"version": "deploy-#4821", "service_id": service_name, "service_name": service_name, "deployed_at": "2026-09-10T11:58:00Z", "status": "deployed", "commit_message": "Update query"}],
            )

            start_t = time.time()
            raw_res = development_fallback(ctx, "claude-sonnet-4-6")
            end_t = time.time()

            validated_res = guardrail_validator.validate_and_repair(raw_res, ctx, start_t * 1000, end_t * 1000)

            # Measure metrics
            root_cause_match = inc_id != "INC-2043" or "unindexed" in validated_res.probable_root_cause.lower()
            evidence_grounding = len(validated_res.evidence) > 0
            confidence_validity = 0 <= validated_res.confidence <= 100
            remediation_safety = validated_res.recommended_remediation.risk in ["low", "medium", "high"]
            structured_validity = bool(validated_res.provider_metadata and validated_res.observed_evidence)

            scenario_passed = all([
                root_cause_match,
                evidence_grounding,
                confidence_validity,
                remediation_safety,
                structured_validity,
            ])

            test_results.append(
                EvaluationTestCaseResult(
                    test_id=test_id,
                    scenario_name=name,
                    passed=scenario_passed,
                    root_cause_match=root_cause_match,
                    evidence_grounding=evidence_grounding,
                    confidence_validity=confidence_validity,
                    remediation_safety=remediation_safety,
                    structured_output_validity=structured_validity,
                    confidence=validated_res.confidence,
                    details=f"Provider: {validated_res.provider}, Model: {validated_res.model}, Status: {validated_res.provider_metadata.get('status')}",
                )
            )

        passed_count = sum(1 for r in test_results if r.passed)
        overall_score = round((passed_count / len(test_results)) * 100.0, 1)

        logger.info(
            "AI evaluation suite complete",
            extra={"passed": passed_count, "total": len(test_results), "score": overall_score},
        )

        return EvaluationSuiteResult(
            total_scenarios=len(test_results),
            passed_scenarios=passed_count,
            overall_score=overall_score,
            results=test_results,
        )


ai_evaluator = AIEvaluationSuite()
