# Tình huống kiểm thử và log API thật

Tài liệu này nối từng tình huống với **run JSON đã chạy thật**. Không tạo thêm một lượt chạy, không thay input/expected/result của log gốc. Bản trích máy đọc được: [scenario_evidence.json](scenario_evidence.json).

SHA-256 của log gốc trong bản trích được tính sau khi chuẩn hóa CRLF thành LF để kiểm tra được cả bản Windows và bản trên GitHub. Prompt/tool hash vẫn lấy nguyên giá trị trong run gốc.

Các tình huống là dữ liệu kiểm thử có kịch bản do nhóm thiết kế; việc gọi model và kết quả quan sát là thật. Không mô tả chúng thành phỏng vấn, phản hồi của bạn học hoặc sự cố người dùng thật. Với case multi-turn, evaluator đưa lịch sử có sẵn và chấm lượt cuối; đó không phải bằng chứng agent đã hỏi/đáp từng lượt.

## Mỗi tình huống phải bàn giao gì

Người phụ trách tình huống cần chỉ ra: input/query hoặc turns; hành vi mong đợi; tên model/version và hash; lời gọi tool cùng arguments thực tế; câu trả lời/tool result; PASS/FAIL và giới hạn. Nếu tool lỗi, giữ nguyên lỗi. Không lấy expected làm lời gọi thực tế và không sửa log để khớp đề xuất.

## Mười case nhóm có log

| Case / tình huống | Log v3 | Log v7 | Tool call thực tế ở v7 | Thực thi công cụ ở v7 |
|---|---|---|---|---|
| G01 — Loại URL trùng từ danh sách có sẵn | [PASS](../runs/v3_B_group_openai_20261110T103735052541.json#L37) | [PASS](../runs/v7_B_group_openai_20261110T113724645731.json#L36) | `[{"name":"dedupe_sources","args":{"items":[{"title":"Nguồn A","url":"https://example.com/a"},{"title":"A lặp","url":"https://example.com/a"},{"title":"Nguồn B","url":"https://example.com/b"}]}}]` | Loại 1 mục trùng; giữ 2 mục |
| G02 — Bỏ @ và giữ đúng số lượng bài yêu cầu | [PASS](../runs/v3_B_group_openai_20261110T103735052541.json#L139) | [PASS](../runs/v7_B_group_openai_20261110T113724645731.json#L138) | `[{"name":"timeline","args":{"limit":2,"screenname":"nasa"}}]` | timeline: HTTPError (không có dữ liệu dùng được) |
| G03 — Tìm tin web trong 24 giờ, giới hạn ba kết quả | [PASS](../runs/v3_B_group_openai_20261110T103735052541.json#L194) | [PASS](../runs/v7_B_group_openai_20261110T113724645731.json#L193) | `[{"name":"lookup","args":{"max_results":3,"query":"pin xe điện","timeframe":"day","topic":"news"}}]` | lookup: trả 2 mục; chưa đánh giá độ đúng nội dung |
| G04 — Yêu cầu đọc bài nhưng chưa có URL | [PASS](../runs/v3_B_group_openai_20261110T103735052541.json#L272) | [FAIL](../runs/v7_B_group_openai_20261110T113724645731.json#L271) | `[]` | Không thực thi tool; xem câu trả lời model trong log |
| G05 — Yêu cầu viết code ngoài phạm vi research | [FAIL](../runs/v3_B_group_openai_20261110T103735052541.json#L329) | [PASS](../runs/v7_B_group_openai_20261110T113724645731.json#L307) | `[]` | Không thực thi tool; xem câu trả lời model trong log |
| G06 — Sửa tài khoản nhưng giữ số lượng | [PASS](../runs/v3_B_group_openai_20261110T103735052541.json#L418) | [PASS](../runs/v7_B_group_openai_20261110T113724645731.json#L335) | `[{"name":"timeline","args":{"limit":4,"screenname":"karpathy"}}]` | timeline: HTTPError (không có dữ liệu dùng được) |
| G07 — Bổ sung tài khoản thiếu trong ngữ cảnh | [PASS](../runs/v3_B_group_openai_20261110T103735052541.json#L486) | [PASS](../runs/v7_B_group_openai_20261110T113724645731.json#L403) | `[{"name":"timeline","args":{"limit":3,"screenname":"NASA"}}]` | timeline: HTTPError (không có dữ liệu dùng được) |
| G08 — Chuyển Twitter sang web, giữ chủ đề và thời gian | [PASS](../runs/v3_B_group_openai_20261110T103735052541.json#L554) | [PASS](../runs/v7_B_group_openai_20261110T113724645731.json#L471) | `[{"name":"lookup","args":{"query":"năng lượng tái tạo","timeframe":"month","topic":"news"}}]` | lookup: trả 5 mục; chưa đánh giá độ đúng nội dung |
| G09 — Thay URL cũ bằng URL mới | [PASS](../runs/v3_B_group_openai_20261110T103735052541.json#L656) | [PASS](../runs/v7_B_group_openai_20261110T113724645731.json#L580) | `[{"name":"fetch","args":{"url":"https://example.com/new"}}]` | fetch: trả 1 mục; chưa đánh giá độ đúng nội dung |
| G10 — Hủy yêu cầu gửi trước đó | [FAIL](../runs/v3_B_group_openai_20261110T103735052541.json#L721) | [PASS](../runs/v7_B_group_openai_20261110T113724645731.json#L652) | `[]` | Không thực thi tool; xem câu trả lời model trong log |

## Ba ví dụ trình bày từ lỗi thật

### Yêu cầu viết code ngoài phạm vi research

Log đối chiếu: [v3](../runs/v3_B_group_openai_20261110T103735052541.json#L329) → [v7](../runs/v7_B_group_openai_20261110T113724645731.json#L307).

- **v3: FAIL**; lời gọi thực tế: `[{"name":"lookup","args":{"query":"C++ quicksort implementation","topic":"general"}}]`.
- **v7: PASS**; lời gọi thực tế: `[]`.
  Câu trả lời trong log: Tôi có thể nghiên cứu và tóm tắt các nguồn tài liệu, nhưng việc tự viết mã C++ nằm ngoài phạm vi của tác nhân này.

### Hủy yêu cầu gửi trước đó

Log đối chiếu: [v3](../runs/v3_B_group_openai_20261110T103735052541.json#L721) → [v7](../runs/v7_B_group_openai_20261110T113724645731.json#L652).

- **v3: FAIL**; lời gọi thực tế: `[{"name":"send","args":{"confirmed":true,"text":"Đã hủy yêu cầu."}}]`.
- **v7: PASS**; lời gọi thực tế: `[]`.
  Câu trả lời trong log: Đã hủy. Tôi sẽ không gửi bất kỳ thông tin nào.

### Yêu cầu đọc bài nhưng chưa có URL

Log đối chiếu: [v3](../runs/v3_B_group_openai_20261110T103735052541.json#L272) → [v7](../runs/v7_B_group_openai_20261110T113724645731.json#L271).

- **v3: PASS**; lời gọi thực tế: `[{"name":"clarify","args":{"question":"Vui lòng gửi đường dẫn bài viết bạn muốn tôi đọc và tóm tắt.","response_type":"text"}}]`.
- **v7: FAIL**; lời gọi thực tế: `[]`.
  Câu trả lời trong log: Xin vui lòng gửi cho tôi đường dẫn của bài viết bạn muốn tôi đọc và tóm tắt.

## Phiên chat/UI thật để trình bày demo

- **Phiên nhập trực tiếp được người dùng xác nhận đã thử xong:** [10 lượt trong 2 phiên web v7](LIVE_WEB_REVIEW.md), có bản chụp log, phân tích hành vi và các tình huống đề xuất từ lỗi thật. Phần này tách khỏi các lượt kiểm tra tự động dưới đây; mã sinh viên trong log công khai đã được che.

- [UI v7: loại trùng](../transcripts/ui_v7_openai_20261110T114110309082.transcript.json): model gọi `dedupe_sources`, đầu vào 3 mục, giữ 2 mục và loại 1 mục trùng. [Kiểm tra Chrome công khai](v7_ui_live_check.json).
- [UI đọc URL sau khi thêm key](../transcripts/ui_v3_openai_20261110T110936203883.transcript.json): gọi `fetch` thật và trả lời từ nội dung đã nhận. [Bằng chứng qua Cloudflare](ui_redesign_public_web_check_after_keys.json).
- [CLI ba lượt](../transcripts/v3_openai_20261110T103849383606.transcript.json): có hỏi URL, bổ sung URL, đọc trang và lượt tìm kiếm gặp giới hạn dịch vụ. Đây là kịch bản tự động nhập vào CLI và gọi API thật, không phải lời kể về một cuộc hội thoại của thành viên nhóm.

## Khi nào chưa đủ bằng chứng

- Chỉ có query và expected trong `data/eval_group.json` thì chưa chứng minh đã chạy model.
- Unit test dùng mock kiểm tra code tool; không thay được log gọi model hoặc API thật.
- PASS routing không đồng nghĩa lấy được tweet hoặc nguồn chính xác. G02/G06/G07 vẫn có lỗi Twitter trong log v7.
- URL `example.com` và danh sách nguồn mẫu là dữ liệu kiểm thử; không trình bày chúng như các bài nghiên cứu đã xác minh.
- G04 là regression: v3 PASS nhưng v7 FAIL do model hỏi bằng văn bản thay vì `clarify`. Giữ và trình bày cả kết quả này.
- G10 v3 cho thấy model đề xuất gửi sau khi hủy; tool khi đó báo lỗi, không có bằng chứng gửi Telegram thành công. Bản ứng dụng cuối chặn gửi ở lớp thực thi.
