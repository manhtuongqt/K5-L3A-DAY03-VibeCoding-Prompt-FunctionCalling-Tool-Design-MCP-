"""Run from starter_v0: python -m streamlit run app.py."""
from __future__ import annotations

import json
import os
import time
from html import escape
from datetime import datetime
from pathlib import Path

import streamlit as st

from chat import now_iso, safe_slug, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from ui_support import redact_secrets, run_ui_turn
from versioning import artifact_version_dict, build_artifact_version
from ui_design import CSS, PRESETS, source_links, tool_label

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


def render_tool_results(events: list[dict], show_tools: bool) -> None:
    """Show usable evidence first and keep diagnostic details opt-in."""
    if not events:
        return
    completed, errors = [], []
    for event in events:
        result = event.get("result", {})
        name = event.get("tool", "tool")
        if isinstance(result, dict) and result.get("error"):
            errors.append(tool_label(name))
        else:
            completed.append(tool_label(name))
        if name == "dedupe_sources" and isinstance(result, dict) and "duplicates_removed" in result:
            st.caption(f"Đã kiểm tra {result['input_count']} mục · Giữ {result['item_count']} nguồn · Loại {result['duplicates_removed']} mục trùng")
    if completed:
        names = " → ".join(dict.fromkeys(completed))
        st.markdown(f'<div class="tool-summary">{escape(names)}</div>', unsafe_allow_html=True)
    if errors:
        st.warning("Một số công cụ chưa trả dữ liệu: " + ", ".join(dict.fromkeys(errors)) + ". Hãy thử lại sau hoặc dùng mẫu Loại nguồn trùng để kiểm tra công cụ cục bộ. Agent không coi dữ liệu lỗi là nguồn đã kiểm chứng.")
    links = source_links(events)
    if links:
        with st.expander(f"Liên kết từ kết quả công cụ ({len(links)})", expanded=False):
            st.caption("Với mẫu loại trùng, đây là URL bạn cung cấp, chưa được đọc hay xác minh nội dung.")
            for title, url in links:
                st.link_button(title[:100], url, use_container_width=True)
    if show_tools:
        with st.expander("Nhật ký công cụ · dữ liệu chi tiết"):
            st.json(redact_secrets(events))


def choose_preset(text: str) -> None:
    st.session_state["research_input"] = text
    st.session_state["preset_selected"] = True


def main() -> None:
    public_demo = os.getenv("LAB_PUBLIC_DEMO", "").strip() == "1"
    st.set_page_config(page_title="Research Desk · Day 03", page_icon=None, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    with st.sidebar:
        st.markdown('<div class="eyebrow">Day 03 / Tool calling lab</div>', unsafe_allow_html=True)
        st.header("Phiên làm việc")
        st.caption("Mỗi phiên giữ ngữ cảnh hội thoại và nhật ký riêng để tải về.")
        names = ["openai", "openrouter", "gemini", "anthropic", "ollama"]
        default = os.getenv("LAB_PROVIDER", "openai")
        provider_name = st.selectbox("Provider", names, index=names.index(default) if default in names else 0, disabled=public_demo)
        provider_keys = {"openai": "OPENAI_API_KEY", "openrouter": "OPENROUTER_API_KEY",
                         "gemini": "GEMINI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}
        key_name = provider_keys.get(provider_name)
        if key_name and not os.getenv(key_name):
            st.warning("Model chưa được cấu hình trên máy chủ. Hãy báo người vận hành demo.")
        with st.expander("Cấu hình model", expanded=not public_demo):
            model = st.text_input("Model (trống: dùng cấu hình provider)", value=os.getenv("LAB_MODEL", ""), disabled=public_demo)
            version = st.text_input("Nhãn phiên bản", value=os.getenv("LAB_VERSION", "v7"), disabled=public_demo)
            max_rounds = st.slider("Số vòng công cụ tối đa mỗi lượt", min_value=1, max_value=4 if public_demo else 10,
                                   value=4 if public_demo else 5, disabled=public_demo)
            if public_demo:
                st.caption("Cấu hình được cố định để các nhóm cùng thử trên một phiên bản.")
        if public_demo:
            provider_name = default if default in names else "openai"
            model = os.getenv("LAB_MODEL", "")
            version = os.getenv("LAB_VERSION", "v7")
            max_rounds = 4
        show_tools = st.checkbox("Hiện nhật ký công cụ", value=True)
        if st.button("Bắt đầu phiên mới", use_container_width=True):
            start_session(provider_name, model.strip(), version.strip() or "v7", max_rounds)
            st.rerun()
        st.caption("Bắt đầu phiên mới sẽ xóa hội thoại trên màn hình. Tải transcript trước nếu cần lưu lại.")
        st.divider()
        st.markdown("**Trạng thái dịch vụ**")
        st.caption("Web: có thể bị giới hạn lượt gọi.\n\nLoại trùng: xử lý cục bộ; vẫn cần model để gọi công cụ.")
        st.caption(os.getenv("LAB_TWITTER_STATUS", "X / Twitter: chưa kết nối ổn định, hiện không dùng làm luồng demo chính."))
        st.markdown('<div class="footer-note">Không nhập API key hoặc thông tin riêng tư. Demo không gửi Telegram. Hội thoại được lưu trên máy chủ phục vụ bài lab.</div>', unsafe_allow_html=True)
    if "lab_session" not in st.session_state:
        start_session(provider_name, model.strip(), version.strip() or "v7", max_rounds)
    session = st.session_state["lab_session"]
    transcript = session["transcript"]
    st.markdown('<div class="workspace-topline"><span class="brand"><span class="brand-mark">RD</span>Research Desk</span><span class="top-tag">Day 03 · Demo tương tác</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">Từ câu hỏi đến nguồn thông tin</div>', unsafe_allow_html=True)
    st.title("Tìm hiểu rõ hơn, từng nguồn một.")
    st.markdown('<p class="hero-description">Tìm tài liệu, đọc nội dung từ URL và sắp xếp nguồn trong một cuộc hội thoại. Agent chọn công cụ theo yêu cầu; bạn kiểm tra nguồn và quyết định sử dụng kết quả.</p>', unsafe_allow_html=True)
    current = build_artifact_version(session["version"], PROMPT, TOOLS)
    if current.artifact_version != transcript["artifact_version"]:
        st.warning("Prompt hoặc khai báo tool đã đổi. Hãy bắt đầu phiên mới để dùng phiên bản hiện tại.")
    if not transcript["turns"]:
        st.markdown('<div class="section-label">Bắt đầu với một việc cụ thể</div>', unsafe_allow_html=True)
        for col, (number, title, description, prompt) in zip(st.columns(3), PRESETS):
            with col:
                with st.container(border=True):
                    st.markdown(f'<div class="sample-number">{number} / THỬ NHANH</div><div class="sample-title">{title}</div><div class="sample-copy">{description}</div>', unsafe_allow_html=True)
                    st.button("Dùng mẫu " + title.lower(), key="preset_" + number, on_click=choose_preset, args=(prompt,), use_container_width=True)
        if st.session_state.pop("preset_selected", False):
            st.info("Đã điền mẫu vào ô chat phía dưới. Bạn có thể sửa nội dung, sau đó nhấn gửi để chạy.")
    with st.expander("Cách dùng demo trong 1 phút", expanded=False):
        st.markdown("**1. Chọn mẫu hoặc nhập câu hỏi.** Với bài cụ thể, dán URL đầy đủ.\n\n**2. Gửi và theo dõi công cụ.** Nếu agent hỏi lại, trả lời tiếp ngay trong ô chat; phiên vẫn giữ ngữ cảnh.\n\n**3. Kiểm tra kết quả.** Mở nguồn và nhật ký để biết công cụ đã trả dữ liệu gì, rồi tải transcript ở thanh bên nếu cần làm bằng chứng.")
        st.caption("Tìm nguồn và đọc URL phụ thuộc dịch vụ bên ngoài. Một câu trả lời của model không đồng nghĩa với nguồn đã được xác minh. Các nút mẫu chỉ điền nội dung, chưa gọi API.")
    if transcript["turns"]:
        st.markdown('<div class="section-label">Hội thoại nghiên cứu</div>', unsafe_allow_html=True)
    for turn in transcript["turns"]:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant"):
            st.markdown(turn.get("assistant_text") or "Lượt này chưa có câu trả lời.")
            render_tool_results(turn.get("tool_events", []), show_tools)
            if turn["status"] == "waiting_for_user":
                st.caption("Đang chờ bạn bổ sung thông tin. Trả lời tiếp trong ô chat bên dưới.")
            if turn["status"] == "provider_error":
                st.error("Chưa kết nối được model. Bạn có thể thử lại; nếu vẫn lỗi, báo người vận hành kiểm tra dịch vụ.")
            if turn.get("elapsed_seconds") is not None:
                st.caption(f"Thời gian xử lý: {turn['elapsed_seconds']:.1f} giây")
    if transcript["turns"]:
        st.sidebar.download_button("Tải transcript JSON", json.dumps(redact_secrets(transcript), ensure_ascii=False, indent=2),
                                   file_name=f"{transcript['transcript_id']}.transcript.json", mime="application/json", use_container_width=True)
        st.sidebar.caption(f"{len(transcript['turns'])} lượt trao đổi · Phiên {session['version']}")
    with st.sidebar.expander("Thông tin phiên"):
        st.caption(f"Provider: {session['provider']}\n\nModel: {session['model'] or 'Mặc định'}\n\nPhiên bản: {transcript['artifact_version']}")
    user_text = st.chat_input("Bạn muốn tìm hiểu điều gì? Nhập câu hỏi hoặc dán URL…", key="research_input", max_chars=4000 if public_demo else None)
    if user_text:
        started = time.monotonic()
        turn = {"turn_index": len(transcript["turns"]) + 1, "started_at": now_iso(),
                "user": redact_secrets(user_text), "status": "started", "assistant_text": None,
                "rounds": [], "tool_events": []}
        with st.status("Đang đọc yêu cầu…", expanded=True) as progress:
            def update_progress(event: dict) -> None:
                label = tool_label(event.get("tool", "tool"))
                if event.get("phase") == "tool_start":
                    progress.update(label=label + "…")
                    st.write(label)
                else:
                    result = event.get("result", {})
                    if isinstance(result, dict) and result.get("error"):
                        st.caption("Dịch vụ chưa trả dữ liệu. Agent sẽ nhận trạng thái lỗi để xử lý tiếp.")
                    else:
                        st.caption("Đã nhận kết quả công cụ.")
            try:
                provider = make_provider(session["provider"])
                transcript["model"] = session["model"] or getattr(provider, "default_model", None)
                tools = to_openai_tools([item for item in session["declarations"] if item["name"] != "send"])
                messages = ([{"role": "system", "content": session["prompt"]}] if not session["context"] else list(session["context"]))
                messages.append({"role": "user", "content": user_text})
                result = run_ui_turn(provider=provider, messages=messages, tools=tools,
                                     model=session["model"], max_tool_rounds=session["rounds"], on_event=update_progress)
                session["context"] = result.pop("context_messages")
                turn.update(redact_secrets(result))
                progress.update(label="Đã xử lý yêu cầu", state="complete", expanded=False)
            except Exception as exc:
                turn.update({"status": "provider_error", "error_type": type(exc).__name__,
                             "assistant_text": "Chưa kết nối được model. Hãy thử lại sau hoặc báo người vận hành demo kiểm tra cấu hình API."})
                progress.update(label="Chưa kết nối được dịch vụ", state="error", expanded=False)
        turn["ended_at"] = now_iso()
        turn["elapsed_seconds"] = round(time.monotonic() - started, 3)
        transcript["turns"].append(turn)
        write_transcript(Path(session["path"]), redact_secrets(transcript))
        st.rerun()


if __name__ == "__main__":
    main()
