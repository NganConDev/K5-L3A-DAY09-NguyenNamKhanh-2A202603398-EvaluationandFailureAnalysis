# Team

## Thông tin nhóm

- Tên nhóm: DatToanAnKhanhQuan
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-DatToanAnKhanhQuan-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/datnguyen101004/K5-L3A-DAY08-DatToanAnKhanhQuan-FromWorkflowsToAgents, main, cebe0638701d8b49ff7af8eacb679871a49c5c38

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Phạm Nguyễn Tất Đạt | 2A202603401 | datnguyen101004@gmail.com | datnguyen101004 | Integration, Benchmark + Report, Bonus |
|   2 | Nguyễn Ngọc Toàn | 2A202603405 | nguyengoctoan20042004@gmail.com | jpack1 | Shape B — single agent |
|   3 | Phan Bá An | 2A202603375 | anp29239@gmail.com | anphn3 | Shape C — orchestrator + handoff |
|   4 | Nguyễn Nam Khánh | 2A202603398 | nguyennamkhanhnd2004@gmail.com | ngancondev | CP3 + CP4: Ledger Durability, Policy & Crash Safety |
|   5 | Lê Hoàng Quân | 2A202603369 | lehoangquanvcb@gmail.com | lehoanquanvcb | Shape A — Deterministic Workflow |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Phạm Nguyễn Tất Đạt (2A202603401, datnguyen101004) | Integration, Benchmark + Report, Bonus | 7158031 | tests/test_integration_harness.py, src/tests/test_bonus_mast.py |
| Nguyễn Ngọc Toàn (2A202603405, jpack1) | Shape B — single ReAct agent (`src/lab8/shapes/single.py`) | 307a9a4 | `src/tests/test_single_shape.py` (thêm mới) |
| Phan Bá An (2A202603375, anphn3) | Shape C — orchestrator + read-only investigators (`src/lab8/shapes/orchestrator.py`) | 5002904 | `src/tests/test_orchestrator_shape_c.py` (thêm mới, 7 test) |
| Nguyễn Nam Khánh (2A202603398, ngancondev) | CP3 + CP4: Ledger Durability, Policy Enforcement & Crash Safety | ff33243 | src/tests/test_cp3_cp4_durability_policy.py |
| Lê Hoàng Quân (2A202603369, lehoanquanvcb) | Shape A — Deterministic Workflow (Issue #2) | `4e5c355` | `src/tests/test_workflow.py::test_workflow_unknown_claim_returns_failed_without_refund` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603401_PhamNguyenTatDat

### Phần việc phụ trách

- **Integration (CP1):** Thiết lập môi trường Python 3.12, kích hoạt venv, kiểm định smoke test, duy trì cổng host pytest luôn xanh, chạy Crash suite (20/20), bổ sung integration test harness và kiểm định checklist submission.
- **Benchmark + Report (CP5):** Thực thi benchmark toàn diện 4 shapes × 14 claims × 5 seeds (280 trials), tổng hợp số liệu và phân tích ra `reports/benchmark.json`, hoàn thiện `report/team/decision_adr.md`, `report/team/group_report.md` và `report/team/research_card.md`.
- **Bonus Topic (B2):** Nghiên cứu mở rộng gắn nhãn lỗi Multi-Agent theo phân loại MAST (NeurIPS 2025), xây dựng pipeline `src/bonus/`, viết bộ test `src/tests/test_bonus_mast.py` và sinh báo cáo `reports/bonus_mast.json` (Cohen's kappa = 1.0000).

### Đóng góp cụ thể

- Cài đặt virtual environment `.venv` và dependencies (`requirements.txt`).
- Xây dựng bộ test harness `src/tests/test_integration_harness.py` kiểm định môi trường runtime Python 3.11–3.13, SQLite, tính toàn vẹn 14 public claims, cấu hình YAML và crash safety.
- Chạy sinh `src/reports/crash.json` đạt chuẩn must-pass 20/20.
- Thực thi benchmark ma trận 4 shapes × 5 seeds tạo `src/reports/benchmark.json`, kiểm tra độ lệch chuẩn, phân tích chi phí và pass rate giữa các shape.
- Soạn thảo và hoàn thiện đầy đủ hồ sơ nộp bài nhóm: `decision_adr.md`, `group_report.md` (8 phần theo chuẩn Rubric) và `research_card.md` (câu R2).
- Hoàn thành Bonus B2: gán nhãn lỗi MAST cho 112 failure traces, viết test `test_bonus_mast.py` và tạo báo cáo `report/team/bonus_report.md`.

### Bằng chứng

- `tests/test_integration_harness.py` (4 passed), `src/tests/test_bonus_mast.py` (6 passed)
- `src/reports/crash.json` (`crash_safety: 20/20`), `src/reports/benchmark.json` (280 trials), `src/reports/bonus_mast.json` ($\kappa = 1.0000$)
- `report/team/group_report.md`, `report/team/decision_adr.md`, `report/team/research_card.md`, `report/team/bonus_report.md`

## 2A202603405_NguyenNgocToan

### Phần việc phụ trách

- Shape B: Single ReAct Agent (`src/lab8/shapes/single.py`).

### Đóng góp cụ thể

- Triển khai vòng lặp ReAct có giới hạn (tối đa 8 bước), tích hợp MockLLM và các tool đọc/ghi.
- Đảm bảo tiền bồi thường tính bằng `compute_compensation`, không để LLM tự quyết định số tiền.
- Viết test kiểm thử `src/tests/test_single_shape.py`.

### Bằng chứng

- `src/tests/test_single_shape.py` (passed)
- Student matrix ma trận kiểm thử Shape B: 62 passed.

## 2A202603375_PhanBaAn

### Phần việc phụ trách

- Shape C: Orchestrator + read-only investigators (`src/lab8/shapes/orchestrator.py`).

### Đóng góp cụ thể

- Triển khai kiến trúc Orchestrator và Investigator chỉ đọc với cơ chế Handoff thông qua allowlist nghiêm ngặt.
- Ngăn chặn rò rỉ secret / PII ra ngoài trace.
- Viết bộ test `src/tests/test_orchestrator_shape_c.py` (7 tests).

### Bằng chứng

- `src/tests/test_orchestrator_shape_c.py` (7 passed)
- Student matrix ma trận kiểm thử Shape C: 62 passed.

## 2A202603398_NguyenNamKhanh

### Phần việc phụ trách

- CP3: Ledger Durability, Idempotency, Crash Safety.
- CP4: Policy Enforcement, Approval Validation, Audit Integrity.

### Đóng góp cụ thể

- Xây dựng bộ test bất biến `src/tests/test_cp3_cp4_durability_policy.py` kiểm thử các trường hợp biên approval, crash trước/sau effect, conflict amount và idempotency replay.
- Kiểm tra tính bền vững giao dịch, đảm bảo `durability.issue_refund` luôn nhận full quote, không bắt `InjectedCrash`.
- Xác minh crash safety đạt 20/20 trên `reports/crash.json`.

### Bằng chứng

- File test: `src/tests/test_cp3_cp4_durability_policy.py` (6 passed).
- Crash report: `src/reports/crash.json` (`crash_safety: 20/20`).

## 2A202603369_LeHoangQuan

### Phần việc phụ trách

- Shape A — xây dựng luồng xử lý claim tất định cho LogiX-VN theo Issue #2.

### Đóng góp cụ thể

- Triển khai `run_claim` trong `src/lab8/shapes/workflow.py`. Workflow kiểm tra mã đơn và quyền truy cập, tính số tiền đề xuất từ dữ liệu đơn hàng và policy hiện hành, rồi chuyển toàn bộ số tiền đề xuất cho host kiểm tra approval và ghi refund.
- Truyền `crash_at` cho host để kiểm thử khôi phục sau sự cố. Ghi trace cho cả các nhánh trả kết quả sớm.
- Thêm test cho mã claim không tồn tại, kiểm tra trạng thái `failed`, lý do `unknown_claim`, số dòng ledger giữ nguyên và trace có `run_id` khớp với kết quả.

### Bằng chứng

- Commit kỹ thuật `4e5c355` — Implement deterministic workflow and test unknown claim.
- Test thêm mới `src/tests/test_workflow.py::test_workflow_unknown_claim_returns_failed_without_refund`.
- Kết quả đã ghi nhận: 62 test trong ma trận public của Shape A và 54 test trong bộ mặc định đều pass.
