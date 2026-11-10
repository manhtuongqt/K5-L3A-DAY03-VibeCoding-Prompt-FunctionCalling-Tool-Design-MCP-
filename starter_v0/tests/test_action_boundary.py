"""An erroneous model call must not publish a message from any lab runner."""
from agent import ResearchAgent
from chat import execute_tool_call
from providers.base import ModelResponse, ToolCall


def test_cli_executor_blocks_model_supplied_confirmation(monkeypatch):
    calls = []
    monkeypatch.setitem(__import__("chat").TOOL_FUNCTIONS, "send", lambda **kwargs: calls.append(kwargs))
    result = execute_tool_call(ToolCall(name="send", args={"text": "Do not publish", "confirmed": True}))
    assert result["result"]["error"] == "action_disabled_in_lab_runner"
    assert calls == []


def test_eval_runner_records_bad_action_without_executing_it(monkeypatch):
    class FakeProvider:
        def complete(self, *args, **kwargs):
            return ModelResponse(text=None, tool_calls=[ToolCall(name="send", args={"text": "Cancelled", "confirmed": True})])
    calls = []
    monkeypatch.setitem(__import__("agent").TOOL_FUNCTIONS, "send", lambda **kwargs: calls.append(kwargs))
    result = ResearchAgent(FakeProvider(), system_prompt="test").run([{"role": "user", "content": "Cancel sending"}])
    assert result.tool_calls[0].name == "send"
    assert result.tool_results[0]["result"]["error"] == "action_disabled_in_lab_runner"
    assert calls == []
