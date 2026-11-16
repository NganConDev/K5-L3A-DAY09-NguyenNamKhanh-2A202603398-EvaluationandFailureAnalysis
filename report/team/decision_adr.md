# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: f60bb2e
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (reports/crash.json)
- Secret leak / approval bypass: 0 / 0

## Vì sao shape này

Trên cùng tập 14 claims public và 5 seeds (11, 22, 33, 44, 55) với tổng 70 trials, `workflow` đạt độ chính xác tuyệt đối (pass rate 1.000, pass^5 1.000, variance 0.000000), đồng thời tối ưu chi phí vận hành ở mức thấp nhất (27.86 VND/lần thành công, 1.86 steps). Quy trình bồi thường có luật nghiệp vụ và ranh giới rõ ràng (tính tiền theo clause, kiểm tra quyền sở hữu order, kiểm duyệt approval và trừ trần theo đơn). Việc thực thi bằng code tuần tự loại bỏ hoàn toàn tính bất định (non-determinism) của LLM và ngăn chặn triệt để nguy cơ model bị đánh lừa bởi dữ liệu người dùng trong ticket (như trường hợp T02 hay T09).

## Có đáng đổi lấy multi-agent không

Không đáng đổi. So sánh trực tiếp với Swarm (Shape D), Swarm có chi phí cao gần gấp đôi (49.57 VND so với 27.86 VND), phương sai hạt giống cao hơn (0.000816 so với 0.000000) và pass rate thấp hơn (0.986 do fail T02 ở seed 55 vì tin delay trong ticket). Nhóm giữ nguyên `workflow` theo nguyên lý "kiến trúc ít tự chủ nhất mà vẫn hoàn thành tốt công việc". Quyết định chỉ đảo lại khi bài toán xuất hiện các yếu tố phi cấu trúc phức tạp đòi hỏi suy luận đa góc nhìn (ví dụ: thẩm định bằng chứng gian lận ảnh chụp, đối soát hóa đơn đa nguồn) mà code tuần tự hoặc rule engine không thể bao quát.

## Trace và bằng chứng

Trace của nhóm ghi nhận các sự kiện: `lookup_order` (trạng thái hiển thị), `quote` (payload tính tiền từ chính sách hiện hành), `crash` (điểm tiêm lỗi nếu có), và `decision` / `error` khi kết thúc. Cố ý **không** ghi `parent_secret`, token `Bearer`, các trường PII (`phone`, `address`, `internal_note`, `item_name`) hay toàn bộ bản ghi `claims` / `orders` thô nhằm đảm bảo an toàn biên bảo mật. Nếu trace nằm ngoài vùng scanner quét được, đội security chứng minh hệ thống an toàn bằng cách kiểm toán tĩnh (static code analysis) chứng minh các adapter (`get_claim_view`, `lookup_order`, `make_handoff`) chỉ lọc đúng allowlist và host gate chặn cứng mọi luồng ghi vi phạm.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.
