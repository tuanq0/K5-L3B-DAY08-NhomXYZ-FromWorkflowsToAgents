# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: Chưa chốt — working tree còn thay đổi; cập nhật hash sau khi commit.
- Run id dẫn chứng: `R-workflow-C-001-s11` (src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000 (70/70 trial; 14 claim × 5 seed)
- Cost per success (mô phỏng, VND): 27.86 VND (tổng 1,950 VND / 70 trial thành công)
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 leak suspect trong 70 public trial workflow; 0 bypass ở scenario `retry_without_approval` (CR-19, src/reports/crash.json)

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Chọn workflow vì trên cùng bộ public 14 claim và 5 seed, workflow đạt 70/70 trial (pass rate 1.000), pass^5 1.000, seed variance 0.000 và cost per success thấp nhất trong bốn shape. Single và orchestrator cũng đạt pass rate/pass^5 1.000 nhưng cost lần lượt là 39.95 và 45.71 VND; swarm đạt pass rate 0.986, pass^5 0.929 và variance 0.000816. Vì vậy workflow là lựa chọn tốt nhất theo độ đúng và chi phí trên benchmark public hiện có.

## Có đáng đổi lấy multi-agent không

Chưa đáng đổi: single và orchestrator không tăng pass rate so với workflow nhưng tốn chi phí mô phỏng cao hơn; swarm vừa có pass rate thấp hơn vừa có variance khác 0 và chi phí cao nhất. Quyết định sẽ được xem lại nếu bộ hidden cho thấy workflow không đạt ngưỡng pass rate 0.75, hoặc một shape khác cải thiện đáng kể pass rate/bảo đảm xử lý các claim mà workflow thất bại với mức chi phí chấp nhận được.

## Trace và bằng chứng

Workflow ghi event `error` cho claim không tồn tại, `decision` cho `needs_info`/`escalated`, và `quote` sau khi tính bồi hoàn. Trace không ghi ticket thô, `parent_secret`, raw headers, hay dữ liệu order nhạy cảm như số điện thoại, địa chỉ, ghi chú nội bộ và tên hàng; các trường đó không cần cho việc kiểm tra quyết định và có thể làm lộ dữ liệu. Bằng chứng hiện có: 70/70 public trial workflow qua benchmark, trong đó scanner không phát hiện leak suspect; đây chỉ là kết quả trên corpus public.

## Giới hạn

Benchmark hiện tại chỉ có 14 public claim × 5 seed, không phải bộ hidden 40 claim × 5 seed, nên chưa chứng minh được ngưỡng hidden 0.75. Kết quả chi phí là mô phỏng với MockLLM, không đại diện cho giá API hay chất lượng model sản xuất; latency là `unavailable`. Không sửa JSON để ép đạt ngưỡng.
