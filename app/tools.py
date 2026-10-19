import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(filename: str):
    path = DATA_DIR / filename

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def api_health(issue: str) -> dict:
    """Return simulated API health and latency information."""
    services = load_json("service_status.json")

    issue_lower = issue.lower()

    if "payment" in issue_lower:
        service_name = "payment_service"
    else:
        service_name = "api"

    return {
        "tool": "api_health",
        "service": service_name,
        "data": services[service_name],
        "source": "simulated_service_status"
    }


def authentication(issue: str) -> dict:
    """Inspect simulated authentication metadata without exposing secrets."""
    issue_lower = issue.lower()

    if any(word in issue_lower for word in ["401", "api key", "credential"]):
        return {
            "tool": "authentication",
            "status": "configuration_mismatch",
            "configured_key_id": "key_old",
            "active_key_id": "key_new",
            "secret_exposed": False,
            "source": "simulated_authentication_metadata"
        }

    if "expired token" in issue_lower or "token expired" in issue_lower:
        return {
            "tool": "authentication",
            "status": "token_expiry_suspected",
            "secret_exposed": False,
            "source": "simulated_authentication_metadata"
        }

    return {
        "tool": "authentication",
        "status": "inconclusive",
        "secret_exposed": False,
        "source": "simulated_authentication_metadata"
    }


def log_analyzer(issue: str) -> dict:
    """Find sample log entries relevant to the reported issue."""
    logs = load_json("sample_logs.json")
    issue_lower = issue.lower()

    terms = []

    if "401" in issue_lower or "api key" in issue_lower:
        terms = ["401", "unauthorized", "credential"]

    elif "403" in issue_lower:
        terms = ["403", "forbidden", "permission"]

    elif "429" in issue_lower or "rate limit" in issue_lower:
        terms = ["429", "rate limit", "too many requests"]

    elif "500" in issue_lower:
        terms = ["500", "internal server error"]

    elif any(word in issue_lower for word in ["slow", "latency", "timeout"]):
        terms = ["latency", "timeout"]

    else:
        terms = [
            word for word in issue_lower.split()
            if len(word) > 3
        ]

    matches = [
        log for log in logs
        if any(term in log["message"].lower() for term in terms)
    ]

    return {
        "tool": "log_analyzer",
        "matching_entries": matches,
        "match_count": len(matches),
        "source": "simulated_logs"
    }


def knowledge_base(issue: str) -> dict:
    """Search local troubleshooting articles using keyword matching."""
    articles = load_json("knowledge_base.json")
    issue_lower = issue.lower()

    results = []

    for article in articles:
        matched_keywords = [
            keyword
            for keyword in article["keywords"]
            if keyword.lower() in issue_lower
        ]

        if matched_keywords:
            results.append({
                "id": article["id"],
                "title": article["title"],
                "guidance": article["guidance"],
                "matched_keywords": matched_keywords
            })

    return {
        "tool": "knowledge_base",
        "results": results,
        "result_count": len(results),
        "source": "local_knowledge_base"
    }


TOOL_REGISTRY = {
    "api_health": api_health,
    "authentication": authentication,
    "log_analyzer": log_analyzer,
    "knowledge_base": knowledge_base,
}


def run_diagnostic(tool_name: str, issue: str) -> dict:
    """Run only a registered diagnostic tool."""
    tool = TOOL_REGISTRY.get(tool_name)

    if tool is None:
        raise ValueError(f"Unknown diagnostic tool: {tool_name}")

    return tool(issue)