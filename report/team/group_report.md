# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: DatToanAnKhanhQuan
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-DatToanAnKhanhQuan-FromWorkflowsToAgents`
- URL repo: https://github.com/datnguyen101004/K5-L3A-DAY08-DatToanAnKhanhQuan-FromWorkflowsToAgents
- Thành viên:
  1. Phạm Nguyễn Tất Đạt (MSSV: 2A202603401) — Integration, Benchmark + Report, Bonus B2
  2. Nguyễn Ngọc Toàn (MSSV: 2A202603405) — Shape B (Single ReAct Agent)
  3. Phan Bá An (MSSV: 2A202603375) — Shape C (Orchestrator + Investigators)
  4. Nguyễn Nam Khánh (MSSV: 2A202603398) — CP3 & CP4 (Ledger Durability, Policy & Crash Safety)
  5. Lê Hoàng Quân (MSSV: 2A202603369) — Shape A (Deterministic Workflow)
- Commit chốt: `8422194` (đồng bộ với `report/team/decision_adr.md`)

---

## 2. Mục tiêu và cách tiếp cận

### Mục tiêu bài toán
Hệ thống xử lý khiếu nại hoàn cước vận chuyển tự động cho sàn thương mại điện tử **LogiX-VN**, xử lý các yêu cầu bồi thường (claims) từ khách hàng với các yêu cầu kỹ thuật nghiêm ngặt:
- **Nguyên tắc thẩm quyền (Least Privilege):** Tiền bồi thường phải được tính toán hoàn toàn bằng mã nguồn tất định (`compute_compensation`), tuyệt đối không để LLM can thiệp vào số tiền hay tự ý ghi ledger.
- **Bảo mật và toàn vẹn dữ liệu (Audit & Security):** Không để lộ chuỗi bí mật `CANARY_SECRET_*`, `parent_secret` và thông tin nhận dạng cá nhân (PII: SĐT, địa chỉ, tên hàng) ra log/trace.
- **Độ bền vững giao dịch (Durability & Idempotency):** Đảm bảo an toàn giao dịch 2 pha, tính lũy đẳng (idempotency key), chống hoàn tiền 2 lần (double refund) kể cả khi hệ thống gặp sự cố sập nguồn (Crash Injection).

### Phân công công việc
Nhóm chia thành 5 vai trò độc lập theo đúng quy trình phân rã kỹ thuật:
- **Đạt:** Khởi tạo môi trường, test harness tích hợp, thực thi ma trận benchmark 4 shapes, hoàn thiện báo cáo và hồ sơ nộp bài, triển khai Bonus B2 (MAST Tagging).
- **Quân:** Hiện thực Shape A (Deterministic Workflow), kiểm soát luồng tất định thuần code.
- **Toàn:** Hiện thực Shape B (Single ReAct Agent), kiểm soát vòng lặp suy luận có giới hạn bước.
- **An:** Hiện thực Shape C (Orchestrator + Handoff), kiểm soát kiến trúc phân rã điều phối và trinh sát chỉ đọc.
- **Khánh:** Đảm bảo tính toàn vẹn CP3 & CP4 (Durability, Crash recovery, Policy enforcement, bộ test biên).

---

## 3. Giải pháp kỹ thuật

### Shape A — Deterministic Workflow (`src/lab8/shapes/workflow.py`)
- **Luồng xử lý:** Thực thi tuần tự 100% bằng code Python: Đọc claim qua view an toàn `get_claim_view` $\rightarrow$ Kiểm tra `order_id` (nếu thiếu trả `needs_info`) $\rightarrow$ Tra cứu đơn qua `lookup_order` với `principal_id` (nếu không hiển thị trả `escalated`) $\rightarrow$ Tính tiền bằng `compute_compensation` từ dữ liệu thật của đơn (bỏ qua số ngày trễ ghi trong ticket) $\rightarrow$ Nếu quote = 0 trả `denied`, nếu > 0 gọi `durability.issue_refund`.
- **Ranh giới:** Không sử dụng model call cho logic nghiệp vụ (`model_calls = 0`). Truyền nguyên vẹn **Full Quote** để host tự trừ trần theo đơn.

### Shape B — Bounded Single ReAct Agent (`src/lab8/shapes/single.py`)
- **Luồng xử lý:** Vòng lặp ReAct (Thought $\rightarrow$ Action $\rightarrow$ Observation) có giới hạn tối đa 8 bước.
- **Ranh giới:** Model chỉ nhận thông tin qua format chuẩn `Thought: ... / Action: tool_name(...)`. Tool `compute_compensation` trực tiếp tính tiền trong DB; tool `issue_refund` chỉ được gọi ở bước cuối khi đã đủ căn cứ xác thực.

### Shape C — Orchestrator + Read-Only Investigators (`src/lab8/shapes/orchestrator.py`)
- **Luồng xử lý:** Orchestrator đóng vai trò tổng điều phối, ủy quyền các tác vụ điều tra cho các sub-agents trinh sát (`order_investigator`, `policy_investigator`).
- **Cơ chế Handoff an toàn:** Handoff chỉ truyền các trường thông tin tối thiểu theo allowlist (`order_id`, `principal_id`, `carrier`), loại bỏ hoàn toàn các trường nhạy cảm (`parent_secret`, PII). Các sub-agents chạy với quyền hạn chỉ đọc (`worker=True`), không thể gọi tool ghi ledger. Chỉ duy nhất Orchestrator có quyền gọi `issue_refund`.

### Xử lý sự cố & Durability (CP3/CP4)
- Khi gọi `durability.issue_refund(conn, claim_id, quote, crash_at=crash_at)`, các shapes **không try-catch `InjectedCrash`**, cho phép ngoại lệ văng ra ngoài tự nhiên để phục vụ kiểm thử idempotent replay khi resume lại tiến trình.

---

## 4. Kết quả thực nghiệm

### Bảng so sánh 4 Shape trên tập Public (14 claims × 5 seeds = 70 trials)
Số liệu trích xuất chính thức từ [src/reports/benchmark.json](file:///D:/AI/vin-thucchien/Lab/lab8/K5-L3A-DAY08-DatToanAnKhanhQuan-FromWorkflowsToAgents/src/reports/benchmark.json):

| Kiến trúc (Shape) | Pass Rate | Pass^5 | Seed Variance | Min - Max | Chi phí mô phỏng / thành công (VND) | Mean Steps | P95 Steps |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Workflow (A)** | **1.000** | **1.000** | **0.000000** | 1.000 - 1.000 | **27.86** | 1.00 | 1.00 |
| **Single Agent (B)** | **1.000** | **1.000** | **0.000000** | 1.000 - 1.000 | **37.16** | 6.64 | 7.00 |
| **Orchestrator (C)** | **1.000** | **1.000** | **0.000000** | 1.000 - 1.000 | **53.77** | 5.00 | 6.00 |
| **Swarm (D)** | **0.986** | **0.929** | **0.000816** | 0.929 - 1.000 | **49.57** | 2.80 | 3.00 |

### Kết quả kiểm định an toàn & tự kiểm Hidden
- **Crash Safety Suite:** Đạt **`20/20`** kịch bản an toàn tuyệt đối (file `src/reports/crash.json`), không có trường hợp nào tạo ra 2 bản ghi refund.
- **Tự kiểm tra bộ Hidden (`src/student_drop/`):** Chạy trên 40 claims ẩn × 5 seeds = 200 trials cho cả 3 shapes:
  - `error_trials = 0` (100% không crash).
  - `leak_suspect_trials = 0` (100% không lộ secret `CANARY_SECRET_*` hay PII).
- **Phân tích thất bại của Swarm ở Seed 55:** Trên claim `C-002`, khách hàng khai trễ 5 ngày nhưng dữ liệu DB thực tế chỉ trễ 2 ngày. Swarm ở seed 55 bị bẫy `model_override`, tin vào lời khai người dùng và hoàn tiền 20.000 VNĐ cho đơn không đủ điều kiện (lỗi Grounding Failure / TV-1 theo phân loại MAST).

---

## 5. Khó khăn và cách xử lý

1. **Khôi phục sự cố sau Crash Injection (T12):**
   * *Khó khăn:* Ban đầu agent có xu hướng bọc try-catch quanh `issue_refund` để tránh crash làm dừng chương trình.
   * *Cách xử lý:* Loại bỏ khối try-catch, để `InjectedCrash` lan truyền ra ngoài, giúp bộ kiểm thử T12 kích hoạt lại với cùng `claim_id` và xác minh tính lũy đẳng (idempotent recovery) thành công.
2. **Quy tắc trần bồi thường theo đơn hàng (T13, T14):**
   * *Khó khăn:* Khi một đơn có nhiều claim bồi thường, việc tự trừ phần tiền đã hoàn trước đó ở tầng Shape dẫn đến việc Host trừ lần thứ hai.
   * *Cách xử lý:* Tuân thủ kiến trúc phân tầng: Shape luôn chuyển **Full Quote**, Host chịu trách nhiệm kiểm tra lịch sử và trừ trần lũy kế.
3. **Quản lý rò rỉ dữ liệu trong Trace:**
   * *Khó khăn:* `get_claim_view` và `lookup_order` nếu trả về raw database row sẽ vô tình đưa `parent_secret` vào trace audit.
   * *Cách xử lý:* Áp dụng view filter với allowlist cứng, che giấu hoàn toàn các cột nhạy cảm trước khi đưa vào context và trace.

---

## 6. Tổng hợp đóng góp

| Thành viên | Nhiệm vụ chính | Commit kỹ thuật | Test case đóng góp |
|---|---|:---:|---|
| **Phạm Nguyễn Tất Đạt** | Integration, Test harness runtime, Bonus B2 | `7158031` | `src/tests/test_integration_harness.py` & `src/tests/test_bonus_mast.py` |
| **Nguyễn Ngọc Toàn** | Shape B (Single ReAct Agent bounded loop) | `307a9a4` | `src/tests/test_single_shape.py` |
| **Phan Bá An** | Shape C (Orchestrator + read-only investigators) | `5002904` | `src/tests/test_orchestrator_shape_c.py` |
| **Nguyễn Nam Khánh** | CP3/CP4: Durability, Idempotency, Policy & Crash | `ff33243` | `src/tests/test_cp3_cp4_durability_policy.py` |
| **Lê Hoàng Quân** | Shape A (Deterministic Workflow) | `4e5c355` | `src/tests/test_workflow.py` |

---

## 7. Hạn chế và hướng cải thiện

1. **Giới hạn của MockLLM:**
   - Trong khuôn khổ bài lab, MockLLM sử dụng mô phỏng phản hồi giả lập, chi phí token tính theo công thức ngắn và độ trễ là `unavailable`.
   - Trong môi trường thực tế với mô hình nền tảng lớn (GPT-4o, Claude 3.5 Sonnet), chi phí token của Agent sẽ lớn hơn gấp hàng chục lần so với Workflow do việc tích lũy context qua từng lượt suy luận.
2. **Khả năng mở rộng:**
   - Khi bài toán xuất hiện các yếu tố phi cấu trúc (ví dụ: phát hiện gian lận qua hình ảnh gói hàng hư hỏng, thư khiếu nại bằng nhiều ngôn ngữ), kiến trúc **Orchestrator** sẽ phát huy ưu thế vượt trội so với Workflow nhờ khả năng linh hoạt phân tích đa phương thức.

---

## 8. Tài liệu tham khảo

1. Yao, S., et al. (2023). *ReAct: Synergizing Reasoning and Acting in Language Models*. ICLR 2023.
2. Wu, Q., et al. (2023). *AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation*. arXiv:2308.08155.
3. *MAST: Multi-Agent Systems Taxonomy for Failure Modes and Evaluation*. NeurIPS 2025.
4. Tài liệu kiến trúc và hướng dẫn nghiệp vụ LogiX-VN (`docs/architecture.md`, `docs/business_rules.md`, `docs/contracts.md`).
