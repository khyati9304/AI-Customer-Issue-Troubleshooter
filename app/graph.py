from langgraph.graph import StateGraph, START, END

from app.nodes import (
    analyze_issue,
    run_diagnostics,
    evaluate_evidence,
    generate_report,
)
from app.state import TroubleshooterState


def route_after_evaluation(state: TroubleshooterState) -> str:
    """Continue investigation only when another tool can be run."""
    if state["sufficient_evidence"]:
        return "report"

    if not state["pending_tools"]:
        return "report"

    if state["investigation_steps"] >= 4:
        return "report"

    return "investigate"


def build_graph():
    workflow = StateGraph(TroubleshooterState)

    workflow.add_node("analyze", analyze_issue)
    workflow.add_node("investigate", run_diagnostics)
    workflow.add_node("evaluate", evaluate_evidence)
    workflow.add_node("report", generate_report)

    workflow.add_edge(START, "analyze")
    workflow.add_edge("analyze", "investigate")
    workflow.add_edge("investigate", "evaluate")

    workflow.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {
            "investigate": "investigate",
            "report": "report",
        },
    )

    workflow.add_edge("report", END)

    return workflow.compile()


troubleshooter_graph = build_graph()


def troubleshoot(issue: str) -> dict:
    """Run the complete investigation."""
    issue = issue.strip()

    if not issue:
        raise ValueError("Please enter a description of the issue.")

    initial_state = {
        "issue_description": issue,
        "issue_type": "unknown",
        "pending_tools": [],
        "diagnostic_results": [],
        "investigation_steps": 0,
        "sufficient_evidence": False,
        "errors": [],
        "final_report": None,
    }

    return troubleshooter_graph.invoke(initial_state)