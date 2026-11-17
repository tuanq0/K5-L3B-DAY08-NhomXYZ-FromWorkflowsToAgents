# Báo cáo cá nhân — 2A202604076_DaoHongThang

## 1. Thông tin thành viên

- Họ tên: Đào Hồng Thắng
- MSSV: 2A202604076
- Email:
- GitHub: myblue-ai

## 2. Phần việc phụ trách

Phụ trách shape B `single` (vòng ReAct). Ở CP5, chạy crash suite, ablation R2 và tự kiểm hidden cho workflow; điền research card, group report và TEAM.md.

## 3. Đóng góp cụ thể

- `d83cc69`: viết `single.py`. Hàm `decide()` chỉ chọn tool đọc theo thứ tự `get_claim_view` → `lookup_order` → `lookup_refund_history` → `compute_compensation`, rồi dừng. Vòng lặp tối đa 8 bước; mỗi bước gọi MockLLM một lần để cost được tính đúng.
- Ban đầu bị kẹt vì `run_react` chỉ đưa cho `decide()` kết quả của tool vừa gọi. Cách xử lý: giữ thêm một dict `memory` bên ngoài; sau vòng lặp, code đọc số tiền từ `memory`, không lấy từ "model".
- Truyền quote đầy đủ vào `issue_refund` để host tự trừ phần đã hoàn (T13, T14). Truyền `crash_at` vào host; khi crash chỉ ghi trace rồi `raise` lại.
- Trace của single ghi các event `think`/`observe` đã lọc. Cố ý bỏ ticket, `principal_id` và nội dung policy.
- `07dc8fb`: `crash.json` (20/20).
- `0c0c2e4`: research card R2. Ablation chỉ đổi tập seed: swarm pass 0.929 trên seed chia hết cho 5 và 1.000 trên các seed còn lại. Lỗi luôn rơi vào C-002, thuộc nhóm task verification theo MAST.
- `19dcfbb`: `hidden_selfcheck.json`. Workflow chạy 200/200 trial không lỗi, không nghi lộ secret; đối chiếu tay 40 claim với business rules, tất cả đều khớp.
- Gộp `decision_adr.md` khi bị conflict với bản của Tuấn.
- Test: chưa thêm test riêng. <!-- TODO: thêm test rồi ghi tên file vào đây -->

## 4. Bằng chứng

- `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"` ra 62 passed. Lệnh `-k single` trong CHECKPOINTS khớp nhầm cả test của shape khác nên phải lọc lại.
- Benchmark single (`src/reports/benchmark.json`): pass 1.000, pass^5 1.000, cost/success 39.95, khoảng 11 bước mỗi trial.
- Trace mẫu: `R-single-C-001-s11`.
- Ablation: `src/reports/ablation_r2_seed_div5.json`, `src/reports/ablation_r2_seed_nondiv5.json`.

## 5. Công cụ AI đã dùng

Claude (Claude Code trong VS Code): đọc hiểu docs và code host, giải thích luồng của swarm, gợi ý code cho `single.py`, chạy benchmark/ablation, viết nháp các file báo cáo.

Cách tự kiểm tra: làm lần lượt từng CP và chạy test sau mỗi bước. Ở CP2 cố ý chưa truyền `crash_at` để thấy T12 đỏ, rồi sửa ở CP3 cho xanh. Số liệu trong báo cáo đều lấy từ file JSON do lệnh của lab sinh ra, không chép tay. Phần đối chiếu hidden đọc trực tiếp world state, không dùng `compute_compensation` để tự chấm.

## 6. Tự đánh giá

Khoảng 8/10. Single chạy đúng; giải thích được ranh giới code/model: agent chỉ chọn tool, còn tiền và quyền ghi thuộc về code và host. Single tốn hơn workflow khoảng 43% mà không đúng hơn, nên nhóm chọn workflow là hợp lý. Còn thiếu test riêng. Phần viết code dựa vào AI khá nhiều, nên cần đọc kỹ lại để tự trả lời được khi giảng viên hỏi.
