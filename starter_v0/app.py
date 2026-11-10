"""Run from starter_v0: python -m streamlit run app.py."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from chat import now_iso, safe_slug, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from ui_support import redact_secrets, run_ui_turn
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).resolve().parent
PROMPT = ROOT / "artifacts" / "system_prompt.md"
TOOLS = ROOT / "artifacts" / "tools.yaml"


def start_session(provider_name: str, model: str, version: str, rounds: int) -> None:
    artifact = build_artifact_version(version, PROMPT, TOOLS)
    transcript_id = f"ui_{safe_slug(version)}_{safe_slug(provider_name)}_{datetime.now():%Y%m%dT%H%M%S%f}"
    st.session_state["lab_session"] = {
        "provider": provider_name, "model": model or None, "version": version,
        "rounds": rounds, "prompt": PROMPT.read_text(encoding="utf-8"),
        "declarations": load_tool_declarations(TOOLS), "context": [],
        "path": str(ROOT / "transcripts" / f"{transcript_id}.transcript.json"),
        "transcript": {"transcript_id": transcript_id, **artifact_version_dict(artifact),
                       "provider": provider_name, "model": model or None,
                       "system_prompt": "artifacts/system_prompt.md", "tools": "artifacts/tools.yaml",
                       "history_window": "full_session", "max_tool_rounds": rounds,
                       "interface": "streamlit", "send_enabled": False,
                       "created_at": now_iso(), "updated_at": now_iso(), "turns": []}}


def main() -> None:
    public_demo = os.getenv("LAB_PUBLIC_DEMO", "").strip() == "1"
    st.set_page_config(page_title="Day 03 Research Agent", page_icon=None, layout="wide")
    st.title("Research Agent — Day 03")
    st.write("Tìm nguồn, đọc bài và tổng hợp thông tin. Khi thiếu URL hoặc tài khoản, agent sẽ hỏi lại.")
    st.caption("Kết quả được tạo bằng API thật. Giao diện demo không gửi Telegram. Không nhập key hoặc dữ liệu riêng tư vào ô chat.")
    st.caption(os.getenv("LAB_TWITTER_STATUS", "Twitter/X: lần kiểm tra gần nhất bị giới hạn dịch vụ (HTTP 429); chưa bảo đảm có dữ liệu trực tiếp."))
    if public_demo:
        st.caption("Phiên demo công khai dùng cấu hình model cố định và tối đa 4 vòng công cụ mỗi lượt.")
    with st.sidebar:
        st.header("Phiên làm việc")
        names = ["openai", "openrouter", "gemini", "anthropic", "ollama"]
        default = os.getenv("LAB_PROVIDER", "openai")
        provider_name = st.selectbox("Provider", names, index=names.index(default) if default in names else 0, disabled=public_demo)
        provider_keys = {"openai": "OPENAI_API_KEY", "openrouter": "OPENROUTER_API_KEY",
                         "gemini": "GEMINI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}
        key_name = provider_keys.get(provider_name)
        if key_name and not os.getenv(key_name):
            st.warning(f"Chưa có {key_name} trên máy chạy. Thêm vào .env rồi khởi động lại UI.")
        model = st.text_input("Model (trống: dùng cấu hình provider)", value=os.getenv("LAB_MODEL", ""), disabled=public_demo)
        version = st.text_input("Nhãn phiên bản", value=os.getenv("LAB_VERSION", "v3"), disabled=public_demo)
        max_rounds = st.slider("Số vòng công cụ tối đa mỗi lượt", min_value=1, max_value=4 if public_demo else 10,
                               value=4 if public_demo else 5, disabled=public_demo)
        if public_demo:
            provider_name = default if default in names else "openai"
            model = os.getenv("LAB_MODEL", "")
            version = os.getenv("LAB_VERSION", "v3")
            max_rounds = 4
        show_tools = st.checkbox("Hiện nhật ký công cụ", value=True)
        if st.button("Bắt đầu phiên mới", use_container_width=True):
            start_session(provider_name, model.strip(), version.strip() or "v3", max_rounds)
            st.rerun()
        st.caption("Cấu hình mới chỉ áp dụng khi bắt đầu phiên mới. Key được đọc từ môi trường/.env trên máy chạy.")
    if "lab_session" not in st.session_state:
        start_session(provider_name, model.strip(), version.strip() or "v3", max_rounds)
    session = st.session_state["lab_session"]
    transcript = session["transcript"]
    st.caption(f"Provider: {session['provider']} · {transcript['artifact_version']}")
    current = build_artifact_version(session["version"], PROMPT, TOOLS)
    if current.artifact_version != transcript["artifact_version"]:
        st.warning("Prompt hoặc khai báo tool đã đổi. Hãy bắt đầu phiên mới để dùng phiên bản hiện tại.")
    if not transcript["turns"]:
        st.info("Thử: 'Bạn có thể làm gì?', 'Tóm tắt bài này' hoặc cung cấp các nguồn để loại URL trùng.")
    for turn in transcript["turns"]:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant"):
            st.markdown(turn.get("assistant_text") or "Lượt này chưa có câu trả lời.")
            if show_tools and turn.get("tool_events"):
                with st.expander("Các công cụ đã gọi"):
                    st.json(redact_secrets(turn["tool_events"]))
            if turn["status"] == "waiting_for_user":
                st.caption("Đã tạm dừng để chờ thông tin bổ sung từ người dùng.")
            if turn["status"] == "provider_error":
                st.error("Không gọi được model. Kiểm tra provider, key, model và kết nối rồi thử lại.")
    if transcript["turns"]:
        st.sidebar.download_button("Tải transcript JSON", json.dumps(redact_secrets(transcript), ensure_ascii=False, indent=2),
                                   file_name=f"{transcript['transcript_id']}.transcript.json", mime="application/json")
    user_text = st.chat_input("Nhập yêu cầu hoặc trả lời câu hỏi của agent", max_chars=4000 if public_demo else None)
    if user_text:
        turn = {"turn_index": len(transcript["turns"]) + 1, "started_at": now_iso(),
                "user": redact_secrets(user_text), "status": "started", "assistant_text": None,
                "rounds": [], "tool_events": []}
        with st.spinner("Agent đang xử lý yêu cầu..."):
            try:
                provider = make_provider(session["provider"])
                transcript["model"] = session["model"] or getattr(provider, "default_model", None)
                tools = to_openai_tools([item for item in session["declarations"] if item["name"] != "send"])
                messages = ([{"role": "system", "content": session["prompt"]}] if not session["context"] else list(session["context"]))
                messages.append({"role": "user", "content": user_text})
                result = run_ui_turn(provider=provider, messages=messages, tools=tools,
                                     model=session["model"], max_tool_rounds=session["rounds"])
                session["context"] = result.pop("context_messages")
                turn.update(redact_secrets(result))
            except Exception as exc:
                turn.update({"status": "provider_error", "error_type": type(exc).__name__,
                             "assistant_text": "Không kết nối được model. Hãy kiểm tra cấu hình API rồi gửi lại yêu cầu."})
        turn["ended_at"] = now_iso()
        transcript["turns"].append(turn)
        write_transcript(Path(session["path"]), redact_secrets(transcript))
        st.rerun()


if __name__ == "__main__":
    main()
