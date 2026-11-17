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
| CÂU | R1 / R2 / R3 / R4 | R2 · Failure taxonomy |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri et al., *Why Do Multi-Agent LLM Systems Fail?* (MAST), NeurIPS 2025, https://arxiv.org/abs/2503.13657. Loại bằng chứng: phân tích trace của nhiều framework multi-agent, gán nhãn bởi người (slide 35, 45) |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lỗi của hệ multi-agent gom được vào 14 failure mode thuộc 3 nhóm: system design, inter-agent misalignment, task verification; taxonomy dựng bằng human annotation với độ đồng thuận κ = 0.88 |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Trace của các framework MAS mã nguồn mở chạy model LLM thật trên task lập trình/toán/hội thoại. Không phải task tài chính có host gate, và không dùng model giả lập theo seed như MockLLM |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Lỗi của swarm ở seed 55 thuộc nhóm task verification: không agent nào đối chiếu số ngày trễ trong ticket với `delay_days` của order. Nếu chỉ dùng seed chia hết cho 5, swarm fail đúng các claim có ticket lệch DB (C-002) ở mọi seed: pass ≈ 13/14 = 0.929, pass^5 0.929, variance 0. Với seed không chia hết cho 5, swarm pass 1.000. Workflow (có kiểm chứng bằng code, không đọc ticket) giữ 1.000 ở cả hai tập |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, tool, 14 claim public, `config/pricing.yaml`, evaluator `lab8.metrics`, as_of 2026-11-15, SQLite mới mỗi trial, cùng hai shape workflow và swarm. Biến duy nhất được thay đổi: tập seed (5,10,15,20,25 so với 1,2,3,4,6) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: swarm trả `resolved` 20000 cho C-002 thay vì `denied` (tin số ngày trong ticket). Đo bằng pass rate, pass^5 và danh sách trial fail (`reason`) trong file report; phụ thêm cost/success |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,swarm --cases data/public_claims.jsonl --seeds 5,10,15,20,25 --out reports/ablation_r2_seed_div5.json` và `python -m lab8.benchmark --shapes workflow,swarm --cases data/public_claims.jsonl --seeds 1,2,3,4,6 --out reports/ablation_r2_seed_nondiv5.json` (chạy trong `src/`)
- Run id / file report: `src/reports/ablation_r2_seed_div5.json` (trial fail: R-swarm-C-002-s5, -s10, -s15, -s20, -s25), `src/reports/ablation_r2_seed_nondiv5.json` (không có trial fail)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng.** Seed chia hết cho 5: swarm pass 0.929, pass^5 0.929, variance 0, cost/success 53.23; cả 5 trial fail đều là C-002 với lý do `status resolved != denied`. Seed không chia hết cho 5: swarm pass 1.000, cost/success 48.72. Workflow 1.000 / pass^5 1.000 / cost/success 27.86 ở cả hai tập. Lỗi phụ thuộc hoàn toàn vào nhánh tin ticket, không phải ngẫu nhiên, nên xếp vào nhóm MAST task verification (thiếu bước kiểm chứng dữ kiện trước khi hành động). Cách sửa đúng nhóm lỗi là thêm verifier bằng code đối chiếu với order row, hoặc dùng workflow
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Lỗi của swarm ở đây được cài sẵn (`REFERENCE_WEAKNESS`) nên chỉ minh họa một failure mode, không ước lượng được tần suất lỗi của MAS thật. Chỉ có 1/14 claim public có ticket lệch DB, nên con số 0.929 phụ thuộc thành phần corpus.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
