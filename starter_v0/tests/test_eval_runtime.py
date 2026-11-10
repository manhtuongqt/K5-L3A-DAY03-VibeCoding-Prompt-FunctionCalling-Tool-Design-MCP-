"""Regression tests for nested JSON evaluation and credential-safe evidence."""
from __future__ import annotations

import json
from pathlib import Path

from run_eval import compare_subset, evaluate_phase_b, normalize_value
from redaction import redact_secrets
from env_loader import load_lab_env
from chat import write_transcript


def test_json_object_lists_can_be_compared_without_type_error():
    a = [{"url": "https://a.test", "title": "A"}, {"url": "https://b.test", "title": "B"}]
    assert normalize_value(a) == normalize_value(list(reversed(a)))
    assert compare_subset({"items": a}, {"items": a, "extra": 1})[0]


def test_nested_item_wrong_url_is_a_failure():
    case = {"failure_type": "wrong_arg_value", "expect": {"tool_calls": [
        {"name": "dedupe_sources", "args": {"items": [{"url": "https://a.test"}]}}
    ]}}
    result = evaluate_phase_b(case, [{"name": "dedupe_sources", "args": {"items": [{"url": "https://b.test"}]}}], None)
    assert not result["passed"]
    assert result["observed_mismatch"] == "wrong_arg_value"


def test_redaction_covers_known_keys_sensitive_fields_and_urls(monkeypatch):
    secret = "unit-test-value-12345678"
    monkeypatch.setenv("TEST_API_KEY", secret)
    data = {"error": f"Bearer {secret}", "api_key": "not-in-env",
            "url": "https://api.test/?key=unseen-secret-123",
            "telegram": "https://api.telegram.org/bot123:secret/sendMessage"}
    cleaned = json.dumps(redact_secrets(data))
    assert secret not in cleaned
    assert "not-in-env" not in cleaned
    assert "unseen-secret-123" not in cleaned
    assert "123:secret" not in cleaned


def test_transcript_writer_redacts_before_writing(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_API_KEY", "unit-secret-value-12345678")
    target = tmp_path / "session.json"
    write_transcript(target, {"turns": [{"error": "unit-secret-value-12345678"}]})
    assert "unit-secret-value-12345678" not in target.read_text(encoding="utf-8")
    assert json.loads(target.read_text(encoding="utf-8"))["turns"]


def test_unknown_gemini_style_key_is_not_saved():
    fake = "AIza" + "Z" * 35
    assert fake not in redact_secrets(f"User pasted {fake} into the chat")


def test_day03_env_path_accepts_bom_and_precedes_legacy(tmp_path, monkeypatch):
    modern = tmp_path / "modern.env"
    legacy = tmp_path / "legacy.env"
    modern.write_text("DAY03_TEST_SETTING=modern\n", encoding="utf-8-sig")
    legacy.write_text("DAY03_TEST_SETTING=legacy\n", encoding="utf-8")
    monkeypatch.setenv("DAY03_ENV_FILE", str(modern))
    monkeypatch.setenv("DAY04_ENV_FILE", str(legacy))
    monkeypatch.delenv("DAY03_TEST_SETTING", raising=False)
    load_lab_env(Path("unused"))
    assert __import__("os").environ["DAY03_TEST_SETTING"] == "modern"
