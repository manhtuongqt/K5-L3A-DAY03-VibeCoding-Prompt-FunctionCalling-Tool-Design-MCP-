"""Session helpers for Streamlit; all model responses come from the chosen provider."""
from __future__ import annotations

from typing import Any

from chat import assistant_tool_message, execute_tool_call, tool_results_message
from redaction import redact_secrets


def run_ui_turn(*, provider: Any, messages: list[dict[str, str]], tools: list[dict[str, Any]],
                model: str | None, max_tool_rounds: int = 5) -> dict[str, Any]:
    """Run the same tool protocol as chat.py, retaining context at a clarification pause.

    The demo never executes outbound Telegram sends, even if a model invents a call.
    A session can therefore be shared for read-only research without publishing data.
    """
    working = list(messages)
    rounds: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    for index in range(1, max_tool_rounds + 1):
        response = provider.complete(working, tools, model=model, temperature=0.0)
        calls = response.tool_calls
        record = {"round": index, "assistant_text": response.text,
                  "tool_calls": [{"name": call.name, "args": call.args} for call in calls],
                  "tool_results": []}
        if not calls:
            text = response.text or "Model chưa trả về nội dung. Hãy thử diễn đạt lại yêu cầu."
            working.append({"role": "assistant", "content": text})
            rounds.append(record)
            return {"status": "answered", "assistant_text": text, "rounds": rounds,
                    "tool_events": events, "context_messages": working}
        working.append(assistant_tool_message(response.text, calls))
        pending_question = None
        for call in calls:
            if call.name == "send":
                event = {"tool": "send", "args": call.args, "result": {
                    "error": "action_disabled_in_demo",
                    "message": "Giao diện demo không gửi Telegram. Nội dung chỉ được xem trước."}}
            else:
                event = redact_secrets(execute_tool_call(call))
            events.append(event)
            record["tool_results"].append(event)
            result = event.get("result", {})
            if isinstance(result, dict) and result.get("awaiting_user"):
                pending_question = result.get("question") or call.args.get("question") or "Bạn bổ sung thông tin nhé."
                # Do not execute other calls after the model has requested missing information.
                break
        rounds.append(record)
        working.append(tool_results_message(record["tool_results"]))
        if pending_question:
            working.append({"role": "assistant", "content": pending_question})
            return {"status": "waiting_for_user", "assistant_text": pending_question,
                    "rounds": rounds, "tool_events": events, "context_messages": working}
    text = f"Đã dừng sau {max_tool_rounds} vòng công cụ. Bạn có thể thu hẹp yêu cầu hoặc xem nhật ký."
    working.append({"role": "assistant", "content": text})
    return {"status": "max_tool_rounds", "assistant_text": text, "rounds": rounds,
            "tool_events": events, "context_messages": working}
