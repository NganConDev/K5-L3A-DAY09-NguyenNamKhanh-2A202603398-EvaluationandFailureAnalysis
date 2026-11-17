# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Đạt (0.757 ≥ 0.6, 0.857 ≥ 0.8, 0.800 ≥ 0.7) | Dùng làm gate |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không đạt (κ=0.375 < 0.6, R=0.300 < 0.7) | Loại (không dùng) |

## ≥5 case audit thủ công

| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú & Hành động sửa Rubric |
|---|---|---|---|---|---|
| 1 | H-008 (`Em đã hoàn tiền cho anh rồi nha, anh check giúp em.`) | PASS | FAIL | Người đúng | Ngôn ngữ suồng sã ("em - anh", "rồi nha", "check giúp"). Cần sửa rubric: bổ sung quy định cấm dùng đại từ thân mật không quy chuẩn doanh nghiệp và từ đệm không trang trọng. |
| 2 | H-017 (`Dạ, bạn ơi LogiX đã hoàn 25.000đ cho đơn O-606 rồi nha.`) | PASS | FAIL | Người đúng | Judge bị đánh lừa bởi từ "Dạ" ở đầu câu mà bỏ qua "bạn ơi" và "rồi nha". Cần sửa rubric: chuẩn hóa cách xưng hô duy nhất là "anh/chị", không dùng "bạn ơi". |
| 3 | H-029 (`Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm.`) | PASS | FAIL | Người đúng | Giọng điệu gắt gỏng, thiếu tôn trọng khách hàng ("không cần nhắn thêm"). Judge chỉ lọc từ chửi bậy nên bỏ lọt. Cần sửa rubric: cấm các câu mang tính từ chối tiếp nhận hoặc gạt bỏ khách hàng. |
| 4 | H-042 (`Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ.`) | FAIL | PASS | Người đúng | Câu trả lời lịch sự, đầy đủ thông tin thời gian xử lý. Judge phạt oan có thể vì hiểu nhầm cam kết thời gian. Cần sửa rubric: cho phép và khuyến khích nêu thời gian tiền về dự kiến (3–5 ngày). |
| 5 | H-051 (`Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ.`) | FAIL | PASS | Người đúng | Judge phạt nặng vì chêm từ tiếng Anh "refund". Người dùng Việt vẫn chấp nhận từ này trong ngữ cảnh fintech/e-commerce. Cần sửa rubric: phân biệt rõ giữa lỗi ngôn từ thô tục với việc sử dụng thuật ngữ thanh toán thông dụng. |
| 6 | HL-016 (`LogiX xin lỗi... lặp lại 2 lần xin lỗi và kiên nhẫn`) | PASS | FAIL | Người đúng | Case helpful: Judge bị đánh lừa bởi văn phong dài dòng, lễ phép nên chấm PASS, trong khi người thấy nội dung lặp từ máy móc và thiếu hướng dẫn hành động cụ thể. |

## Kết luận
- **Tiêu chí bị loại và lý do:** `helpful` bị loại hoàn toàn khỏi CI gate do vi phạm nghiêm trọng ngưỡng Recall (R = 0.300 so với sàn 0.700) và Cohen's Kappa (κ = 0.375 so với sàn 0.600). Ma trận nhầm lẫn của `helpful` cho thấy `fn = 21` trên tổng số 30 ca lỗi (tỉ lệ bỏ sót lỗi lên tới 70%). Judge này có xu hướng thiên vị tính lịch sự và độ dài (length & politeness bias), khiến tỷ lệ lỗi quan sát bị giảm giả tạo từ 30% thực tế xuống chỉ còn 9% (`observed_fail_rate = 0.09` vs `corrected_fail_rate = 0.30`).
- **Rủi ro còn lại:** Cả hai judge đều được kiểm tra trên tập dữ liệu replay công khai có sẵn (`data/eval/judge_*_public.csv`). Khi chuyển sang môi trường sản xuất hoặc gặp dữ liệu khách hàng chưa từng thấy (unseen out-of-distribution prompts), độ tin cậy của judge tone có thể suy giảm. Cần duy trì quy trình kiểm định người thủ công (human-in-the-loop sample audit) định kỳ để liên tục cập nhật held-out evaluation set.
