# Bonus report: B2

- Topic + nguồn (tên, năm, slide): MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* (Slide 35, 45 bài lý thuyết N8).
- CLAIM của nguồn (1 câu): Các thất bại trong hệ thống Multi-Agent LLM phân rã thành 14 failure modes thuộc 3 nhóm chính (System Design, Inter-agent Misalignment, Task Verification) với độ đồng thuận chú giải cao (Cohen's $\kappa = 0.88$).
- BOUNDARY (model / dataset / setup): Áp dụng trên hệ thống xử lý khiếu nại LogiX-VN với 4 kiến trúc (Workflow, Single ReAct, Orchestrator, Swarm) trên bộ dữ liệu public claims và MockLLM đa hạt giống (seed 11–55).
- HYPOTHESIS trên LogiX: Các lỗi thực tế trong LogiX-VN (đặc biệt là hiện tượng Swarm thất bại ở seed 55) có thể tự động nhận diện và gán nhãn chính xác vào phân loại MAST dựa trên sự kiện trong nhật ký trace, đạt độ tương đồng cao với chuyên gia gán nhãn thủ công ($\kappa \ge 0.85$).
- Biến cố định / biến thay đổi: Cố định bộ quy tắc nghiệp vụ LogiX-VN, bảng giá mô phỏng, và danh sách 14 public claims; thay đổi kiến trúc thực thi (shape), hạt giống ngẫu nhiên (seed 11–55), và cơ chế tiêm lỗi có chủ đích (Fault Injection).
- Lệnh tái lập (copy-paste được):
  ```bash
  python -m bonus.mast_tag --benchmark reports/benchmark_swarm.json --traces traces --out reports/bonus_mast.json
  python -m pytest -q tests/test_bonus_mast.py
  ```
- File report + run id: `src/reports/bonus_mast.json`, phân tích ca `R-swarm-C-002-s55`.

---

## Kết quả

Số liệu trích xuất tự động từ `src/reports/bonus_mast.json`:

### 1. Phân loại lỗi theo Kiến trúc × Nhóm MAST
| Kiến trúc (Shape) | System Design | Inter-agent Misalignment | Task Verification | Tổng lỗi nhận diện |
|---|:---:|:---:|:---:|:---:|
| **Swarm Reference** (Seed 11–55) | 0 | 0 | 1 | 1 |
| **Fault Injection Benchmarks** | 2 | 2 | 1 | 5 |

### 2. Đánh giá độ tin cậy liên người đánh giá (Inter-Annotator Agreement)
Đối chiếu giữa bộ tự động gắn nhãn `mast_tag.py` và 15 mẫu gán nhãn thủ công (Human Annotation):
* **Số lượng mẫu đánh giá ($N$):** 15 mẫu (bao gồm các ca thực tế và các ca thử nghiệm cố tình gây lỗi).
* **Tỷ lệ đồng thuận quan sát ($P_o$):** 100.0% (15/15 ca trùng khớp).
* **Xác suất đồng thuận ngẫu nhiên ($P_e$):** 0.3600.
* **Hệ số Cohen's Kappa ($\kappa$):** **1.0000** (vượt ngưỡng tin cậy cao $\kappa \ge 0.80$ của nghiên cứu MAST gốc $\kappa = 0.88$).

### 3. Ma trận tương quan (Contingency Matrix)
| Nhãn Chuyên gia (Human) \ Nhãn Máy (Auto) | System Design | Inter-agent Misalignment | Task Verification |
|---|:---:|:---:|:---:|
| **System Design** | 7 | 0 | 0 |
| **Inter-agent Misalignment** | 0 | 4 | 0 |
| **Task Verification** | 0 | 0 | 4 |

---

## Kết luận

**ỦNG HỘ HYPOTHESIS.**

### 1. Phân tích nguyên nhân lỗi Swarm ở Seed 55:
* **Hồ sơ thất bại:** Claim `C-002` ở `seed = 55` (Run ID: `R-swarm-C-002-s55`).
* **Hiện tượng:** Kết quả trả về `status = resolved` với tiền bồi thường 20.000đ, trong khi kết quả đúng phải là `denied` (0đ).
* **Nhóm lỗi MAST:** Thuộc nhóm **Task Verification** (Failure Mode `TV-1: Grounding Failure / Untrusted Text Belief`).
* **Cơ chế gây lỗi:**
  * Đơn hàng `O-202` trong cơ sở dữ liệu có số ngày trễ thực tế là `delay_days = 2` (< 3 ngày nên không đủ điều kiện bồi thường).
  * Ở seed 55, agent đọc hiểu tin nhắn bị "ảo giác" bởi câu chữ phàn nàn của khách hàng trong ticket, phát sinh sự kiện `model_override` gán đè `delay_days = 5`.
  * Do thiếu bước đối soát độc lập với dữ liệu gốc, thông tin sai lệch này được đưa vào bộ tính toán `compute_compensation`, dẫn đến việc chi trả sai quy định.
* **Biện pháp khắc phục (Mitigation theo Slide 35):**
  * Áp dụng mẫu thiết kế **Evaluator-Verifier / Ground-Truth Assertion**: Chèn một bộ kiểm tra chéo bằng code cứng trước khi gọi host ghi tiền. Nếu thông tin tính toán mâu thuẫn với bản ghi có cấu trúc trong bảng `orders`, hệ thống phải tự động bác bỏ hoặc ép buộc đọc lại dữ liệu thật.

### 2. Điều kiện kết luận có thể đảo ngược:
* Nếu hệ thống chuyển sang xử lý các ticket khiếu nại mở (open-domain) không có cơ sở dữ liệu đối chứng có cấu trúc, ranh giới giữa *Inter-agent Misalignment* (hiểu lầm giữa các agent) và *Task Verification* (kiểm chứng nghiệp vụ) sẽ trở nên mờ nhạt hơn, đòi hỏi quy trình gán nhãn phức tạp hơn quy tắc heuristic.

---

## Giới hạn

1. **Mô hình giả lập (MockLLM):** Hành vi của agent được kích hoạt thông qua hạt giống giả lập (`seed`), chưa phản ánh trọn vẹn độ ngẫu nhiên phi tất định và các dạng biến thể ngôn ngữ phức tạp của LLM thương mại trong môi trường sản xuất.
2. **Đo lường Latency:** Thời gian trễ trong môi trường kiểm thử là `unavailable` (mô phỏng), chưa đo được độ trễ mạng thực tế khi các agent giao tiếp phân tán.
3. **Số lượng mẫu kiểm thử:** Tập dữ liệu public gồm 14 claims mẫu; để hoàn thiện bộ phân loại cần mở rộng kiểm thử trên tập dữ liệu đa dạng hơn.
