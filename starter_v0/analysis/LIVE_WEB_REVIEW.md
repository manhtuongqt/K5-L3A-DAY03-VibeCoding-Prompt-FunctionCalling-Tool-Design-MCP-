# Phiên thử trực tiếp trên web - v7

## Phạm vi bằng chứng

Người dùng thông báo nhập câu hỏi trực tiếp trên web và xác nhận đã thử xong. Máy chủ ghi nhận **2 phiên UI, tổng cộng 10 lượt** trong ngày 10/11/2026, khoảng 12:26–12:33 theo giờ Việt Nam. Không suy ra đây là hai người độc lập; log không xác minh danh tính, mức hài lòng hoặc chất lượng sử dụng lâu dài.

- **S1:** [bản chụp 4 lượt](../transcripts/live_web_v7_20261110_122635_122911.snapshot.json), từ phiên `ui_v7_openai_20261110T114528950323`.
- **S2:** [bản chụp 6 lượt](../transcripts/live_web_v7_20261110_123044_123347.snapshot.json), từ phiên `ui_v7_openai_20261110T123020243504`.
- [Tóm tắt máy đọc được và hash của bản chụp](live_web_v7_review.json).

Hai phiên dùng `v7+p2d0663692961+ta78aedb0119c`, adapter `openai`, model ID `gemini-2.5-flash-lite` qua cấu hình gateway CKEY của bài. Đây là thông tin model ID cấu hình, không phải xác minh độc lập backend bên trong gateway.

Bản công khai thay hai mã sinh viên bằng `[STUDENT_ID_01]` và `[STUDENT_ID_02]` nhất quán trong câu hỏi, arguments, câu trả lời và tool results. Ngoài việc che thông tin định danh/khóa bí mật, không thay nội dung các lượt hoặc thêm lời gọi tool. Hai file gốc trên máy chủ được giữ nguyên. Không sửa prompt, tool declaration hay code trong lúc ghi nhận hai phiên này.

## Kết quả quan sát

Log có **10 lượt mang trạng thái `answered`, 5 lời gọi tool thật, 1 tool error**. Thời gian từng lượt khoảng 2,05–9,80 giây. Trạng thái `answered` chỉ có nghĩa model đã trả văn bản, không phải người dùng đã nhận đúng kết quả. Không tính accuracy mới từ bảng nhận xét thủ công này.

| Lượt / vị trí trong snapshot | Câu hỏi | Hành vi thật | Nhận xét từ log |
|---|---|---|---|
| S1-T1 `/turns/0` | “giá vàng hôm nay” | `lookup(query="giá vàng hôm nay", topic="news")`; không truyền `timeframe`; tool dùng mặc định `week`, trả 5 nguồn, không báo error; 9,688 giây | Câu trả lời gọi thông tin 8/11 là “hôm nay” rồi trộn nguồn khác ngày. Chưa đáp ứng rõ mốc thời gian của ngày thử. Không kiểm chứng độc lập các mức giá trong bản review này. |
| S1-T2 `/turns/1` | “bạn có thể trả lời đến đâu” | Không gọi tool; trả lời trong phạm vi giá vàng; 2,250 giây | Có giữ ngữ cảnh câu trước. Câu hỏi còn mơ hồ nên không mặc định đây là lỗi; chưa có phản hồi người dùng về việc có cần giới thiệu toàn bộ agent hay không. |
| S1-T3 `/turns/2` | “UI của bạn build bởi đâu” | Không gọi tool; trả lời “Tôi là một mô hình ngôn ngữ lớn, được đào tạo bởi Google.”; 2,656 giây | Chuyển sang danh tính model, chưa trả lời về giao diện. Mã ứng dụng dùng Streamlit: xem [app.py](../app.py). |
| S1-T4 `/turns/3` | “API lấy ở đâu” | Không gọi tool; trả lời “Tôi được xây dựng dựa trên các API của Google.”; 2,047 giây | Chưa có cơ sở cho khẳng định này về ứng dụng. Tài liệu triển khai ghi gateway CKEY/OpenAI-compatible: xem [RUN_GUIDE](../RUN_GUIDE.md). Không suy ra hãng backend chỉ từ model ID. |
| S2-T1 `/turns/0` | “chào bạn, liệt kê top 10 phim marvel gần đây” | `lookup(query="top 10 marvel movies", topic="general", max_results=10)`, trả 10 nguồn; 9,796 giây | Query bỏ điều kiện “gần đây”. Danh sách trả lời chứa phim được ghi năm 2008. Cần làm rõ khoảng thời gian hoặc giữ ràng buộc mới nhất; chưa đánh giá đúng/sai từng thông tin phim. |
| S2-T2 `/turns/1` | “bạn biết gì về cap america” | `lookup(query="Captain America", max_results=5)`, trả 5 nguồn; 9,360 giây | Có tìm kiếm thực và trả lời theo chủ đề. Độ đúng từng chi tiết nhân vật chưa được kiểm chứng độc lập trong lần review log. |
| S2-T3 `/turns/2` | “captain america tim huyết thanh vào ngày nào? thời gian là mấy giờ?” | Văn bản trả về là `tool_code` cùng `print(default_api.lookup(...))`; `tool_events=[]`; 2,328 giây | **Không có tool call được thực thi.** Không được trình bày đoạn mã này như một lần tìm kiếm. Người dùng chưa nhận được câu trả lời có nguồn cho ngày/giờ. |
| S2-T4 `/turns/3` | Một mã sinh viên đứng riêng, đã che thành `[STUDENT_ID_01]` | Gọi `paper_text(arxiv_url="[STUDENT_ID_01]")`, nhận `ValueError`; 4,891 giây | Nhầm dữ liệu chưa rõ ý nghĩa thành arXiv ID. Cần hỏi người dùng muốn làm gì với mã, không tự chọn công cụ đọc paper. |
| S2-T5 `/turns/4` | Hỏi thông tin sinh viên có mã `[STUDENT_ID_02]` của Trường Đại học Cần Thơ | `lookup` nhận query chứa mã và tên trường, trả 5 nguồn chung; model nói không tìm thấy thông tin chi tiết; 8,859 giây | Không tạo ra danh tính hay thông tin cá nhân cụ thể khi không tìm thấy. Không coi các tin chung về trường là hồ sơ sinh viên được xác minh. |
| S2-T6 `/turns/5` | “tóm tắt giúp tôi bài viết này” | Không gọi tool; hỏi xin URL hoặc nội dung bằng văn bản; 3,140 giây | Hỏi lại hợp lý về nội dung nhưng chưa gọi `clarify`, cùng loại lỗi protocol còn lại trong eval. |

## Các tình huống đề xuất có nguồn gốc từ log này

Đây là đề xuất cho lần cải tiến tiếp theo, **chưa phải bộ case đã chạy/chấm mới**. Expected được đề xuất sau khi đọc log, không đưa ngược vào log để tạo PASS.

| Tình huống cần kiểm tra tiếp | Bằng chứng gốc | Hành vi mong đợi |
|---|---|---|
| Câu hỏi “hôm nay” cần ràng buộc thời gian | S1-T1 | Dùng `timeframe=day`, xác định ngày hiện tại và phân biệt ngày xuất bản/giá cập nhật; không gọi nguồn cũ là hôm nay. |
| “Gần đây” không đồng nghĩa “hay nhất mọi thời” | S2-T1 | Giữ hoặc làm rõ khoảng thời gian; không bỏ từ khóa thời gian khi chuyển sang query. |
| Giới thiệu đúng UI và nguồn API của ứng dụng | S1-T3/T4 | Dùng thông tin ứng dụng đã cấu hình; phân biệt Streamlit, adapter, gateway và model ID; không đoán backend. |
| Không in mã giả tool thành câu trả lời | S2-T3 | Gọi function có cấu trúc nếu cần công cụ; nếu không có lời gọi thật thì không nhận là đã tìm nguồn. |
| Mã chưa rõ ý nghĩa cần hỏi lại | S2-T4 | Dùng `clarify` để hỏi mục đích thay vì đoán đó là arXiv ID. |
| Thiếu URL cần đúng giao thức hỏi lại | S2-T6 | Gọi `clarify(response_type="text")`, chờ câu trả lời và dùng URL được bổ sung. |

## Quan hệ với kết quả lab

Điểm tự động **base 85%, nhóm 90%** vẫn giữ nguyên vì bộ dữ liệu, prompt/tools và grader không đổi. Hai phiên web này bổ sung bằng chứng về trải nghiệm đầu cuối và chất lượng trả lời, không thay thế run eval, unit test hoặc được cộng thành case PASS mới.

Chưa có dữ liệu về mức hài lòng, số người thử độc lập hay tỷ lệ hoàn thành nhiệm vụ trên một mẫu lớn. Những kết luận hiện tại chỉ dựa trên 10 lượt đã ghi và các vấn đề thấy trực tiếp trong log.
