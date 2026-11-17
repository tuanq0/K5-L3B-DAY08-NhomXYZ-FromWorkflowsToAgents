# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: NhomXYZ
- Lớp: L3b
- Thành viên và vai trò: xem [`TEAM.md`](../../TEAM.md).
- Commit chốt: `5552d9c` (theo [`decision_adr.md`](./decision_adr.md)).

## 2. Mục tiêu và cách tiếp cận

Mục tiêu là xử lý claim hoàn tiền với cùng một contract nhưng so sánh bốn shape: workflow xác định, một ReAct agent, orchestrator với investigator chỉ đọc, và swarm tham chiếu. Ở mọi shape, model không quyết định số tiền và không ghi ledger: code lấy dữ liệu order trong phạm vi principal, tính quote theo policy, còn host xác thực approval, áp dụng giới hạn theo order và ghi refund idempotent.

Phân công theo [`TEAM.md`](../../TEAM.md): Trần Văn Tuấn phụ trách workflow, Đào Hoàng Thắng phụ trách single agent, Nguyễn Công Minh phụ trách orchestrator. Benchmark cố định cùng bộ public 14 claim, năm seed `11,22,33,44,55`, `as_of` `2026-11-15`, MockLLM, bảng giá và evaluator; mỗi trial dùng SQLite mới. Swarm là shape tham chiếu để so sánh, không phải implementation do nhóm chọn.

## 3. Giải pháp

| Shape | Luồng xử lý | Ranh giới model/host |
| --- | --- | --- |
| Workflow | Đọc claim qua `get_claim_view`, kiểm tra order bằng `lookup_order`, tính quote bằng `compute_compensation`. | Luồng quyết định cố định trong Python; chỉ gọi `issue_refund` với full quote. |
| Single | Một ReAct agent chọn các tool đọc, tối đa 8 bước; xem claim, order, refund history và quote. | Model chọn bước đọc tiếp theo, không chọn số tiền hay ghi refund. Host dùng quote và thực hiện kiểm tra/commit. |
| Orchestrator | Tạo handoff theo allowlist; investigator chạy các tool chỉ đọc; orchestrator dùng kết quả order/policy/quote. | Không đưa secret hoặc raw claim vào handoff; investigator không có tool ghi. Host là nơi duy nhất ghi refund. |
| Swarm (tham chiếu) | Chạy các investigator và tổng hợp kết quả để đối chiếu cost, pass rate và variance. | Là baseline được cung cấp; có điểm yếu đã biết khi seed chia hết cho 5 có thể tin số ngày trong ticket thay vì order. |

Các shape tuân theo cùng ranh giới an toàn: claim và order được kiểm tra theo principal; tiền được tính trong code; approval, giới hạn refund, idempotency và ledger thuộc host. Trace ghi các event cần cho kiểm tra như decision, quote, handoff/investigator hoặc tool observation tùy shape; không ghi parent secret, raw headers, ticket thô hay PII như số điện thoại, địa chỉ, ghi chú nội bộ và tên hàng. Orchestrator dùng `handoff.v1` đã sanitize thay vì chuyển parent context.

## 4. Kết quả

Benchmark gồm 70 trial cho mỗi shape (14 claim × 5 seed). Chi phí là mô phỏng, đơn vị VND; số liệu lấy từ [`benchmark.json`](../../src/reports/benchmark.json).

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND) | Mean/p95 steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 1.00 / 1.00 |
| Single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 39.95 | 10.93 / 12.00 |
| Orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 45.71 | 2.86 / 3.00 |
| Swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3.00 |

Workflow, single và orchestrator đều đạt 70/70; workflow có cost/success thấp nhất. Swarm đạt 69/70; lần miss là do điểm yếu đã biết ở seed 55. Crash suite đạt **20/20** theo [`crash.json`](../../src/reports/crash.json). Benchmark không ghi nhận `leak_suspect`; scenario `retry_without_approval` CR-19 cũng pass trong crash suite. Chưa đưa kết quả tự kiểm trên `student_drop/` vào báo cáo này.

Theo ADR, nhóm chọn workflow dựa trên độ đúng bằng các shape còn lại và chi phí thấp nhất trên public benchmark. Kết quả này chưa xác nhận ngưỡng 0.75 trên hidden set; phiếu nghiên cứu/ablation ở [`research_card.md`](./research_card.md) cần được hoàn tất riêng.

## 5. Khó khăn và cách xử lý

Điểm cần kiểm soát là không để ticket quyết định số tiền, không vượt trần khi nhiều claim cùng order, và không làm lộ dữ liệu trong trace/handoff. Nhóm giữ việc tính quote, xác thực approval và ghi ledger ở code/host; chỉ truyền full quote cho host để host tự áp dụng giới hạn order và idempotency.

Trong lần chạy `python -m lab8.check_submission` gần nhất, benchmark, crash report và ADR được chấp nhận; checker còn báo thiếu bảng đóng góp trong `TEAM.md` và các trường research card. Bảng đóng góp đã được điền tên/vai trò; research card và test cụ thể cho từng thành viên cần được hoàn tất rồi chạy lại checker trước khi nộp. Không có lỗi runtime nào được ghi nhận trong báo cáo benchmark.

## 6. Tổng hợp đóng góp

| Thành viên | Phần phụ trách | Bằng chứng hiện có |
| --- | --- | --- |
| Trần Văn Tuấn | Workflow | Student test workflow: 62 passed; chi tiết trong báo cáo cá nhân. |
| Đào Hoàng Thắng | Single agent | Benchmark single: 70/70 public trial passed. |
| Nguyễn Công Minh | Orchestrator | Benchmark orchestrator: 70/70 public trial passed. |

Vai trò theo [`TEAM.md`](../../TEAM.md). Bảng đóng góp trong file đó cần có commit và ít nhất một test cụ thể cho mỗi người theo yêu cầu của checker.

## 7. Hạn chế và hướng cải thiện

Public benchmark chỉ có 14 claim × 5 seed, trong khi cổng hidden yêu cầu 40 claim × 5 seed; không thể suy rộng pass rate public thành kết quả hidden. MockLLM không đại diện cho model sản xuất, giá là mô phỏng và latency là `unavailable`. Hướng tiếp theo là hoàn thiện research card/ablation, chạy kiểm tra hidden khi được cung cấp, rồi cập nhật ADR nếu workflow không đạt ngưỡng hoặc shape khác cho thấy cải thiện đáng kể về độ đúng với chi phí hợp lý.

## 8. Tài liệu tham khảo

- [`docs/architecture.md`](../../docs/architecture.md) — shape và ranh giới code/model.
- [`docs/contracts.md`](../../docs/contracts.md) — contract kết quả, trace và handoff.
- [`docs/metrics.md`](../../docs/metrics.md) — định nghĩa metric và điều kiện benchmark.
- [`src/reports/benchmark.json`](../../src/reports/benchmark.json) — kết quả benchmark public.
- [`src/reports/crash.json`](../../src/reports/crash.json) — kết quả crash safety.
