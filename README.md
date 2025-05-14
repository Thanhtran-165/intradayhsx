## Giới thiệu

**Ứng Dụng Theo Dõi Giá Cổ Phiếu Trong Ngày** là một ứng dụng theo dõi giá cổ phiếu theo thời gian thực, được phát triển bằng Python với giao diện người dùng sử dụng thư viện `tkinter`. Ứng dụng cho phép người dùng theo dõi giá cổ phiếu, khối lượng giao dịch và các thống kê lệnh mua/bán trong thời gian thực. Dữ liệu được lấy từ API của `vnstock`.

Ứng dụng được thiết kế để hoạt động ổn định, với tính năng cập nhật dữ liệu định kỳ mà không gặp lỗi liên quan đến đa luồng trong `tkinter`.

## Tính năng chính

- Theo dõi giá cổ phiếu theo thời gian thực.
- Hiển thị thông tin giá mới nhất, khối lượng giao dịch và loại khớp lệnh.
- Thống kê lệnh mua/bán: số lượng lệnh, khối lượng trung bình và tổng giá trị.
- Hiển thị bảng thống kê theo giá với các giá trị mua, bán và giá trị ròng.
- So sánh giá hiện tại với giá trung bình 5, 10, 20 ngày.
- So sánh khối lượng giao dịch hôm nay với khối lượng trung bình 5, 10, 20 ngày.
- Cập nhật dữ liệu định kỳ với các khoảng thời gian tùy chỉnh: 1 giây, 5 giây, 10 giây, 15 giây, 30 giây, 1 phút, 5 phút, 10 phút, 15 phút.

## Yêu cầu hệ thống

- Python phiên bản 3.6 trở lên.
- Các thư viện Python: `tkinter`, `pandas`, `vnstock`, `threading`, `time`.

## Hướng dẫn cài đặt

1. **Tải mã nguồn từ GitHub**:
   ```bash
   git clone https://github.com/yourusername/stock-intraday-monitoring.git
   cd stock-intraday-monitoring
