# Kiểm tra trước khi nộp Day03

## Các phần đã có bằng chứng

- [x] Provider thật và preflight: `analysis/optimization_preflight.txt`.
- [x] Baseline v0 và ba vòng v1–v3, có run JSON và version log.
- [x] Tối ưu bổ sung v4–v7; giữ cả các thử nghiệm không cải thiện. Bản chọn hiện tại: **v7**, base **17/20 (85%)**, nhóm **9/10 (90%)**.
- [x] Bộ base giữ nguyên; không thay grader trong lần tối ưu bổ sung. Xem `analysis/optimization_integrity.json`.
- [x] Tool mới `dedupe_sources`, có implementation, TOOL.md, đăng ký, declaration và nhiều hơn ba unit test.
- [x] Team eval đủ 10 case: 5 single-turn, 5 multi-turn.
- [x] Unit/contract/runtime test: **147 passed, 0 failed, 0 skipped** sau khi chọn v7.
- [x] Hội thoại CLI ít nhất ba lượt gọi model thật, có transcript.
- [x] Streamlit UI, link Cloudflare, đọc URL thật và tải transcript. Xem `DEMO_GUIDE.md`.
- [x] REPORT phần A/B, failure analysis, reflection kỹ thuật và giới hạn có dẫn chứng.
- [x] API key nằm trong `.env` được ignore; không đưa vào bài nộp.

## Các việc cần con người chốt

- [ ] Điền tên nhóm, tên/MSSV của hai thành viên còn lại trong `artifacts/REPORT.md`.
- [ ] Các thành viên tự thử UI, mở nguồn kiểm tra nội dung, đọc báo cáo và chuẩn bị trình bày vai trò thực tế của mình.
- [ ] Giữ máy và Cloudflare Tunnel hoạt động khi demo; cập nhật link nếu khởi động tunnel mới.
- [ ] Nộp `starter_v0/` hoặc link repository theo hướng dẫn của lớp, kiểm tra trạng thái nộp trên LMS.

## Giới hạn còn tồn tại

- Model vẫn có thể hỏi thiếu URL/tài khoản hoặc xin xác nhận bằng văn bản thay vì tool `clarify`. Base v7 còn ba case FAIL, nhóm còn G04 FAIL; không đổi các lời hỏi thành tool call giả để tăng điểm.
- Twitter/X chưa kết nối ổn định. Nếu demo chức năng này, cần tài khoản RapidAPI có quyền/quota Twitter API45 và kiểm tra dữ liệu thật; không tự coi key đã điền là kết nối thành công.
- Routing accuracy chỉ đo chọn tool và arguments. Nó không đo độ đúng nội dung, độ tin cậy của nguồn hay tỷ lệ API trả dữ liệu. Các lỗi dịch vụ còn trong run JSON.
- Chưa có phép đo lặp và bộ kiểm chứng độc lập; không coi một run 85%/90% là cam kết chất lượng cho mọi yêu cầu.

README không đặt ngưỡng bắt buộc 100% accuracy. Telegram gửi thật, Small Local Model Challenge, poster HTML/SVG và điều kiện UI + hơn ba tool mới là các phần bonus; chưa được thực hiện đủ để nhận các bonus đó.
