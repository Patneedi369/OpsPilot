import logging
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from app.schemas.investigation import InvestigationResult
from app.services.ai.graph.checkpointer import get_checkpointer
from app.services.ai.graph.nodes import (
    context_collector_node,
    human_approval_node,
    recovery_verifier_node,
    remediation_executor_node,
    remediation_recommender_node,
    remediation_rejected_node,
    root_cause_analyst_node,
    signal_correlator_node,
)
from app.services.ai.graph.state import InvestigationGraphState

logger = logging.getLogger("opspilot.graph.workflow")


def route_approval(state: InvestigationGraphState) -> str:
    decision = state.get("approval_decision")
    if decision == "approved":
        return "remediation_executor"
    return "remediation_rejected"


def route_execution(state: InvestigationGraphState) -> str:
    status = state.get("status")
    if status == "remediation_failed":
        return END
    return "recovery_verifier"


async def get_compiled_graph():
    checkpointer = await get_checkpointer()
    builder = StateGraph(InvestigationGraphState)

    builder.add_node("context_collector", context_collector_node)
    builder.add_node("signal_correlator", signal_correlator_node)
    builder.add_node("root_cause_analyst", root_cause_analyst_node)
    builder.add_node("remediation_recommender", remediation_recommender_node)
    builder.add_node("human_approval", human_approval_node)
    builder.add_node("remediation_executor", remediation_executor_node)
    builder.add_node("recovery_verifier", recovery_verifier_node)
    builder.add_node("remediation_rejected", remediation_rejected_node)

    builder.add_edge(START, "context_collector")
    builder.add_edge("context_collector", "signal_correlator")
    builder.add_edge("signal_correlator", "root_cause_analyst")
    builder.add_edge("root_cause_analyst", "remediation_recommender")
    builder.add_edge("remediation_recommender", "human_approval")

    builder.add_conditional_edges(
        "human_approval",
        route_approval,
        {
            "remediation_executor": "remediation_executor",
            "remediation_rejected": "remediation_rejected",
        },
    )

    builder.add_conditional_edges(
        "remediation_executor",
        route_execution,
        {
            "recovery_verifier": "recovery_verifier",
            END: END,
        },
    )

    builder.add_edge("recovery_verifier", END)
    builder.add_edge("remediation_rejected", END)

    return builder.compile(checkpointer=checkpointer)


async def run_or_resume_graph(
    thread_id: str,
    initial_state: InvestigationGraphState | None = None,
    resume_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    graph = await get_compiled_graph()
    config = {"configurable": {"thread_id": thread_id}}

    logger.info(
        "executing LangGraph workflow",
        extra={"thread_id": thread_id, "is_resume": bool(resume_payload)},
    )

    if resume_payload is not None:
        input_data = Command(resume=resume_payload)
    else:
        input_data = initial_state or {}

    final_state = await graph.ainvoke(input_data, config=config)
    return final_state


async def get_graph_state(thread_id: str) -> Any:
    graph = await get_compiled_graph()
    config = {"configurable": {"thread_id": thread_id}}
    return await graph.aget_state(config)
