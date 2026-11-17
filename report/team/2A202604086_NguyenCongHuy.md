# Báo cáo cá nhân — 2A202604086_NguyenCongHuy

## 1. Thông tin thành viên

- Họ tên: Nguyễn Công Huy
- MSSV: 2A202604086
- Email: conghuycr@gmail.com
- GitHub: https://github.com/HyperSyst

## 2. Phần việc phụ trách

- Hoàn thành và kiểm thử shape `orchestrator` trong [src/lab8/shapes/orchestrator.py](../../src/lab8/shapes/orchestrator.py).
- Xác nhận ranh giới an toàn giữa host và worker: handoff chỉ chứa field allowlist, tool chỉ read-only, không có write tool.
- Kiểm tra trace và bảo mật dữ liệu để tránh lộ `parent_secret`, headers, SĐT, địa chỉ và ghi chú nội bộ.

## 3. Đóng góp cụ thể

- Implemented `run_claim` cho orchestrator theo đúng contract của lab.
- Dùng `make_handoff` để tạo handoff có `contract_version`, `claim_id`, `task`, `facts`, `allowed_tools`, `max_output_tokens` và loại bỏ mọi dữ liệu không cần thiết.
- Chạy `run_readonly_investigators` để truy vấn `lookup_order`, `lookup_policy`, `lookup_refund_history` và `compute_compensation` mà không cấp quyền ghi.
- Lấy quote từ investigator, làm việc với `issue_refund` để host kiểm tra approval, cap theo đơn và idempotency.
- Trả về các nhánh `needs_info`, `escalated`, `denied`, `resolved`, `failed` thông qua `finish(...)`.
- Truyền `crash_at` tới `issue_refund` và không bắt `InjectedCrash`.

## 4. Bằng chứng

- File chính: [src/lab8/shapes/orchestrator.py](../../src/lab8/shapes/orchestrator.py)
- Lệnh kiểm tra: `cd src; python -m pytest -q -m student -o addopts= -k orchestrator`
- Kết quả: `62 passed, 240 deselected in 6.46s`
- Kết quả này xác nhận việc hoàn thành shape orchestrator và đúng các contract về trace, handoff và refund.

## 5. Công cụ AI đã dùng

- Copilot SDK trong VS Code / GitHub Copilot
- Dùng để đọc mã, xác nhận contract, đề xuất cấu trúc handoff, suy luận lỗi logic và kiểm tra trace/security boundary.
- Mỗi gợi ý đều được kiểm tra bằng pytest và mã nguồn để đảm bảo đúng điều kiện trong [RULES.md](../../RULES.md).

## 6. Tự đánh giá

- Mức độ hoàn thành: 9/10.
- Đã hoàn thành shape orchestrator theo đúng contract and security requirements.
- Đã validate bằng test tương ứng và giữ đúng ranh giới giữa host và worker.
- Trong tương lai, có thể mở rộng test hidden case để tăng độ tin cậy thêm.
