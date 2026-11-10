"""Presentation helpers for the Day03 research workspace (no network calls)."""
from __future__ import annotations

from urllib.parse import urlparse

CSS = """
<style>
:root { --ink:#162c3c; --muted:#657482; --teal:#087e83; }
.stApp { background:#f7f8f5; color:var(--ink); }
.block-container { max-width:1120px; padding-top:2.1rem; padding-bottom:3rem; }
header[data-testid="stHeader"] { background:rgba(247,248,245,.94); }
[data-testid="stSidebar"] { background:#edf2f0; border-right:1px solid #dce5e0; }
[data-testid="stSidebar"] .block-container { padding-top:1.6rem; }
h1,h2,h3 { color:var(--ink); letter-spacing:-.035em; }
h1 { font-size:2.9rem!important; line-height:1.12!important; font-weight:720!important; }
h2 { font-size:1.45rem!important; }
h3 { font-size:1.05rem!important; }
p,li { line-height:1.65; }
.eyebrow { color:var(--teal); font-size:.72rem; letter-spacing:.16em; font-weight:750; text-transform:uppercase; margin-bottom:.8rem; }
.hero-description { color:#526777; max-width:650px; font-size:1.04rem; margin-bottom:1.25rem; }
.workspace-topline { display:flex; justify-content:space-between; gap:16px; align-items:center; margin-bottom:2rem; padding-bottom:1rem; border-bottom:1px solid #dae2dd; }
.brand { font-size:.95rem; font-weight:750; letter-spacing:-.02em; }
.brand-mark { display:inline-flex; background:#163c47; color:#fff; padding:4px 9px; border-radius:7px; margin-right:9px; font-size:.75rem; letter-spacing:.08em; }
.top-tag { font-size:.74rem; color:#477267; border:1px solid #ceded5; padding:5px 10px; border-radius:30px; white-space:nowrap; background:#eff6f1; }
.section-label { color:#526777; font-size:.72rem; letter-spacing:.12em; text-transform:uppercase; font-weight:700; margin:1.1rem 0 .65rem; }
.sample-number { color:#638881; font-size:.75rem; letter-spacing:.08em; margin-bottom:.55rem; }
.sample-title { color:#1b3a49; font-size:1.02rem; font-weight:700; margin-bottom:.35rem; }
.sample-copy { color:#647883; font-size:.87rem; line-height:1.55; min-height:65px; }
[data-testid="stVerticalBlockBorderWrapper"] > div { border-radius:14px!important; border-color:#d9e3dd!important; }
div.stButton > button { border-radius:9px; border:1px solid #c6d7cf; font-weight:600; color:#24605b; background:#f7faf7; min-height:2.6rem; }
div.stButton > button:hover { border-color:#087e83; color:#075e62; background:#edf7f1; }
div.stButton > button[kind="primary"] { background:#087e83; color:white; border-color:#087e83; }
[data-testid="stChatMessage"] { border:1px solid #dce4df; background:#fff; border-radius:14px; padding:1.15rem; margin-top:.8rem; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background:#edf3f1; border-color:#d6e1db; }
[data-testid="stChatInput"] { border-radius:12px; border:1px solid #a5c4bb; box-shadow:0 5px 22px #12342a09; }
[data-testid="stBottomBlockContainer"] { max-width:1120px; }
[data-testid="stBottom"] { background:#f7f8f5; }
.source-row { margin:.45rem 0; font-size:.88rem; }
.tool-summary { padding:.6rem .8rem; margin:.55rem 0; border-left:3px solid #67a89b; background:#f0f6f3; border-radius:0 7px 7px 0; color:#355d57; font-size:.85rem; }
.footer-note { color:#718078; font-size:.78rem; line-height:1.55; margin-top:1.2rem; }
@media(max-width:640px) { .block-container { padding:3.8rem 1rem 2rem; } h1 { font-size:2.05rem!important; } .workspace-topline { margin-top:1.75rem; margin-bottom:1.4rem; } .top-tag { font-size:.65rem; padding:4px 7px; } .sample-copy { min-height:0; } }
</style>
"""

PRESETS = [
    ("01", "Tìm nguồn", "Tìm tài liệu chính thức, chọn thông tin liên quan và trả lời kèm đường dẫn.",
     "Tìm 3 nguồn chính thức về Python dành cho người mới học. Với mỗi nguồn, ghi tiêu đề, URL và một câu giải thích nguồn đó giúp ích gì."),
    ("02", "Đọc một URL", "Gửi một bài cụ thể để đọc, tóm tắt ý chính và kiểm tra lại nguồn.",
     "Đọc https://docs.python.org/3/tutorial/ và tóm tắt 3 ý chính bằng tiếng Việt, kèm đường dẫn nguồn."),
    ("03", "Loại nguồn trùng", "Thử công cụ của nhóm với một danh sách mẫu; không cần gọi dịch vụ tìm kiếm.",
     'Dùng dedupe_sources để loại URL trùng trong danh sách sau, giữ thứ tự và mục xuất hiện đầu tiên. Trả lại danh sách và số mục đã loại: [{"title":"Python Tutorial","url":"https://docs.python.org/3/tutorial/"},{"title":"Python trùng","url":"https://docs.python.org/3/tutorial/"},{"title":"Python Library","url":"https://docs.python.org/3/library/"}]'),
]


def source_links(events: list[dict]) -> list[tuple[str, str]]:
    """Extract only actual URL fields in successful tool results, never model text."""
    found: list[tuple[str, str]] = []
    seen: set[str] = set()

    def visit(value: object) -> None:
        if isinstance(value, dict):
            if value.get("error"):
                return
            url = value.get("url")
            if isinstance(url, str):
                parsed = urlparse(url.strip())
                if parsed.scheme in {"https", "http"} and parsed.hostname and url.strip() not in seen:
                    seen.add(url.strip())
                    found.append((str(value.get("title") or parsed.hostname), url.strip()))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    for event in events:
        visit(event.get("result", {}))
    return found[:8]


def tool_label(name: str) -> str:
    return {"lookup":"Tìm nguồn trên web", "fetch":"Đọc nội dung URL", "dedupe_sources":"Loại URL trùng",
            "format":"Định dạng kết quả", "clarify":"Hỏi thêm thông tin", "timeline":"Đọc dòng thời gian X",
            "social_search":"Tìm bài trên X", "policy":"Tra cứu quy tắc", "send":"Gửi nội dung"}.get(name, name)
