from app.tools import (
    api_health,
    authentication,
    log_analyzer,
    knowledge_base,
    run_diagnostic,
)


ISSUE = (
    "My API started returning HTTP 401 errors "
    "after I rotated my API key."
)


def test_api_health():
    result = api_health(ISSUE)

    assert result["tool"] == "api_health"
    assert result["data"]["status"] == "healthy"


def test_authentication_detects_mismatch():
    result = authentication(ISSUE)

    assert result["status"] == "configuration_mismatch"
    assert result["configured_key_id"] != result["active_key_id"]
    assert result["secret_exposed"] is False


def test_log_analyzer_finds_401():
    result = log_analyzer(ISSUE)

    assert result["match_count"] > 0


def test_knowledge_base_finds_article():
    result = knowledge_base(ISSUE)

    assert result["result_count"] > 0


def test_unknown_tool_is_rejected():
    try:
        run_diagnostic("execute_shell", ISSUE)
    except ValueError:
        return

    assert False, "Unknown tool should be rejected"