# Báo cáo cá nhân — 2A202603398_NguyenNamKhanh

## 1. Thông tin thành viên

- Họ tên: Nguyễn Nam Khánh
- MSSV: 2A202603398
- Email: nguyennamkhanhnd2004@gmail.com
- GitHub: ngancondev

## 2. Phần việc phụ trách

- **CP3:** Ledger Durability, Idempotency, Crash Safety (Xử lý giao dịch nguyên tử, chống ghi trùng, cơ chế phục hồi sau crash).
- **CP4:** Policy Enforcement, Approval Validation, Audit Integrity (Cổng duyệt quyền, ràng buộc approval theo claim, áp trần hoàn tiền theo đơn và kiểm toán audit).

## 3. Đóng góp cụ thể

- Phân tích luồng nghiệp vụ và ranh giới bảo mật giữa Shape và Host trong hệ thống LogiX-VN.
- Thêm bộ test `src/tests/test_cp3_cp4_durability_policy.py` bao quát 6 nhóm ca biên:
  - Crash trước effect (đảm bảo không rác DB, resume thành công).
  - Crash sau checkpoint (đảm bảo idempotent replay).
  - Trạng thái approval không hợp lệ (`pending`, `rejected`).
  - Approval số tiền không dương (<= 0).
  - Ranh giới ngày hết hạn của approval đối chiếu với ngày hiệu lực hệ thống (`as_of`).
  - Xung đột số tiền khi replay bảo toàn số tiền cũ và ghi nhận audit `amount_conflict`.
- Đảm bảo ranh giới giao dịch ở các shapes: luôn truyền toàn bộ quote vào `durability.issue_refund`, truyền `crash_at`, không bắt `InjectedCrash` và flush trace trước khi crash.
- Chạy và xác minh suite crash đạt tuyệt đối `crash_safety: 20/20` (`reports/crash.json`).
- Kiểm soát trace contract v1: đảm bảo `approval_bypass_count = 0`, `secret_leak_count = 0`, `pii_leak_count = 0`.

## 4. Bằng chứng

- File test đóng góp: `src/tests/test_cp3_cp4_durability_policy.py`.
- Kết quả test:
  - Host gate (`python -m pytest -q`): `60 passed` (bao gồm 6 test mới).
  - Student matrix (`python -m pytest -q -m student -o addopts=`): `248 passed` (đặc biệt T11 và T12 pass 100% trên cả 4 shapes).
- File bằng chứng sinh tự động:
  - `src/reports/crash.json`: `20/20` scenarios pass.
  - `src/reports/benchmark.json`: Pass rate 1.000 trên Workflow, Single, Orchestrator.
- Commit hash: `ff33243`

## 5. Công cụ AI đã dùng

- Công cụ: Antigravity Assistant.
- Mục đích: Hỗ trợ phân tích luồng code trong `durability.py` và `policy.py`, gợi ý các ca biên kiểm thử idempotency và crash recovery.
- Cách tự kiểm tra:
  - Chạy `python -m pytest -q` trên terminal môi trường cục bộ để xác minh assertions.
  - Chạy `python -m lab8.crash_test` để xác nhận 20 crash points.
  - Đối chiếu SQLite database bằng các truy vấn SQL trực tiếp để kiểm tra tính toàn vẹn dữ liệu.

## 6. Tự đánh giá

- Hoàn thành đầy đủ 100% nhiệm vụ CP3 và CP4 được phân công.
- Vượt qua toàn bộ 3 điều kiện Must-Pass của lab (Không bypass approval, không rò rỉ secret/PII, crash safety 20/20).
- Đóng góp test case thực tế và code chạy ổn định trên toàn bộ ma trận kiểm thử.
