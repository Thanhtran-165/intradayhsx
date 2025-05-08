Công cụ Phân tích Cổ phiếu Việt Nam
Mô tả
Công cụ này cho phép người dùng phân tích chi tiết dữ liệu giao dịch trong ngày của các mã cổ phiếu Việt Nam. Nó sử dụng API từ vnstock để lấy dữ liệu và cung cấp các chỉ số tài chính quan trọng cùng các biểu đồ trực quan hóa, giúp người dùng hiểu rõ hơn về hoạt động giao dịch của mã cổ phiếu.
Tính năng chính
Lấy dữ liệu giao dịch: Sử dụng API từ vnstock để truy xuất dữ liệu giao dịch trong ngày.
Phân tích dữ liệu: Tính toán các chỉ số quan trọng như:
Dòng tiền vào, dòng tiền ra, dòng tiền ròng.
Số lượng lệnh mua/bán và khối lượng trung bình của lệnh mua/bán.
Các chỉ số khác: volatility (độ biến động giá), imbalance ratio (tỷ lệ mất cân đối), order-to-volume ratio (tỷ lệ lệnh trên khối lượng).
Hiển thị kết quả:
Phần tóm tắt được định dạng đẹp mắt với các thông tin chính như tổng dòng tiền, giá cao nhất/thấp nhất, v.v.
Biểu đồ trực quan hóa:
Biểu đồ dòng tiền ròng lũy kế với chú thích các điểm đột biến (dựa trên IQR).
Biểu đồ tỷ lệ khối lượng trung bình lệnh mua/bán.
Biểu đồ dòng tiền mua/bán lũy kế.
Heatmap áp lực mua/bán (dòng tiền ròng) với bảng màu coolwarm.
Biểu đồ khối lượng giao dịch theo thời gian.
Biểu đồ áp lực mua/bán.
Biểu đồ số lệnh mua/bán lũy kế.
Phân bố số lệnh theo giá.
Phân bố khối lượng theo giá.
Phân bố dòng tiền theo giá.
Cơ chế retry: Tự động thử lại tối đa 5 lần nếu gặp lỗi khi lấy dữ liệu, với thời gian chờ tăng dần.
Giao diện người dùng: Đơn giản, cho phép nhập mã cổ phiếu để phân tích hoặc gõ "END" để kết thúc.
Cài đặt
Để sử dụng công cụ, bạn cần cài đặt các thư viện Python sau:
bash
pip install pandas numpy matplotlib seaborn vnstock
Đảm bảo bạn đã cài đặt Python (phiên bản 3.6 trở lên) và các công cụ quản lý package như pip.
Cách sử dụng
Tải mã nguồn từ repository và mở terminal tại thư mục chứa file.
Chạy file Python chính (giả sử tên file là stock_analysis.py):
bash
python stock_analysis.py
Nhập mã cổ phiếu (ví dụ: ACB, VIC, VNM) khi được yêu cầu.
Xem phần tóm tắt và các biểu đồ phân tích được hiển thị.
Gõ END để kết thúc chương trình.
Lưu ý
Mã cổ phiếu cần được nhập đúng định dạng (viết hoa, ví dụ: ACB).
Đảm bảo kết nối internet để lấy dữ liệu từ API.
Ví dụ
Khi chạy chương trình:
=== HỆ THỐNG PHÂN TÍCH CỔ PHIẾU ===
Hướng dẫn:
- Nhập mã cổ phiếu (ví dụ: ACB, VIC, VNM...) để xem phân tích
- Gõ END để kết thúc phiên làm việc
==================================

Nhập mã cổ phiếu để xem (gõ END để kết thúc): ACB
Đang tải dữ liệu cho mã ACB... Vui lòng chờ...
Bạn sẽ nhận được phần tóm tắt (dòng tiền, số lệnh, giá, v.v.) và các biểu đồ phân tích cho mã ACB.
