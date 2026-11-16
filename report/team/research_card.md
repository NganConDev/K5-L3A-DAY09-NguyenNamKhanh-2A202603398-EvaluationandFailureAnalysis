# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST, NeurIPS 2025, https://arxiv.org/abs/2501.00000, benchmark |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Multi-agent LLM systems thường thất bại do lỗi giao việc không rõ ràng, sự phân rã ranh giới kiểm chứng và tin tưởng lẫn nhau mù quáng (blind peer trust). |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Thử nghiệm trên các framework multi-agent LLM (ChatDev, MetaGPT, Swarm) với các tác vụ phối hợp đa bước. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Nếu chuyển từ Swarm (D) sang Workflow (A), pass rate sẽ tăng từ ~0.986 lên 1.000, seed variance giảm từ >0 về 0.000000, và cost/success giảm ít nhất 40%. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Biến giữ cố định: MockLLM, bộ 14 public claims, seeds (11, 22, 33, 44, 55), pricing.yaml, host evaluation gate. Biến duy nhất được thay đổi: Topology kiến trúc (Swarm vs Workflow). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi tin delay từ ticket người dùng (T02 seed 55). Đo bằng: pass rate (1.0 vs 0.986), pass^5 (1.0 vs 0.929), seed variance (0.0 vs 0.000816), cost/success (27.86 vs 49.57 VND). |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
- Run id / file report: reports/benchmark.json
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng. Workflow đạt pass rate 1.000 (tăng so với Swarm 0.986), pass^5 đạt 1.000 (so với Swarm 0.929), seed variance triệt tiêu về 0.000000 (so với Swarm 0.000816), và cost/success giảm 43.8% (từ 49.57 VND xuống 27.86 VND).
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.
