"""Streamlit smoke tests: configuration and reruns never call a provider."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def test_public_ui_locks_server_configuration_without_calling_model(monkeypatch):
    calls = []

    def forbidden_provider(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("Startup must not call the provider")

    monkeypatch.setenv("LAB_PUBLIC_DEMO", "1")
    monkeypatch.setenv("LAB_PROVIDER", "openai")
    monkeypatch.setenv("LAB_MODEL", "test-model")
    monkeypatch.setenv("LAB_VERSION", "test-version")
    monkeypatch.setattr("providers.make_provider", forbidden_provider)
    app = AppTest.from_file(str(APP)).run(timeout=20)
    assert not app.exception
    assert app.sidebar.selectbox[0].disabled
    assert all(widget.disabled for widget in app.sidebar.text_input)
    assert app.sidebar.slider[0].disabled
    assert app.sidebar.slider[0].value == 4
    assert app.chat_input[0].max_chars == 4000
    session = app.session_state["lab_session"]
    assert session["model"] == "test-model"
    assert session["version"] == "test-version"
    assert session["rounds"] == 4
    app.sidebar.button[0].click().run(timeout=20)
    assert not app.exception
    assert not app.session_state["lab_session"]["transcript"]["turns"]
    assert calls == []


def test_local_ui_keeps_configuration_editable(monkeypatch):
    monkeypatch.setenv("LAB_PUBLIC_DEMO", "0")
    app = AppTest.from_file(str(APP)).run(timeout=20)
    assert not app.exception
    assert not app.sidebar.selectbox[0].disabled
    assert all(not widget.disabled for widget in app.sidebar.text_input)
    assert not app.sidebar.slider[0].disabled
    assert app.sidebar.slider[0].value == 5
