"""Fill final evidence tables from saved API runs and transcripts, without inventing outputs."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    report = ROOT / "artifacts" / "REPORT.md"
    text = report.read_text(encoding="utf-8")
    deployment = read("analysis/deployment_check.json")
    url = deployment["url"]
    old = "**Link chạy local:** <http://localhost:8501>. Địa chỉ này chỉ dùng trên máy đang chạy UI. Chưa có link demo công khai; không coi đây là bằng chứng đã deploy."
    text = text.replace(old, f"**Link dùng thử:** <{url}>. Link tạm thời phụ thuộc máy chạy Streamlit và Cloudflare Tunnel còn hoạt động. Local: <http://localhost:8501>. Đã kiểm tra HTTP 200 ở trang chính và health endpoint; bằng chứng: [deployment_check.json](../analysis/deployment_check.json).")
    text = text.replace("Nhóm có 3 người; tên hai thành viên còn lại và tên nhóm chưa được cung cấp, cần bổ sung trước khi nộp.", "Nhóm có 3 người; tên nhóm và hai thành viên còn lại để trống theo yêu cầu để nhóm tự bổ sung trước khi nộp.")
    marker = "# PHẦN A — Giới thiệu agent"
    if "| 2 |  |  |" not in text:
        table = "Tên nhóm: ____________________\n\n| STT | Thành viên | MSSV |\n|---|---|---|\n| 1 | Nguyễn Mạnh Tường | 2A202603646 |\n| 2 |  |  |\n| 3 |  |  |\n\n"
        text = text.replace(marker, table + marker)
    start = text.index("Root đã kiểm tra live HTTP 200")
    end = text.index("\n## A3.", start)
    text = text[:start] + ("Các lời gọi qua ứng dụng đã trả dữ liệu thật cho Tavily Search, Tavily Extract và tool local mới: [services_smoke.json](../analysis/services_smoke.json). Twitter API45 chưa được kiểm chứng dùng được: các lần kiểm tra gặp thiếu key, 403 hoặc 429 ở những thời điểm khác nhau. Tavily keyless cũng có giới hạn lưu lượng: trong run base v3, 16/17 tool call trả error, dù routing đạt 75%; group run v3 có 5/10 tool call trả error. Vì vậy điểm chọn tool không được diễn giải thành tỷ lệ hoàn thành nghiên cứu.\n\nCác runner eval/CLI và UI đều chặn gửi Telegram tại lớp thực thi trong bản cuối. G10 cho thấy model vẫn có thể gọi `send(confirmed=true)` sau khi người dùng hủy; cờ do model tự tạo không phải sự đồng ý của con người. Guard bổ sung sau các run giữ nguyên raw log và điểm routing, và có regression test riêng. Không có Telegram message thật nào được gửi.\n") + text[end:]
    text = text.replace("eval gốc so tool call đầu tiên và đối chiếu arguments theo subset", "eval gốc chấm tập tool call trong một lượt model và đối chiếu arguments theo subset")
    group_path = sorted((ROOT / "runs").glob("v3_B_group_*.json"))[-1]
    group = json.loads(group_path.read_text(encoding="utf-8"))
    outcomes = {case["id"]: case for case in group["results"]}
    lines = []
    for line in text.splitlines():
        if line.startswith("| G"):
            fields = line.split("|")
            case = outcomes.get(fields[1].strip())
            if case:
                fields[-2] = " " + ("PASS" if case["result"]["passed"] else "FAIL — " + str(case["result"].get("observed_mismatch"))) + " "
                line = "|".join(fields)
        lines.append(line)
    text = "\n".join(lines) + "\n"
    anchor = "G01 kiểm tra cả routing"
    summary = (f"Kết quả thật: **8/10 case (80%)**, single-turn 4/5 và multi-turn 4/5; không có provider error. [Run nhóm](../runs/{group_path.name}) dùng đúng prompt/tools hash v3. Hai lỗi còn lại: G05 gọi `lookup` cho yêu cầu viết code; G10 gọi `send(confirmed=true)` dù lượt mới nhất đã hủy gửi. Các lỗi được giữ nguyên để đánh giá boundary.\n\n")
    text = text.replace(anchor, summary + anchor)
    cli_path = sorted((ROOT / "transcripts").glob("v3_openai_*.transcript.json"))[-1]
    cli = json.loads(cli_path.read_text(encoding="utf-8"))
    rows = []
    for turn in cli["turns"]:
        events = turn.get("tool_events", [])
        names = ", ".join(event["tool"] for event in events) or "Không gọi tool"
        errors = sum(bool(event.get("result", {}).get("error")) for event in events)
        outcome = f"{errors} tool error; model báo lỗi dịch vụ" if errors else ("Đã đọc và tóm tắt bằng dữ liệu tool thật" if events else "Hỏi URL bằng text; chưa dùng clarify protocol")
        rows.append(f"| {turn['turn_index']} | {turn['user']} | {names} | `{cli['artifact_version']}` | {outcome} |")
    ui = read("analysis/ui_live_verification.json")
    ui_path = Path(ui["transcript"]).name
    b4 = "## B4. Hội thoại thật và UI\n\n"
    b4 += f"Kịch bản [demo_chat.json](../data/demo_chat.json) được script đưa vào `chat.py`, gọi API model thật và lưu [transcript 3 lượt](../transcripts/{cli_path.name}). Đây là kiểm tra live có input soạn trước, không phải phản hồi của bạn học hay buổi phỏng vấn.\n\n"
    b4 += "| Lượt | Yêu cầu | Tool call thật | Hash/phiên bản | Kết quả |\n|---|---|---|---|---|\n" + "\n".join(rows) + "\n\n"
    b4 += f"UI được kiểm tra bằng Streamlit AppTest gọi model thật: 0 exception, `dedupe_sources` được gọi, trả hai nguồn sau khi bỏ một URL trùng. [Bằng chứng UI](../analysis/ui_live_verification.json), [transcript UI](../transcripts/{ui_path}). Các test startup/reset/public mode chạy offline; không coi chúng là bằng chứng gọi model thật.\n\n"
    b4 += "Phiên demo công khai khóa provider/model/version, giới hạn 4 vòng tool và 4.000 ký tự input. Transcript lưu theo phiên và che key. Không gửi Telegram. Một lượt CLI tìm web gặp rate limit và model đã báo lỗi thay vì tạo nguồn giả.\n\n"
    a, b = text.index("## B4."), text.index("## B5.")
    text = text[:a] + b4 + text[b:]
    text = text.replace("Chờ kết quả test cuối", "PASS; có test contract và test input/error/duplicate semantics")
    text = text.replace("Toàn suite 141 passed, 0 skipped theo lần chạy tích hợp của B; riêng TODO/tool có 64 passed", "Toàn suite **144 passed, 0 failed, 0 skipped**; riêng TODO/tool có 64 passed. [Output pytest](../analysis/pytest_output.txt)")
    text = text.replace("| UI deploy công khai | Chưa có link | Chưa hoàn thành |", f"| UI deploy công khai | [Link demo]({url}), [health check](../analysis/deployment_check.json) | HTTP 200; link tạm theo phiên tunnel |")
    text = text.replace("Live smoke của root cần được liên kết tại đây sau khi chạy.", "Live smoke qua cùng tool implementation được lưu ở [services_smoke.json](../analysis/services_smoke.json).")
    text = text.replace("- Bước tiếp theo là xử lý các lỗi còn lại có mục tiêu:", "- Code guard cuối cùng chặn action ở eval/CLI và UI, độc lập với cờ confirmed do model tự điền; không sửa raw log để biến model FAIL thành PASS.\n- Bước tiếp theo là xử lý các lỗi còn lại có mục tiêu:")
    report.write_text(text, encoding="utf-8")
    print("Final report evidence tables updated from saved JSON.")


if __name__ == "__main__":
    main()
