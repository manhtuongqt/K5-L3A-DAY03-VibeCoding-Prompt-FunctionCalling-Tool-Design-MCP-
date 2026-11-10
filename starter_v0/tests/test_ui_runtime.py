"""Offline regression tests for browser chat pause/resume and action boundaries."""
from providers.base import ModelResponse, ToolCall
from ui_support import redact_secrets, run_ui_turn


class ScriptedProvider:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.seen = []

    def complete(self, messages, tools=None, **kwargs):
        self.seen.append(list(messages))
        return next(self.responses)


def test_clarify_pauses_then_next_turn_retains_question_and_user_answer():
    provider = ScriptedProvider([
        ModelResponse(tool_calls=[ToolCall("clarify", {"question": "Which URL?", "response_type": "text"})]),
        ModelResponse(text="The new URL is available."),
    ])
    first = run_ui_turn(provider=provider, messages=[{"role": "user", "content": "Read this."}],
                        tools=[], model=None)
    assert first["status"] == "waiting_for_user"
    assert len(provider.seen) == 1
    assert first["tool_events"][0]["result"]["awaiting_user"] is True
    second = run_ui_turn(provider=provider,
                         messages=first["context_messages"] + [{"role": "user", "content": "https://example.com"}],
                         tools=[], model=None)
    assert second["status"] == "answered"
    context = provider.seen[1]
    assert context[-1]["content"] == "https://example.com"
    assert any("TOOL_RESULTS_JSON" in item["content"] for item in context)
    assert any(item["content"] == "Which URL?" for item in context)


def test_ui_never_executes_send_even_if_model_claims_confirmation(monkeypatch):
    executed = []
    monkeypatch.setattr("ui_support.execute_tool_call", lambda call: executed.append(call))
    provider = ScriptedProvider([
        ModelResponse(tool_calls=[ToolCall("send", {"text": "Private text", "confirmed": True})]),
        ModelResponse(text="Sending is disabled in this demo."),
    ])
    result = run_ui_turn(provider=provider, messages=[], tools=[], model=None)
    assert executed == []
    assert result["tool_events"][0]["result"]["error"] == "action_disabled_in_demo"


def test_redactor_removes_environment_secret_from_nested_error(monkeypatch):
    monkeypatch.setenv("TEST_PROVIDER_API_KEY", "secret-that-must-not-leak")
    value = {"error": ["Bearer secret-that-must-not-leak", "sk-project-test_secret_123456"]}
    output = redact_secrets(value)
    assert "secret-that-must-not-leak" not in str(output)
    assert "sk-project-test_secret_123456" not in str(output)
    assert "[REDACTED]" in str(output)


def test_live_progress_reports_actual_tools_and_redacts_results(monkeypatch):
    monkeypatch.setenv("TEST_PROVIDER_API_KEY", "private-progress-secret")
    monkeypatch.setattr("ui_support.execute_tool_call", lambda call: {
        "tool": call.name, "result": {"error": "private-progress-secret"}})
    provider = ScriptedProvider([
        ModelResponse(tool_calls=[ToolCall("lookup", {"query": "Python"})]),
        ModelResponse(text="Service unavailable."),
    ])
    progress = []
    result = run_ui_turn(provider=provider, messages=[], tools=[], model=None,
                         on_event=progress.append)
    assert [event["phase"] for event in progress] == ["tool_start", "tool_end"]
    assert all(event["tool"] == "lookup" for event in progress)
    assert "private-progress-secret" not in str(progress)
    assert progress[1]["result"]["error"] == "[REDACTED]"
    assert result["status"] == "answered"
