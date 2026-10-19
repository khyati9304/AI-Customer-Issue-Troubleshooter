import json
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.models import (
    DiagnosticReport,
    IssuePlan,
    InvestigationDecision,
)
from app.prompts import (
    ISSUE_ANALYSIS_PROMPT,
    EVIDENCE_EVALUATION_PROMPT,
    REPORT_GENERATION_PROMPT,
)
from app.state import TroubleshooterState
from app.tools import run_diagnostic


load_dotenv()

MAX_INVESTIGATION_STEPS = 4


def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Configure it in your .env file."
        )

    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        api_key=api_key,
    )


def analyze_issue(state: TroubleshooterState) -> dict:
    """Classify the issue and choose initial diagnostic tools."""
    try:
        planner = get_llm().with_structured_output(IssuePlan)

        plan = planner.invoke([
            ("system", ISSUE_ANALYSIS_PROMPT),
            ("human", state["issue_description"]),
        ])

        return {
            "issue_type": plan.issue_type,
            "pending_tools": list(dict.fromkeys(plan.selected_tools)),
            "errors": state.get("errors", []),
        }

    except Exception as exc:
        return {
            "issue_type": "unclassified",
            "pending_tools": ["log_analyzer", "knowledge_base"],
            "errors": state.get("errors", []) + [
                f"Issue analysis failed: {type(exc).__name__}"
            ],
        }


def run_diagnostics(state: TroubleshooterState) -> dict:
    """Execute registered tools, respecting the investigation limit."""
    already_used = {
        item["tool"]
        for item in state["diagnostic_results"]
        if "tool" in item
    }

    remaining = (
        MAX_INVESTIGATION_STEPS - state["investigation_steps"]
    )

    candidates = [
        name for name in state["pending_tools"]
        if name not in already_used
    ]

    selected = candidates[:max(0, remaining)]
    new_results = []
    new_errors = []

    for tool_name in selected:
        try:
            result = run_diagnostic(
                tool_name,
                state["issue_description"],
            )
            new_results.append(result)

        except Exception as exc:
            new_results.append({
                "tool": tool_name,
                "error": "Diagnostic tool failed",
            })
            new_errors.append(
                f"{tool_name} failed: {type(exc).__name__}"
            )

    return {
        "diagnostic_results": (
            state["diagnostic_results"] + new_results
        ),
        "investigation_steps": (
            state["investigation_steps"] + len(selected)
        ),
        "pending_tools": [],
        "errors": state.get("errors", []) + new_errors,
    }


def evaluate_evidence(state: TroubleshooterState) -> dict:
    """Decide whether further investigation would help."""
    used_tools = [
        result["tool"]
        for result in state["diagnostic_results"]
        if "tool" in result
    ]

    remaining = (
        MAX_INVESTIGATION_STEPS - state["investigation_steps"]
    )

    if remaining <= 0:
        return {
            "sufficient_evidence": False,
            "pending_tools": [],
        }

    try:
        evaluator = get_llm().with_structured_output(
            InvestigationDecision
        )

        decision = evaluator.invoke([
            (
                "system",
                EVIDENCE_EVALUATION_PROMPT.format(
                    issue=state["issue_description"],
                    evidence=json.dumps(
                        state["diagnostic_results"],
                        ensure_ascii=False,
                    ),
                    used_tools=", ".join(used_tools),
                ),
            ),
            (
                "human",
                "Evaluate the current evidence and decide whether "
                "another diagnostic check is needed.",
            ),
        ])

        additional = [
            name
            for name in decision.additional_tools
            if name not in used_tools
        ][:remaining]

        return {
            "sufficient_evidence": decision.sufficient_evidence,
            "pending_tools": (
                [] if decision.sufficient_evidence else additional
            ),
        }

    except Exception as exc:
        return {
            "sufficient_evidence": False,
            "pending_tools": [],
            "errors": state.get("errors", []) + [
                f"Evidence evaluation failed: {type(exc).__name__}"
            ],
        }


def generate_report(state: TroubleshooterState) -> dict:
    """Generate a structured diagnosis grounded in tool results."""
    evidence = state["diagnostic_results"]
    errors = state.get("errors", [])

    if not evidence:
        return {
            "final_report": {
                "issue_summary": state["issue_description"],
                "severity": "medium",
                "probable_root_cause": (
                    "Unable to determine the root cause because "
                    "no diagnostic evidence was collected."
                ),
                "supporting_evidence": [],
                "confidence": 0.0,
                "recommended_actions": [
                    "Check the issue description and diagnostic setup.",
                    "Retry the investigation after resolving configuration errors.",
                ],
                "needs_escalation": True,
                "limitations": errors + [
                    "No diagnostic evidence is available."
                ],
            }
        }

    try:
        reporter = get_llm().with_structured_output(
            DiagnosticReport
        )

        report = reporter.invoke([
            (
                "system",
                REPORT_GENERATION_PROMPT.format(
                    issue=state["issue_description"],
                    evidence=json.dumps(
                        evidence,
                        ensure_ascii=False,
                    ),
                    errors=json.dumps(errors),
                ),
            ),
            (
                "human",
                "Generate the final troubleshooting report.",
            ),
        ])

        return {"final_report": report.model_dump()}

    except Exception as exc:
        return {
            "final_report": {
                "issue_summary": state["issue_description"],
                "severity": "medium",
                "probable_root_cause": (
                    "A reliable root-cause report could not be generated."
                ),
                "supporting_evidence": [
                    json.dumps(item, ensure_ascii=False)
                    for item in evidence
                ],
                "confidence": 0.0,
                "recommended_actions": [
                    "Review the collected diagnostic evidence.",
                    "Retry report generation after checking the LLM configuration.",
                ],
                "needs_escalation": True,
                "limitations": errors + [
                    f"Report generation failed: {type(exc).__name__}"
                ],
            }
        }