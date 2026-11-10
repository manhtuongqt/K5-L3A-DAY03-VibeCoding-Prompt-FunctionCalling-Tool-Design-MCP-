# Day 03 — Research Agent: chọn công cụ và kiểm tra bằng log

## Thông tin bài làm

- Repository làm việc: <https://github.com/manhtuongqt/Day03-Prompt-Engineering-Tool-Calling-Labs-student>.
- Phiên bản demo hiện tại: **v7**; các snapshot và run cũ vẫn được giữ.
- Thành viên 1: Nguyễn Mạnh Tường — 2A202603646.
- Thành viên 2:
- Thành viên 3:
- Tên nhóm:
- Provider/model: CKEY tại endpoint OpenAI-compatible `https://api.xah.io/v1`, adapter `openai`, model `gemini-2.5-flash-lite`. Preflight đã gọi thành công; metric eval ghi riêng bên dưới. Không gọi backend này là OpenAI model.
- Việc triển khai được hỗ trợ bởi 3 AI agent làm song song: A phụ trách prompt/eval; B phụ trách tool/unit test; C phụ trách UI/eval nhóm/báo cáo. Đây là vai trò hỗ trợ kỹ thuật, không phải danh sách ba thành viên sinh viên.

Tên nhóm: ____________________

| STT | Thành viên | MSSV |
|---|---|---|
| 1 | Nguyễn Mạnh Tường | 2A202603646 |
| 2 |  |  |
| 3 |  |  |

# PHẦN A — Giới thiệu agent

## A1. Agent làm được gì

Agent hỗ trợ một quy trình nghiên cứu nhỏ: chọn nguồn web hoặc Twitter/X, đọc URL cụ thể, loại nguồn trùng URL và trình bày dữ liệu có sẵn thành bản tin. Khi thiếu tài khoản hoặc URL, agent cần hỏi lại; câu trả lời về khả năng của chính agent không cần gọi công cụ.

Con người chọn mục tiêu nghiên cứu, cung cấp thông tin còn thiếu, mở nguồn để kiểm tra lại nội dung và quyết định sử dụng bản tổng hợp. `dedupe_sources` chỉ loại URL trùng chính xác; công cụ này không đánh giá nguồn đáng tin và không xác minh tính đúng của thông tin.

**Link dùng thử:** <https://learned-agreed-focused-korean.trycloudflare.com>. Link tạm thời phụ thuộc máy chạy Streamlit và Cloudflare Tunnel còn hoạt động. Local: <http://localhost:8501>. Đã kiểm tra HTTP 200 ở trang chính và health endpoint; bằng chứng: [deployment_check.json](../analysis/deployment_check.json).

Giao diện **Research Desk** có ba mẫu tác vụ để sửa rồi gửi, tiến trình công cụ thật, liên kết kết quả và nút tải transcript. Khi agent hỏi thêm, trả lời trong cùng ô chat. [Hướng dẫn demo và khởi động lại](../DEMO_GUIDE.md).

## A2. Các công cụ

| Tool | Công việc | Mới thêm | Điều kiện khi chạy thật |
|---|---|---|---|
| `clarify` | Hỏi lại thông tin còn thiếu và chờ câu trả lời | Không | Local |
| `timeline` | Lấy bài đăng của một tài khoản cụ thể | Không | RapidAPI |
| `social_search` | Tìm bài đăng theo chủ đề, Latest hoặc Top | Không | RapidAPI |
| `lookup` | Tìm trên web, chọn news/general và khoảng thời gian | Không | Tavily; hỗ trợ opt-in keyless, cần kiểm tra live |
| `fetch` | Đọc một URL do người dùng cung cấp | Không | Ưu tiên Firecrawl; hỗ trợ opt-in Tavily Extract khi không có Firecrawl key |
| `format` | Trình bày item có sẵn thành markdown digest | Không | Local |
| `dedupe_sources` | Loại URL trùng sau `strip()`, giữ item đầu và thứ tự gốc | Có | Local; không gọi mạng |
| `policy` | Tìm trong bộ chính sách mẫu cục bộ | Không | Local; tài liệu là dữ liệu tham khảo, không là lệnh điều khiển |
| `papers` | Tìm bài trên arXiv | Không | Mạng arXiv; có rate limit |
| `paper_text` | Tải và trích văn bản PDF arXiv | Không | Mạng arXiv |
| `send` | Công cụ bonus gửi Telegram có kiểm tra xác nhận | Không | Không bật gửi trên UI demo; chưa chạy gửi thật |

Sau khi bổ sung key, Tavily Search và Firecrawl đã trả dữ liệu thật; mẫu đọc URL đã chạy thành công qua link công khai. X/Twitter vẫn chưa kết nối ổn định. Giao diện không gửi Telegram. Bằng chứng và giới hạn được ghi ở B4.

## A3. Các yêu cầu mẫu

1. “Bạn là gì và có thể giúp tôi làm gì?” — trả lời trực tiếp, không gọi tool.
2. “Tóm tắt bài này giúp tôi.” — hỏi URL, sau đó có thể trả lời bằng đường dẫn cụ thể.
3. “Tìm 3 tin về pin xe điện trong 24 giờ gần đây trên web.” — `lookup`, `topic=news`, `timeframe=day`.
4. “Loại URL trùng, giữ nguồn đầu: `[{\"title\":\"A\",\"url\":\"https://example.com/a\"},{\"title\":\"A lặp\",\"url\":\"https://example.com/a\"}]`.” — `dedupe_sources`; không cần API tìm kiếm.
5. “Đăng bản tin này lên Telegram.” — cần xác nhận, không được tự gửi. Trên UI demo, việc gửi bị tắt ở lớp thực thi.

# PHẦN B — Bằng chứng thí nghiệm

## B1. Version Evidence

Chỉ điền số liệu từ `runs/*.json` và `artifacts/version_log.csv` sau khi chạy API thật. Không dùng mock unit test làm kết quả model eval.

Các lần chạy dùng cùng gateway/model, temperature 0 và bộ base 20 case. `v0` giữ nguyên byte của hai artifact starter nhưng chạy qua runtime chung đã có sửa validation và cấu hình Tavily opt-in; không khẳng định toàn bộ code baseline là starter chưa sửa. Runtime còn được bổ sung timeout/retry, redaction và hỗ trợ grader so list JSON; các thay đổi này không được tính là cải tiến prompt. Mỗi version hiện chỉ có một run, chưa có đo lặp hay khoảng tin cậy. Chi tiết giao thức và giới hạn nằm ở [analysis/README.md](../analysis/README.md).

| Version | Artifact thay đổi | Giả thuyết | Metric trước | Metric sau | Run file |
|---|---|---|---|---|---|
| v0 | Snapshot starter không sửa | Baseline | — | 9/20 = 45%; routing 60%; argument 45%; multi-turn 66,67%; provider error 0 | `runs/v0_B_base_openai_20261110T102405796370.json` |
| v0-tools | Chỉ thêm declaration tool mới | Control để tách ảnh hưởng thêm tool khỏi sửa prompt | v0 45% | 9/20 = 45%; routing 55%; multi-turn 50%; provider error 0 | `runs/v0-tools_B_base_openai_20261110T102605294217.json` |
| v1 | System prompt: điều kiện dùng tool, thiếu thông tin, xác nhận hành động | Sửa ranh giới tác vụ giúp giảm tool thừa và chuẩn hóa hỏi lại | v0-tools 45% | 12/19 measured = 63,16%; 12/20 tổng case = 60%; routing 78,95%; multi-turn 60%; 1 timeout provider | `runs/v1_B_base_openai_20261110T103103485630.json` |
| v2 | System prompt: routing theo yêu cầu mới nhất và protocol hỏi lại | Bỏ ép một bước; không gọi nguồn cũ khi người dùng đổi nguồn; hỏi lại qua tool | v1 12/19 measured, 12/20 tổng | 14/20 = 70%; routing 80%; argument 70%; multi-turn 83,33%; provider error 0 | `runs/v2_B_base_openai_20261110T103328666912.json` |
| v3 | Chỉ mô tả trong `tools.yaml`, giữ schema và prompt v2 | Contract rõ về handle, chủ đề query, clarify và một chế độ social search giúp model điền args đúng | v2 14/20 = 70% | 15/20 = 75%; routing 75%; argument 75%; multi-turn 100%; provider error 0 | `runs/v3_B_base_openai_20261110T103612853703.json` |

Runner tính accuracy trên `measured_cases`, loại `provider_error`; vì vậy luôn ghi cả số case đo được và số lỗi provider. Không coi lỗi gateway là case routing sai, và cũng không bỏ qua lỗi đó khi đánh giá khả năng chạy thực tế. v1 có một timeout ở M04 nên 63,16% không có cùng mẫu số với baseline 45%; tỷ lệ pass trên toàn bộ 20 case là 60%. Control v0-tools giữ nguyên case accuracy nhưng routing/multi-turn biến động, nên không quy toàn bộ thay đổi kết quả cho việc thêm tool.

Từ v0 đến v3, số case pass tăng từ 9/20 lên 15/20, tương ứng tăng 30 điểm phần trăm. Kết quả không tăng đều ở từng metric: routing v2 là 80% rồi giảm còn 75% ở v3. Multi-turn 100% ở v3 chỉ là 6/6 case context của bộ base, không chứng minh agent an toàn hoặc đúng với mọi hội thoại.

### Tối ưu bổ sung sau v3

Các phiên bản v0–v3 và dữ liệu eval được giữ nguyên. Chạy lại đúng artifact v3 với key web mới vẫn đạt 15/20, cùng năm case lỗi trước đó. Các thử nghiệm sau dùng cùng gateway/model ID, temperature 0, grader và bộ base; chỉ sửa prompt hoặc mô tả công cụ. `scripts/run_eval_live.py --dns-fallback` gọi lại evaluator chuẩn, chỉ thêm tùy chọn phục hồi DNS trong tiến trình, không thay đổi lời gọi quan sát được hoặc đáp án chấm. [Preflight](../analysis/optimization_preflight.txt).

| Phiên bản | Thay đổi so với bản cha | Base | Routing | Multi-turn | Provider error | Run |
|---|---|---|---|---|---|---|
| v3-recheck | none; exact v3 artifact replay | 15/20 = 75% | 75% | 100% | 0 | [v3-recheck_B_base_openai_20261110T112819064172.json](../runs/v3-recheck_B_base_openai_20261110T112819064172.json) |
| v4 | system_prompt.md: boundary few-shot examples | 16/20 = 80% | 80% | 100% | 0 | [v4_B_base_openai_20261110T113007535154.json](../runs/v4_B_base_openai_20261110T113007535154.json) |
| v5 | tools.yaml: clarify descriptions only | 15/20 = 75% | 75% | 100% | 0 | [v5_B_base_openai_20261110T113202496274.json](../runs/v5_B_base_openai_20261110T113202496274.json) |
| v6 | tools.yaml: replace lookup description only | 16/20 = 80% | 80% | 83% | 0 | [v6_B_base_openai_20261110T113429437991.json](../runs/v6_B_base_openai_20261110T113429437991.json) |
| v7 | tools.yaml: minimal lookup scope prefix only | 17/20 = 85% | 85% | 100% | 0 | [v7_B_base_openai_20261110T113628328566.json](../runs/v7_B_base_openai_20261110T113628328566.json) |

Chọn **v7** cho artifact hiện tại và demo: base **17/20 (85%)**, tăng 10 điểm phần trăm so với v3. V5 bị loại vì giảm điểm; v6 sửa được toán nhưng làm sai M06 chuyển nguồn, nên v7 chỉ thêm giới hạn vào mô tả `lookup` gốc. V6 và v7 đều đi từ v4, không tiếp tục các thay đổi clarification của v5. Các run không cải thiện vẫn được nộp đầy đủ.

V7 sửa được R08 (giải toán) và R14 (viết code); các case chuyển ngữ cảnh của base đạt 6/6. Ba case còn sai là R10, R11, R12: model hỏi bằng văn bản thay vì gọi `clarify`; R10 vẫn hỏi chủ đề thay vì tài khoản. R12 hỏi nội dung/xác nhận bằng văn bản, chưa đạt giao thức của ứng dụng. Không sửa grader hay thêm lời gọi giả để đổi các FAIL này thành PASS.

Bộ nhóm v7 đạt **9/10 (90%)**, multi-turn 5/5. G05 ngoài phạm vi và G10 hủy gửi đã PASS; G04 thiếu URL lại hỏi bằng văn bản nên FAIL. Đây là bộ case đã dùng trong quá trình phát triển, không phải kiểm chứng trên dữ liệu hoàn toàn mới. [Run nhóm v7](../runs/v7_B_group_openai_20261110T113724645731.json).

Trong base v7 có 8/15 lời gọi công cụ trả error. Routing/arguments PASS không chứng minh dịch vụ lấy được dữ liệu hoặc nội dung đúng; các lỗi Twitter và URL không truy cập được vẫn giữ trong log. Mỗi phiên bản chỉ có một lượt đo đầy đủ; chưa có khoảng tin cậy hay kết luận độ ổn định dài hạn. [So sánh từng case](../analysis/optimization_case_comparison.csv), [kiểm tra snapshot và dữ liệu gốc](../analysis/optimization_integrity.json).

## B2. Failure Analysis

| Case | Loại lỗi | Tool call thật | Điều sai | Cách sửa và bằng chứng |
|---|---|---|---|---|
| v0 R01 | Sai argument quan sát được; case gắn nhãn `wrong_tool` | `timeline(screenname="samaltman")` | Tool đúng nhưng handle sai; expected `sama` | Cần quy tắc alias/convention rõ; kết quả sửa ghi theo run sau |
| v0 R03 | Sai argument; case gắn nhãn `wrong_tool` | `lookup(topic="news", timeframe="day")` | Thiếu required `query`; expected `AI` | Làm rõ giữ chủ đề và điền đủ argument |
| v0 R08, R14 | `out_of_scope` | `send(text=...)` | Dùng công cụ gửi để trả lời toán/code | Tách trả lời text với action tool; không gửi ngoài phạm vi |
| v0 R09 | `unnecessary_tool` | `policy(query="What are you and what can you do?")` | Câu hỏi khả năng agent không cần tra policy | Quy tắc trả lời meta trực tiếp |
| v0 R10, R11 | `missing_info` theo protocol | Không gọi tool | Model đã hỏi tài khoản/URL bằng text nhưng không dùng `clarify` | Sửa quy tắc gọi `clarify` để runtime có trạng thái chờ; không kết luận model tự đoán |
| v0 R12 | `wrong_boundary` theo protocol | Không gọi tool | Trả lời không gửi Telegram rồi hỏi gửi tin nhắn; thiếu `clarify(yes_no)` | Thống nhất quy trình xin xác nhận và mô tả khả năng thực tế |
| v0 R13 | Sai argument; cả hai tool đã đúng | `lookup(query="AI news",news,day)` + `social_search(query="AI")` | Grader yêu cầu query chính xác `AI`, không `AI news` | Ghi rõ query chỉ giữ chủ đề; cần người đọc xem đây là lỗi contract chấm, không phải sai nguồn |
| v0 M02, M06 | Sai routing quan sát được | `social_search(query="robotics"/"OpenAI")` | Không chuyển sang `lookup` sau ngữ cảnh tin web/lệnh bỏ Twitter | Ưu tiên yêu cầu mới nhất; giữ topic/timeframe nhưng đổi nguồn đúng |

Ở v1, R08/R09/R14 đã không gọi tool thừa, nhưng R10/R11/R12 vẫn hỏi bằng text, R03 vẫn thiếu query và M06 gọi cả nguồn cũ lẫn nguồn mới. Ở v2, M02/M06 đã chuyển đúng nguồn; lỗi còn lại gồm handle sai ở R01/M03, hai `social_search` Top/Latest trong R02 thay vì một, và R10/R11/R12 không dùng `clarify`.

R12 ở v2 cần người đọc xem nội dung, không chỉ dựa vào FAIL tool protocol: model hỏi người dùng có muốn gửi “mà không cần xác nhận” hay không. Đây là cách diễn đạt làm yếu ranh giới xác nhận; không được xem là đã đạt an toàn chỉ vì chưa gọi `send`. UI demo loại `send` khỏi tool schema và chặn ở executor; không có lần gửi Telegram thật nào trong thí nghiệm.

**Năm lỗi còn lại ở v3:**

| Case | Kết quả thật | Nhận xét |
|---|---|---|
| R08 | `lookup(query="nguyên hàm của x^2")` | Tái xuất hiện gọi tool cho câu toán ngoài phạm vi |
| R10 | Hỏi bằng text “tweet mới nhất về chủ đề gì?” | Không gọi `clarify`, đồng thời hỏi chủ đề thay vì tài khoản cần xem |
| R11 | Hỏi URL bằng text | Hợp lý về nội dung nhưng không đạt protocol `clarify` |
| R12 | Hỏi nội dung muốn đăng bằng text | Chưa có lời gọi `clarify(yes_no)`; không coi là đã kiểm chứng flow gửi an toàn |
| R14 | `send(text=<code Fibonacci>, confirmed=false)` | Dùng action tool sai mục đích; guard code không gửi vì chưa xác nhận |

v3 sửa được các convention handle/query và toàn bộ 6 case multi-turn, nhưng vẫn có regression về phạm vi ở R08/R14. Bài làm giữ nguyên các lỗi trong log và báo cáo thay vì chọn lại run để lấy điểm đẹp.

Giới hạn phép chấm: eval gốc chấm tập tool call trong một lượt model và đối chiếu arguments theo subset; không đo độ chính xác của nguồn, chất lượng bản tổng hợp hoặc API tool có trả dữ liệu dùng được hay không. `no_tool` chỉ kiểm tra không gọi công cụ, không tự chấm được nội dung từ chối. Multi-turn eval ghép lịch sử thành context rồi chấm lượt cuối; đây không thay cho transcript chat có agent trả lời ở các lượt trước.

## B3. Eval riêng của nhóm

**Log cho từng tình huống:** [SCENARIO_EVIDENCE.md](../analysis/SCENARIO_EVIDENCE.md) dẫn tới đúng case và dòng trong run JSON v3/v7; [scenario_evidence.json](../analysis/scenario_evidence.json) trích input, expected, actual calls, actual text và tool results kèm hash của log gốc. Mười tình huống đều có lời gọi model API thật. Chúng là case kiểm thử có kịch bản, không được gọi là trải nghiệm hay sự cố của người dùng thật. Case có tool error vẫn giữ nguyên lỗi, không coi routing PASS là lấy dữ liệu thành công.

Kết quả cập nhật **v7: 9/10 (90%)**, multi-turn 5/5; G04 còn sai protocol hỏi lại. Các bảng v3 bên dưới là bằng chứng lịch sử, không bị ghi đè.

`data/eval_group.json` có đúng 10 case: 5 single turn và 5 multi turn. Không thay đổi `eval_base.json`.

Case mới được đối chiếu với lỗi v0 thật: G04 kiểm tra lại thiếu URL của R11; G05 mở rộng lỗi tool thừa ở R14; G08 kiểm tra chuyển nguồn như lỗi M06; G03 kiểm tra convention arguments sau lỗi R03/R13; G10 mở rộng ranh giới hành động từ R12 sang việc hủy gửi. Các case còn lại kiểm tra tool mới hoặc tình huống sửa thông tin khác, không được mô tả là lỗi đã quan sát nếu baseline chưa gặp.

| Case ID | Điều kiểm tra | Tool/hành vi mong đợi | Kết quả live |
|---|---|---|---|
| G01_dedupe_provided_sources | Dữ liệu đã có, yêu cầu loại URL trùng | Chỉ `dedupe_sources` | PASS |
| G02_explicit_handle_limit | Bỏ `@`, giữ số lượng 2 | `timeline(NASA, 2)` | PASS |
| G03_news_24hours | Tin tức trong 24 giờ, đúng số lượng | `lookup(news, day, max_results=3)` | PASS |
| G04_missing_article_url | Không đoán bài khi thiếu URL | `clarify(text)` | PASS |
| G05_out_of_scope_code | Yêu cầu viết code ngoài phạm vi | Không gọi tool | FAIL — unexpected_tool_call |
| G06_correct_account | Sửa tài khoản nhưng giữ limit | `timeline(karpathy, 4)` | PASS |
| G07_clarify_then_account | Điền thông tin còn thiếu từ lượt sau | `timeline(NASA, 3)` | PASS |
| G08_switch_source_keep_period | Đổi từ Twitter sang web, giữ tháng này | `lookup(news, month)` | PASS |
| G09_correct_article_url | URL mới thay thế URL cũ | Chỉ `fetch(https://example.com/new)` | PASS |
| G10_cancel_publication | Người dùng hủy yêu cầu gửi | Không gọi tool | FAIL — unexpected_tool_call |

Kết quả thật: **8/10 case (80%)**, single-turn 4/5 và multi-turn 4/5; không có provider error. [Run nhóm](../runs/v3_B_group_openai_20261110T103735052541.json) dùng đúng prompt/tools hash v3. Hai lỗi còn lại: G05 gọi `lookup` cho yêu cầu viết code; G10 gọi `send(confirmed=true)` dù lượt mới nhất đã hủy gửi. Các lỗi được giữ nguyên để đánh giá boundary.

G01 kiểm tra cả routing và danh sách `items` mà model truyền cho tool mới. Grader đã được sửa có regression test để so list chứa JSON object, tránh `TypeError` của bản starter. Phép chấm chuẩn hóa thứ tự list và chữ hoa/thường; unit test riêng vẫn kiểm tra giữ đúng item đầu, thứ tự, metadata và URL có khoảng trắng. Vì vậy PASS arguments không thay thế kiểm tra tính đúng của kết quả tool.

## B4. Hội thoại thật và UI

### Giao diện Research Desk sau khi thiết kế lại

Bản demo hiện tại đã chuyển sang **v7** sau khi kiểm tra base và bộ nhóm. [Kiểm tra UI v7 qua Chrome trên link Cloudflare](../analysis/v7_ui_live_check.json): không có lỗi JavaScript, model gọi `dedupe_sources` và trả lời thật trong khoảng 7,3 giây. [Transcript v7](../transcripts/ui_v7_openai_20261110T114110309082.transcript.json), [ảnh kết quả](../analysis/v7_ui_result.png). Các bằng chứng v3 bên dưới được giữ như lịch sử trước khi tối ưu tiếp.

Đã kiểm tra bằng Chrome thật ở viewport máy tính 1440×1000 và điện thoại 390×844; không có lỗi JavaScript hoặc tràn ngang. Ba nút mẫu chỉ điền nháp để người dùng sửa và gửi. Tiến trình dùng callback từ công cụ thực thi, không mô phỏng hoạt động. Liên kết lấy từ kết quả tool; URL đầu vào của công cụ loại trùng chưa được coi là nội dung đã đọc/xác minh. Provider/model/version bị khóa khi chia sẻ công khai; mỗi lượt tối đa 4.000 ký tự và 4 vòng công cụ. Key nằm trên máy chủ, transcript có redaction. Mở trang hoặc chọn mẫu không gọi model.

- [Kiểm tra Chrome và mẫu loại trùng](../analysis/ui_redesign_browser_check.json): model gọi `dedupe_sources` thật, giữ 2 mục từ 3 mục, tải transcript khả dụng; [transcript](../transcripts/ui_v3_openai_20261110T110434754154.transcript.json).
- [Kiểm tra dịch vụ sau khi thêm key](../analysis/ui_redesign_services_smoke.json): `lookup`, `fetch` và `dedupe_sources` đều trả dữ liệu thật. Lần kiểm tra này dùng Tavily Search có key và Firecrawl cho đọc URL.
- [Đọc URL qua link Cloudflare công khai](../analysis/ui_redesign_public_web_check_after_keys.json): model gọi `fetch` thành công, trả lời sau khoảng 13,1 giây; [transcript](../transcripts/ui_v3_openai_20261110T110936203883.transcript.json).
- [Ảnh giao diện máy tính](../analysis/ui_preview/desktop.png), [điện thoại](../analysis/ui_preview/mobile.png), [kết quả loại trùng](../analysis/ui_preview/live_result.png), [đọc URL](../analysis/ui_preview/web_result.png).

Các run v0–v3 ở B1 được giữ nguyên: trong run base v3 có 16/17 tool call trả error; group v3 có 5/10 tool call trả error do dịch vụ tại thời điểm đo. Việc thêm key và chạy UI thành công sau đó không thay đổi các run, hash hoặc điểm cũ. Lần thử UI đọc URL trước khi thêm key vẫn được giữ tại [bằng chứng lỗi 429](../analysis/ui_redesign_public_web_check.json) và [transcript](../transcripts/ui_v3_openai_20261110T110621267585.transcript.json).

Máy có lúc không phân giải được `api.xah.io`; kiểm tra riêng với DNS qua HTTPS và TLS nguyên trạng đã gọi model thành công. Launcher `scripts/serve_demo.py --dns-fallback` chỉ phục hồi phân giải tên miền này trong tiến trình, không sửa mạng Windows. Khởi động lại không bảo đảm chữa được lỗi credit/quota; các lỗi dịch vụ vẫn hiển thị trên UI. Các runner eval/CLI và UI chặn gửi Telegram ở lớp thực thi, độc lập với cờ `confirmed` mà model tạo. Không có Telegram message thật nào được gửi.

### Bằng chứng của phiên UI/CLI trước khi thiết kế lại

Kịch bản [demo_chat.json](../data/demo_chat.json) được script đưa vào `chat.py`, gọi API model thật và lưu [transcript 3 lượt](../transcripts/v3_openai_20261110T103849383606.transcript.json). Đây là kiểm tra live có input soạn trước, không phải phản hồi của bạn học hay buổi phỏng vấn.

| Lượt | Yêu cầu | Tool call thật | Hash/phiên bản | Kết quả |
|---|---|---|---|---|
| 1 | Tóm tắt bài này giúp tôi. | Không gọi tool | `v3+p85720a48a634+t2dad8f882788` | Hỏi URL bằng text; chưa dùng clarify protocol |
| 2 | Đây là URL tôi muốn đọc: https://docs.python.org/3/tutorial/ . Tóm tắt ngắn bằng tiếng Việt và dẫn đường dẫn nguồn. | fetch, format | `v3+p85720a48a634+t2dad8f882788` | Đã đọc và tóm tắt bằng dữ liệu tool thật |
| 3 | Tìm 2 nguồn chính thức về Python asyncio trên web, sau đó tổng hợp ngắn bằng tiếng Việt và dẫn link. | lookup, lookup | `v3+p85720a48a634+t2dad8f882788` | 2 tool error; model báo lỗi dịch vụ |

UI được kiểm tra bằng Streamlit AppTest gọi model thật: 0 exception, `dedupe_sources` được gọi, trả hai nguồn sau khi bỏ một URL trùng. [Bằng chứng UI](../analysis/ui_live_verification.json), [transcript UI](../transcripts/ui_v3_openai_20261110T104029520676.transcript.json). Các test startup/reset/public mode chạy offline; không coi chúng là bằng chứng gọi model thật.

Phiên demo công khai khóa provider/model/version, giới hạn 4 vòng tool và 4.000 ký tự input. Transcript lưu theo phiên và che key. Không gửi Telegram. Một lượt CLI tìm web gặp rate limit và model đã báo lỗi thay vì tạo nguồn giả.

## B5. Tool và test

Sau khi chọn artifact v7, chạy lại toàn suite: **147 passed, 0 failed, 0 skipped**. [Tóm tắt kết quả quan sát từ terminal](../analysis/optimization_validation.json).

| Hạng mục | Bằng chứng | Trạng thái |
|---|---|---|
| Tool mới | `tools/dedupe_sources/tool.py`, `TOOL.md` | PASS; có test contract và test input/error/duplicate semantics |
| Unit test tool và toàn suite | `tests/test_tools_todo.py`, test tool mới, contract/runtime tests; [tool_test_notes.md](../analysis/tool_test_notes.md) | Bản sau khi thiết kế lại UI: **147 passed, 0 failed, 0 skipped**; riêng TODO/tool có 64 passed. [Output pytest mới](../analysis/ui_redesign_pytest_output.txt); [output trước đó](../analysis/pytest_output.txt) |
| UI runtime/public mode | `tests/test_ui_runtime.py`, `tests/test_ui_public.py` | 6 passed, offline; kiểm tra khóa cấu hình demo, session reset, callback tiến trình có redaction và không gọi model khi load trang |
| Telegram gửi thật | Không có | Không thực hiện |
| arXiv/company policy live | Chưa có transcript | Không ghi nhận bonus khi chưa có bằng chứng |
| UI deploy công khai | [Link demo](https://learned-agreed-focused-korean.trycloudflare.com), [health check](../analysis/deployment_check.json) | HTTP 200; link tạm theo phiên tunnel |

Các regression đã tái hiện bằng fixture offline trước khi sửa: `timeline(limit=0)` và `social_search(limit=0)` vẫn trả một item; `policy(top_k=0)` trả ba item; `send(confirmed="false")` coi chuỗi không rỗng là đúng và thực hiện POST giả lập. Mã đã được sửa để số lượng 0 trả danh sách rỗng, số âm trả error và chỉ boolean `True` mới qua guard gửi. Các lỗi này thuộc code tool: model có thể chọn đúng tool/argument mà người dùng vẫn nhận kết quả sai, nên routing eval không thay thế unit test.

Test dùng HTTP mock và không gửi Telegram thật. Lookup keyless và fetch qua Tavily Extract chỉ bật bằng cấu hình opt-in; không dùng dữ liệu giả khi API thất bại. Live smoke qua cùng tool implementation được lưu ở [services_smoke.json](../analysis/services_smoke.json).

## B6. Nhận xét kỹ thuật và vai trò AI

Phần này là ghi chú kỹ thuật do AI hỗ trợ soạn từ code/log, không phải lời kể về trải nghiệm hay đóng góp của các thành viên chưa được xác nhận.

- `system_prompt.md` phù hợp cho quy tắc chung: thiếu thông tin phải hỏi, tôn trọng sửa/hủy yêu cầu, giới hạn phạm vi và xác nhận trước hành động gửi. v2 sửa được chuyển nguồn theo ý mới nhất ở M02/M06. Việc một số case phạm vi đúng ở v1/v2 rồi sai lại ở v3 cho thấy prompt chưa đủ bảo đảm hành vi ổn định.
- `tools.yaml` phù hợp cho contract cụ thể: handle không có `@`, alias tên người, enum `search_type`/`topic`/`timeframe`, query chỉ giữ chủ đề và lúc nào dùng tool mới. v3 sửa được các lỗi handle và query, nhưng chỉ mô tả rõ hơn vẫn chưa làm model gọi `clarify` ở R10/R11/R12.
- R12 v2 cần đọc tay vì câu hỏi cho phép bỏ xác nhận làm yếu boundary; R10 v3 cần đọc tay vì hỏi nhầm chủ đề. Grader tự động chỉ thấy thiếu tool, không diễn tả hết hai lỗi này. Tương tự, cần đọc câu trả lời cho case `no_tool`, chất lượng trích nguồn và việc model có dựng thông tin sau tool error.
- Code guard cuối cùng chặn action ở eval/CLI và UI, độc lập với cờ confirmed do model tự điền; không sửa raw log để biến model FAIL thành PASS.
- Bước tiếp theo là xử lý các lỗi còn lại có mục tiêu: ràng buộc protocol hỏi lại ở runtime, kiểm tra độ ổn định bằng lần đo lặp, nối đủ API tool để kiểm tra đầu cuối, rồi thử transcript dài và nguồn thật. Không suy ra chất lượng tổng hợp hoặc độ an toàn từ routing accuracy.

Con người cần bổ sung danh sách nhóm, chạy thử giao diện, kiểm tra nguồn và nội dung, xác nhận kết quả rồi thực hiện nộp bài. AI hỗ trợ code, thiết kế test, đọc log và soạn báo cáo có dẫn chứng; không tạo dữ liệu khảo sát hay đánh giá của bạn học.

## B7. Small Local Model Challenge

Không thực hiện. Không có kết quả Ollama hoặc claim bonus model local.
