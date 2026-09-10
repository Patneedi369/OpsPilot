from app.services.ai.graph.workflow import get_graph_state, run_or_resume_graph

run_investigation_graph = run_or_resume_graph

__all__ = ["run_or_resume_graph", "run_investigation_graph", "get_graph_state"]
