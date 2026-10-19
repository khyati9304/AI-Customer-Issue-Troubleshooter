from pydantic import BaseModel, Field
from typing import Literal


DiagnosticToolName = Literal[
    "api_health",
    "authentication",
    "log_analyzer",
    "knowledge_base",
]


class IssuePlan(BaseModel):
    issue_type: str = Field(
        description="Short technical issue category"
    )
    selected_tools: list[DiagnosticToolName] = Field(
        min_length=1,
        max_length=4,
        description="Diagnostic tools relevant to the issue"
    )
    rationale: str = Field(
        description="Why these diagnostic tools are appropriate"
    )


class InvestigationDecision(BaseModel):
    sufficient_evidence: bool = Field(
        description="Whether evidence is sufficient for a useful diagnosis"
    )
    additional_tools: list[DiagnosticToolName] = Field(
        default_factory=list,
        description="New diagnostic tools that could clarify the issue"
    )
    reasoning: str = Field(
        description="Brief explanation based on observed evidence"
    )


class DiagnosticReport(BaseModel):
    issue_summary: str
    severity: Literal["low", "medium", "high", "critical"]
    probable_root_cause: str
    supporting_evidence: list[str]
    confidence: float = Field(ge=0, le=1)
    recommended_actions: list[str]
    needs_escalation: bool
    limitations: list[str]