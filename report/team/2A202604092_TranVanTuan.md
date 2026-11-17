# Báo cáo cá nhân — Trần Văn Tuấn

## 1. Thông tin thành viên

- Họ tên: Trần Văn Tuấn
- MSSV: 2A202604092
- Email: quyvangia2004@gmail.com
- GitHub: tuanq0

## 2. Phần việc phụ trách

- Hoàn thiện shape A — deterministic workflow trong [`src/lab8/shapes/workflow.py`](../../src/lab8/shapes/workflow.py).

## 3. Đóng góp cụ thể

- Thay stub `not_implemented` bằng luồng xử lý claim: đọc claim, kiểm tra order theo phạm vi principal, tính quote từ dữ liệu order và chính sách, rồi trả kết quả phù hợp.
- Xử lý các nhánh `needs_info`, `escalated`, `denied`, `failed` và `resolved`; tạo trace cho các nhánh trả kết quả.
- Chuyển nguyên quote cho `issue_refund` để host kiểm tra approval, giới hạn refund theo order và ghi ledger idempotent. Truyền tiếp `crash_at`.
- Không ghi ticket thô vào trace; chỉ dùng các trường order đã được giới hạn và quote.
- Commit chính: chưa commit phần thay đổi này; bổ sung hash sau khi commit.
- Không thêm hoặc sửa test. Đã chạy bộ student test hiện có cho workflow (xem mục 4).

## 4. Bằng chứng

- Kiểm tra: chạy từ thư mục `src/` lệnh `python -m pytest -q -m student -o addopts= -k workflow`.
- Kết quả: `62 passed, 240 deselected`.
- Các test bao gồm ca public, retry giữ một refund (T11) và crash rồi resume (T12) trong [`src/tests/test_public_matrix.py`](../../src/tests/test_public_matrix.py).
- Chưa có benchmark/run ID được ghi nhận cho phần đóng góp này.

## 5. Công cụ AI đã dùng

- Copilot trong VS Code: hỗ trợ triển khai workflow, giải thích vai trò của `compute_compensation`/`issue_refund` và cách xem trace.
- Tự kiểm tra bằng cách đối chiếu contract trong docstring của workflow và chạy student test nêu ở mục 4. Kết quả AI đề xuất cần được thành viên rà soát và tự giải thích trước khi nộp.

## 6. Tự đánh giá

- Phần workflow đã thay stub và vượt qua bộ 62 test student dành cho shape này.
- Cần nắm rõ ranh giới giữa code tính quote và host ghi refund, lý do phải truyền full quote, cùng các dữ liệu không được ghi vào trace.
