# Báo cáo cá nhân — 2A202603401_PhamNguyenTatDat

## 1. Thông tin thành viên

- Họ tên: Phạm Nguyễn Tất Đạt
- MSSV: 2A202603401
- Email: datnguyen101004@gmail.com
- GitHub: datnguyen101004

## 2. Phần việc phụ trách

- **Integration & Tooling (CP1):** Thiết lập môi trường phát triển ảo, kích hoạt dependencies, kiểm tra smoke test và cổng host pytest, chạy Crash suite đạt 20/20, bổ sung bộ test kiểm định môi trường và quy chuẩn bài nộp (`check_submission`).
- **Benchmark & Report (CP5):** Thực thi ma trận benchmark 4 shapes × 14 claims × 5 seeds (280 trials), tổng hợp số liệu và phân tích ra `reports/benchmark.json`, hoàn thiện `report/team/decision_adr.md`, `report/team/group_report.md` và `report/team/research_card.md`.
- **Bonus Topic (B2):** Nghiên cứu mở rộng gắn nhãn lỗi Multi-Agent theo phân loại MAST (NeurIPS 2025), xây dựng pipeline `src/bonus/`, viết bộ test `src/tests/test_bonus_mast.py` và sinh báo cáo `reports/bonus_mast.json` (Cohen's kappa = 1.0000).

## 3. Đóng góp cụ thể

- Thiết lập Python 3.12 virtual environment (`.venv`) và cài đặt `requirements.txt`.
- Chạy xác nhận `python -m lab8.smoke` và đảm bảo cổng host `python -m pytest -q` đạt 58/58 test xanh (100% pass).
- Viết mới bộ test tích hợp `src/tests/test_integration_harness.py` gồm 4 bài kiểm tra:
  - `test_environment_and_runtime_compliance`: kiểm định Python 3.11–3.13 và SQLite runtime.
  - `test_fixtures_integrity`: kiểm định tính toàn vẹn của 14 public claims (`C-001` đến `C-014`) và world state.
  - `test_config_manifests_validity`: kiểm định cú pháp các file YAML cấu hình trong `config/`.
  - `test_crash_report_safety_status`: kiểm định trạng thái must-pass của crash safety.
- Chạy sinh `src/reports/crash.json` đạt tuyệt đối `crash_safety: 20/20`.
- Chạy ma trận benchmark 4 shapes × 5 seeds sinh `src/reports/benchmark.json`, so sánh phân tích chi phí, độ ổn định và pass rate giữa các kiến trúc.
- Soạn thảo và hoàn thiện hồ sơ báo cáo nhóm: `group_report.md` (đủ 8 mục chuẩn Rubric), `decision_adr.md` (chọn shape Workflow) và `research_card.md` (R2 MAST ablation).
- Thực hiện Bonus B2: Xây dựng pipeline gán nhãn MAST Taxonomy cho 112 failure traces, viết bộ test kiểm định `src/tests/test_bonus_mast.py` (6 passed) và tài liệu `report/team/bonus_report.md`.

## 4. Bằng chứng

- Bộ test: `src/tests/test_integration_harness.py` (4 passed), `src/tests/test_bonus_mast.py` (6 passed)
- Cổng host: `python -m pytest -q` (80 passed)
- Báo cáo an toàn và dữ liệu:
  - `src/reports/crash.json` (`crash_safety: 20/20`)
  - `src/reports/benchmark.json` (280 trials, 4 shapes × 14 claims × 5 seeds)
  - `src/reports/bonus_mast.json` (Cohen's kappa = 1.0000)
- Hồ sơ báo cáo: `report/team/group_report.md`, `report/team/decision_adr.md`, `report/team/research_card.md`, `report/team/bonus_report.md`
- Smoke test: `python -m lab8.smoke pass`

## 5. Công cụ AI đã dùng

- Dùng trợ lý AI hỗ trợ rà soát yêu cầu từ toàn bộ tài liệu Markdown của lab, phân tích quy chuẩn chấm điểm Rubric, tự động hóa việc tạo bộ test harness, chạy benchmark tự động và thiết lập hồ sơ tài liệu nhóm. Đã kiểm tra lại kết quả chạy thực tế qua pytest, benchmark runner và smoke test trên máy cục bộ.

## 6. Tự đánh giá

- Hoàn thành xuất sắc và toàn diện vai trò Integration, Benchmark & Group Report và Bonus B2, đảm bảo toàn bộ hệ thống code, test, bằng chứng benchmark và tài liệu nộp bài đạt chuẩn cao nhất (`0 FAIL, 0 WARN`, 80/80 test passed, crash 20/20, kappa = 1.0000).
