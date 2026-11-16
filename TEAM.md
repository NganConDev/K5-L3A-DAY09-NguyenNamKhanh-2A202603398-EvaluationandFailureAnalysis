# Team

## Thông tin nhóm

- Tên nhóm: DatToanAnKhanhQuan
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-DatToanAnKhanhQuan-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/datnguyen101004/K5-L3A-DAY08-DatToanAnKhanhQuan-FromWorkflowsToAgents, phamnguyentatdat

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Phạm Nguyễn Tất Đạt | datnguyen101004 | datnguyen101004@gmail.com | datnguyen101004 | Integration & Host / Eval |
|   2 | Nguyễn Ngọc Toàn | 2A202603405 |       | jpack1 | Shape B — single agent |
<<<<<<< HEAD
|   3 | Phan Bá An | 2A202603375 |       | anphn3 | Shape C — orchestrator + handoff |
|   4 | Khánh | | | | Orchestrator (Shape C) |
=======
|   3 |  |   | | | Single Agent (Shape B) |
|   4 | An | 2A202603375  |anp29239@gmail.com |anphn3 | Orchestrator (Shape C) |
>>>>>>> b855a2b09a676f65b32eb4e65aed6e1d5b5b4ccb
|   5 | Quân | | | | Evaluation & Report |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Phạm Nguyễn Tất Đạt | integration | 7158031 | tests/test_integration_harness.py |
| Nguyễn Ngọc Toàn (2A202603405, jpack1) | Shape B — single ReAct agent (`src/lab8/shapes/single.py`) | 307a9a4 | `src/tests/test_single_shape.py` (thêm mới) |
<<<<<<< HEAD
| Phan Bá An (2A202603375, anphn3) | Shape C — orchestrator + read-only investigators (`src/lab8/shapes/orchestrator.py`) | 5002904 | `src/tests/test_orchestrator_shape_c.py` (thêm mới, 7 test) |
=======
| Phan Bá An (2A202603375, anphn3) | Shape C — orchestrator + read-only investigators (...) | 5002904 | `src/tests/test_orchestrator_shape_c.py` (thêm mới, 7 test) |
>>>>>>> b855a2b09a676f65b32eb4e65aed6e1d5b5b4ccb

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## datnguyen101004_PhamNguyenTatDat

### Phần việc phụ trách

- Integration: Thiết lập môi trường Python 3.12, kích hoạt venv, kiểm định smoke test, duy trì cổng host pytest luôn xanh, chạy Crash suite (20/20), bổ sung integration test harness và kiểm định checklist submission.

### Đóng góp cụ thể

- Cài đặt virtual environment `.venv` và dependencies (`requirements.txt`).
- Xây dựng bộ test harness `src/tests/test_integration_harness.py` kiểm định môi trường runtime Python 3.11–3.13, SQLite, tính toàn vẹn 14 public claims, cấu hình YAML và crash safety.
- Chạy sinh `src/reports/crash.json` đạt chuẩn must-pass 20/20.

### Bằng chứng

- `tests/test_integration_harness.py` (4 passed)
- `src/reports/crash.json` (`crash_safety: 20/20`)
