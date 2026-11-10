# Demo Research Desk cho nhóm khác

## Mở và dùng thử

Link của phiên hiện tại: <https://learned-agreed-focused-korean.trycloudflare.com>.

Giao diện có ba mẫu: **Tìm nguồn**, **Đọc một URL**, **Loại nguồn trùng**. Chọn mẫu chỉ điền nội dung vào ô chat, chưa gọi API. Có thể sửa yêu cầu rồi bấm nút gửi. Khi agent hỏi lại, trả lời trong cùng ô chat để giữ ngữ cảnh.

Trong lúc xử lý, giao diện hiện tên công cụ đang chạy. Sau khi có câu trả lời, có thể mở **Liên kết từ kết quả công cụ** và **Nhật ký công cụ · dữ liệu chi tiết**. Nút **Tải transcript JSON** nằm ở thanh bên sau lượt đầu tiên. Trên điện thoại, mở thanh bên bằng nút ở góc trên trái.

## Kịch bản trình bày khoảng 3 phút

1. Giới thiệu: agent tìm tài liệu, đọc URL và sắp xếp nguồn. Người dùng kiểm tra nguồn và quyết định dùng kết quả.
2. Chọn **Dùng mẫu loại nguồn trùng**, xem nội dung rồi gửi. Đầu vào có 3 mục, 1 URL lặp; công cụ giữ 2 mục. Mở nhật ký để xem lời gọi và kết quả thực tế. Đây là xử lý URL, không phải xác minh nội dung trang.
3. Bắt đầu phiên mới sau khi tải transcript nếu cần. Nhập “Tóm tắt bài này giúp tôi”, rồi cung cấp `https://docs.python.org/3/tutorial/` khi agent hỏi URL. Luồng này minh họa giữ ngữ cảnh và đọc nguồn thật. Nếu model hỏi bằng văn bản thay vì tool `clarify`, nhật ký sẽ phản ánh đúng hành vi đó.
4. Mở các liên kết nguồn, kiểm tra phần tóm tắt và tải transcript. Có thể cho nhóm khác sửa mẫu tìm nguồn để thử một chủ đề riêng.

Web phụ thuộc quota và tình trạng dịch vụ; X/Twitter chưa kết nối ổn định. Nếu công cụ lỗi, trình bày lỗi thật và giới hạn đang có. Không dùng bản trả lời cũ để giả kết quả của lượt vừa chạy. Demo không gửi Telegram.

## Khởi động lại trên Windows

Chạy các lệnh trong `starter_v0`, sau khi cài thư viện và điền `.env` theo [RUN_GUIDE.md](RUN_GUIDE.md).

Terminal thứ nhất:

```powershell
.\.venv\Scripts\python.exe scripts/serve_demo.py
```

Nếu máy báo lỗi DNS cho `api.xah.io`, dùng thay thế:

```powershell
.\.venv\Scripts\python.exe scripts/serve_demo.py --dns-fallback
```

Tùy chọn này chỉ áp dụng trong tiến trình demo: ưu tiên DNS hệ thống, rồi dùng DNS qua HTTPS khi không phân giải được đúng tên miền gateway. Không sửa DNS Windows hoặc file hosts; hostname và kiểm tra chứng chỉ TLS giữ nguyên. Endpoint được đối chiếu với [hướng dẫn CKEY](https://ckey.vn/vi/llm-api/setup). Tùy chọn không khắc phục key sai, hết credit hoặc lỗi dịch vụ.

Terminal thứ hai:

```powershell
cloudflared tunnel --url http://127.0.0.1:8501
```

Mở link HTTPS mà terminal in ra và thử một yêu cầu. Mỗi lần mở tunnel mới có thể có URL mới: cập nhật link trong `artifacts/REPORT.md` và tài liệu này. Giữ cả hai tiến trình chạy trong buổi demo. Link tạm ngừng hoạt động khi tắt máy hoặc dừng tunnel.

Các lần mở trang, chọn mẫu và bắt đầu phiên mới không gọi model. Gửi chat mới phát sinh lời gọi API. Cấu hình model được khóa trong chế độ demo công khai; key chỉ được đọc trên máy chủ.
