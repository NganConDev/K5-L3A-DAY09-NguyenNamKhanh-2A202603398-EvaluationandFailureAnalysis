# Team

## Thông tin nhóm

- Tên nhóm: DatToanAnKhanhQuan
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-DatToanAnKhanhQuan-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/datnguyen101004/K5-L3A-DAY08-DatToanAnKhanhQuan-FromWorkflowsToAgents, nhánh 2A202603398_NguyenNamKhanh, commit ff33243

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Nam Khánh | 2A202603398 | nguyennamkhanh@vinuni.edu.vn | nguyennamkhanh | CP3 + CP4: Ledger Durability, Policy & Crash Safety |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Nam Khánh | CP3 + CP4: Ledger Durability, Policy Enforcement & Crash Safety | ff33243 | src/tests/test_cp3_cp4_durability_policy.py |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603398_NguyenNamKhanh

### Phần việc phụ trách

- CP3: Ledger Durability, Idempotency, Crash Safety.
- CP4: Policy Enforcement, Approval Validation, Audit Integrity.

### Đóng góp cụ thể

- Xây dựng bộ test bất biến `src/tests/test_cp3_cp4_durability_policy.py` kiểm thử các trường hợp biên approval, crash trước/sau effect, conflict amount và idempotency replay.
- Tích hợp xử lý crash và idempotency (`durability.issue_refund` với full quote, không nuốt `InjectedCrash`) vào các shapes, giúp toàn bộ T11 và T12 pass 100%.
- Xác minh crash safety đạt `20/20` trên `reports/crash.json`.
- Xác minh an toàn bảo mật không rò rỉ secret / PII trong trace.

### Bằng chứng

- File test: `src/tests/test_cp3_cp4_durability_policy.py`.
- Crash report: `src/reports/crash.json` (`crash_safety: 20/20`).
- Benchmark report: `src/reports/benchmark.json`.
- Kết quả test: 60/60 passed ở host gate, 248/248 passed ở student matrix.
