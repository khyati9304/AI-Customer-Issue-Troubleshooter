from typing import TypedDict


class TroubleshooterState(TypedDict):
    issue_description: str
    issue_type: str
    pending_tools: list[str]
    diagnostic_results: list[dict]
    investigation_steps: int
    sufficient_evidence: bool
    errors: list[str]
    final_report: dict | None