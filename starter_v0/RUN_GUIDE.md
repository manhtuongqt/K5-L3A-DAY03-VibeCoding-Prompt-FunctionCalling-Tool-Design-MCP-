# Chạy bài Day 03 trên Windows

Các lệnh bên dưới chạy trong thư mục `starter_v0`. Bài được phát triển từ upstream main `2469cd3`; bộ base eval giữ nguyên.

## 1. Cài môi trường

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Chỉ copy `.env.example` khi chưa có `.env`; không ghi đè key của máy đang dùng. Không đưa key vào notebook, báo cáo, transcript hoặc Git.

## 2. Chọn provider

Máy dùng để thực hiện bài này gọi CKEY qua endpoint OpenAI-compatible:

```dotenv
OPENAI_API_KEY=<key do CKEY cấp>
OPENAI_BASE_URL=https://api.xah.io/v1
LAB_PROVIDER=openai
LAB_MODEL=gemini-2.5-flash-lite
PROVIDER_TIMEOUT_SECONDS=45
PROVIDER_MAX_RETRIES=1
```

`openai` là tên adapter trong starter; `gemini-2.5-flash-lite` là model ID do gateway công bố, không phải tuyên bố rằng đã xác minh model bên trong gateway. Không đặt key của nhà cung cấp khác vào endpoint CKEY. Model ID cũ `gemini-3.8-flash` đã trả 404 trong lúc kiểm tra, nên các run chính dùng cùng model ID hiện tại.

Nếu dùng OpenRouter/OpenAI/Gemini chính thức, cấu hình key, provider và model tương ứng theo `../TOOL-SETUP.md`. Không dùng `OPENAI_BASE_URL` CKEY khi dùng key OpenAI chính thức.

```powershell
.\.venv\Scripts\python.exe scripts/preflight_provider.py --provider openai --model gemini-2.5-flash-lite
```

## 3. Dịch vụ công cụ

Tavily Search/Extract có chế độ keyless giới hạn lưu lượng theo hướng dẫn chính thức mà người dùng cung cấp:

```dotenv
TAVILY_ACCESS_MODE=keyless
FETCH_PROVIDER=auto
```

`lookup` dùng REST Tavily Search. `fetch` ưu tiên Firecrawl nếu có `FIRECRAWL_API_KEY`, nếu không thì dùng Tavily Extract khi đã bật keyless. Đây là lời gọi mạng thật, không phải dữ liệu mock. Khi có Tavily key thì key được ưu tiên cho Search. Muốn chỉ dùng Firecrawl, đặt `FETCH_PROVIDER=firecrawl`.

`timeline` và `social_search` cần `RAPIDAPI_KEY` cùng quyền đăng ký Twitter API45. Một key RapidAPI chung chưa chứng minh đã có subscription hoặc quota cho API45. Khi dịch vụ trả 403/429, tool trả error dict; không tự tạo tweet thay thế. Tình trạng API được ghi trong bằng chứng smoke/eval theo thời điểm.

Telegram là bonus. Bản cuối chặn gửi ở UI, CLI và eval runner, dù model tự đề xuất `send(confirmed=true)`. Muốn làm bonus gửi thật phải bổ sung luồng con người xác nhận ở lớp ứng dụng; một cờ do model tạo không đủ. Các unit test của hàm tool dùng mock HTTP, không gửi tin thật.

## 4. Kiểm thử và eval

Artifact hiện tại là **v7** (base 85%, bộ nhóm 90% trong các run đã lưu). V0–v3 là lịch sử bắt buộc của lab; v4–v7 là các thử nghiệm bổ sung, không ghi đè lịch sử. Nếu máy không phân giải được gateway, thay `run_eval.py` trong lệnh bên dưới bằng `scripts/run_eval_live.py --dns-fallback`; đây vẫn là evaluator chuẩn, không sửa logic chấm.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe run_eval.py --provider openai --model gemini-2.5-flash-lite --version v7 --suite base --eval-cases data/eval_base.json
.\.venv\Scripts\python.exe run_eval.py --provider openai --model gemini-2.5-flash-lite --version v7 --suite group --eval-cases data/eval_group.json
```

Mỗi lệnh eval gọi model/API thật. `--suite` chỉ là nhãn; `--eval-cases` chọn dữ liệu. Muốn tái chạy phiên bản cũ, chỉ định cả `--system-prompt artifacts/versions/<version>/system_prompt.md` và `--tools artifacts/versions/<version>/tools.yaml` để khớp hash. Tên phiên bản không tự khôi phục file.

```powershell
.\.venv\Scripts\python.exe scripts/analyze_evidence.py runs/ --output-dir analysis
```

Routing PASS không chứng minh tool đã lấy được dữ liệu. Xem thêm `tool_results`, số provider error và `analysis/tool_execution.csv`. Bộ multi-turn eval chấm lượt cuối với lịch sử đã cho; transcript chat mới cho thấy vòng tool thực tế.

## 5. Giao diện và hội thoại

Giao diện Research Desk và kịch bản trình bày cho nhóm khác: [DEMO_GUIDE.md](DEMO_GUIDE.md). Có nút chọn mẫu, tiến trình công cụ thật, liên kết nguồn và tải transcript. Khởi động chế độ public với cấu hình khóa sẵn:

```powershell
.\.venv\Scripts\python.exe scripts/serve_demo.py
```

Nếu DNS hệ thống không phân giải được gateway CKEY, thêm `--dns-fallback`. Tùy chọn chỉ tác động tiến trình demo, không sửa DNS Windows, endpoint hoặc kiểm tra chứng chỉ TLS.

Để mở chế độ local có thể sửa cấu hình, dùng lệnh thông thường:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Mở `http://localhost:8501`. Khi prompt/tools đổi, tạo phiên mới để UI nạp snapshot mới. Transcript lưu trong `transcripts/` và có thể tải từ sidebar. Khóa bí mật được che trước khi lưu log; không chủ động nhập dữ liệu nhạy cảm vào chat.

```powershell
.\.venv\Scripts\python.exe chat.py --provider openai --model gemini-2.5-flash-lite --version v7
```

Để chia sẻ demo tạm thời, chạy UI với `LAB_PUBLIC_DEMO=1`, `LAB_PROVIDER`, `LAB_MODEL`, `LAB_VERSION` trên máy chủ. Chế độ public khóa các lựa chọn provider/model/version và giới hạn vòng tool; không tự gửi Telegram. Sau đó mở tunnel theo hướng dẫn README:

```powershell
cloudflared tunnel --url http://127.0.0.1:8501
```

Link `trycloudflare.com` chỉ tồn tại khi máy chạy UI và tunnel còn hoạt động. Link ghi trong REPORT là kết quả của một phiên demo, không phải hosting thường trực.

## 6. Hoàn thiện phần nhóm

Đối chiếu lần cuối theo [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md).

Hai thành viên còn lại tự bổ sung tên/MSSV vào REPORT; người dùng yêu cầu để trống các thông tin này trong lúc triển khai. Nhóm cần tự thử UI, đọc lại nguồn, kiểm tra kết quả và nộp repo lên LMS bằng tài khoản phù hợp. Các vai A/B/C của AI được ghi riêng với danh sách sinh viên.

Tài liệu Tavily: https://www.tavily.com/agent-setup/SKILL.md
