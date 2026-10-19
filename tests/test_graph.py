import pytest

from app.graph import route_after_evaluation, troubleshoot


def make_state(**overrides):
    state = {
        "issue_description": "API returns HTTP 401",
        "issue_type": "authentication",
        "pending_tools": [],
        "diagnostic_results": [],
        "investigation_steps": 1,
        "sufficient_evidence": False,
        "errors": [],
        "final_report": None,
    }

    state.update(overrides)
    return state


def test_route_to_report_when_evidence_is_sufficient():
    state = make_state(sufficient_evidence=True)

    assert route_after_evaluation(state) == "report"


def test_route_to_report_when_no_more_tools_are_available():
    state = make_state(pending_tools=[])

    assert route_after_evaluation(state) == "report"


def test_route_to_report_when_step_limit_is_reached():
    state = make_state(
        pending_tools=["knowledge_base"],
        investigation_steps=4,
    )

    assert route_after_evaluation(state) == "report"


def test_continue_when_more_diagnostics_are_needed():
    state = make_state(
        pending_tools=["knowledge_base"],
        investigation_steps=1,
    )

    assert route_after_evaluation(state) == "investigate"


def test_empty_issue_is_rejected():
    with pytest.raises(ValueError):
        troubleshoot("   ")