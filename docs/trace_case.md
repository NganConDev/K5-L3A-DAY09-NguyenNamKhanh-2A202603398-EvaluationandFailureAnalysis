# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi nhóm 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-014@11`, run ID: `R-seeded_regression-C-014-s11` (report `E-seeded_regression-20261118-c1e0`) |
| Triệu chứng | `lab8 grader: FAIL (proposal_mismatch)`. Graders: `refund_amount_correct` FAIL (ledger ghi 90.000đ khác nhãn 120.000đ) và `refund_reply_matches_ledger` FAIL (reply nói đã hoàn 120.000đ nhưng ledger chỉ có 90.000đ) |
| Bước sai đầu tiên | Bước 5 `proposal` payload `{"amount_vnd": 120000}` (dẫn tới bước 6 `reply` `{"text": "Dạ, LogiX đã hoàn 120.000đ cho đơn O-515."}`) |
| Vì sao là bước *đầu tiên* | Bước 1-3 đúng: `handoff` ủy quyền investigator hợp lệ; `investigator` đọc đơn O-515 chuẩn xác; `quote` tính đúng tổng quyền lợi entitlement 150.000đ từ điều khoản; bước 4 `refund_history` tra cứu đúng lịch sử đã hoàn 30.000đ. Tại bước 5 agent tự ý trừ trước 150.000 - 30.000 = 120.000đ (`pre_deducted`), khiến host policy trừ tiếp lần hai còn 90.000đ |
| Failure mode | `FM-05` (pre_deducted — trừ trước khi được duyệt) & `FM-08` (misreport — reply nói số tiền khác ledger) |
| Đối chứng | Trên `fixed C-014@11`: agent không tự trừ lịch sử trước, gửi đúng proposal 150.000đ, host trừ 30.000đ và commit đúng 120.000đ vào ledger; reply báo đúng 120.000đ khớp ledger (grader PASS) |
| Regression test | `test_wrong_amount_in_ledger`, `test_reply_mismatch_ledger` trong `tests/test_lab9_graders.py`, và metric `refund_reply_matches_ledger` trong gate. Đã verify FAIL trên `seeded_regression` và PASS trên `fixed` |
| Chưa chắc chắn | Tần suất xuất hiện bug này khi chuyển từ MockLLM sang các frontier model thực tế có prompt phức tạp |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
