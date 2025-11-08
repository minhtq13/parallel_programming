# Phân Tích Hiệu Năng Thuật Toán Làm Mờ Ảnh Song Song với OpenMP

Dự án này phân tích và so sánh hiệu năng của thuật toán làm mờ ảnh (Gaussian Blur) giữa phiên bản tuần tự và phiên bản song song được tối ưu hóa bằng OpenMP.

## Cấu trúc thư mục

- `image_baseline.cpp`: Mã nguồn C++ cho phiên bản tuần tự.
- `image_parallel.cpp`: Mã nguồn C++ cho phiên bản song song sử dụng OpenMP.
- `stb_image.h` & `stb_image_write.h`: Thư viện của bên thứ ba để đọc và ghi file ảnh.
- `Makefile`: File để tự động hóa quá trình biên dịch.
- `run_experiments.sh`: Script để chạy thực nghiệm, đo thời gian và thu thập dữ liệu.
- `plot_charts.gp`: Script Gnuplot để vẽ biểu đồ Tăng tốc (Speedup) và Hiệu suất (Efficiency).
- `input.jpg`: Ảnh đầu vào để thực hiện làm mờ. (Cần được cung cấp)
- `results.dat`: File dữ liệu được tạo ra bởi `run_experiments.sh`.
- `*.png`: Các biểu đồ được tạo ra bởi `plot_charts.gp`.

## Yêu cầu hệ thống

- Trình biên dịch C++ hỗ trợ OpenMP (ví dụ: `g++`).
- `make` để thực thi Makefile.
- `gnuplot` để vẽ biểu đồ.
- `bc` để thực hiện các phép tính số thực trong shell script.
- (Tùy chọn) `imagemagick` để tạo ảnh đầu vào nếu `input.jpg` không tồn tại.

Trên macOS, bạn có thể cài đặt các công cụ cần thiết bằng Homebrew:

```bash
brew install gcc gnuplot imagemagick
```

Lưu ý: `gcc` của Homebrew (ví dụ `g++-13`) cần được sử dụng để có hỗ trợ OpenMP. Makefile có thể cần được chỉnh sửa để trỏ đến đúng trình biên dịch.

## Hướng dẫn chạy

1. **Chuẩn bị ảnh đầu vào**:
   Đặt một file ảnh có tên `input.jpg` vào thư mục gốc của dự án. Nếu không có, script sẽ cố gắng tạo một ảnh trắng 1920x1080 nếu bạn đã cài `imagemagick`.

2. **Chạy thực nghiệm**:
   Mở terminal và thực thi script `run_experiments.sh`:

   ```bash
   chmod +x run_experiments.sh
   ./run_experiments.sh
   ```

   Script này sẽ tự động:

   - Dọn dẹp các file cũ.
   - Biên dịch cả hai phiên bản tuần tự và song song.
   - Chạy phiên bản tuần tự 5 lần và lấy thời gian thực thi trung bình.
   - Chạy phiên bản song song với số luồng thay đổi (1, 2, 4, 8, 12, 16), mỗi lần chạy 5 lần và lấy trung bình.
   - Lưu kết quả vào file `results.dat`.

3. **Vẽ biểu đồ**:
   Sau khi script `run_experiments.sh` hoàn tất, chạy Gnuplot để tạo biểu đồ:
   ```bash
   gnuplot plot_charts.gp
   ```
   Thao tác này sẽ tạo ra hai file ảnh:
   - `speedup_chart.png`: Biểu đồ tăng tốc.
   - `efficiency_chart.png`: Biểu đồ hiệu suất.

## Phân Tích Kết Quả

### 1. Biểu đồ Tăng tốc (Speedup)

- **Trục X**: Số luồng `p`.
- **Trục Y**: `Speedup = T_tuần_tự / T_song_song(p)`.
- **Kỳ vọng**: Speedup lý tưởng là một đường thẳng `y = x`. Tuy nhiên, trong thực tế, đường cong speedup sẽ tăng và sau đó "bão hòa" (cong xuống) khi số luồng tăng lên. Điều này là do các yếu tố như chi phí quản lý luồng, giới hạn của Định luật Amdahl, và các vấn đề về truy cập bộ nhớ.

### 2. Biểu đồ Hiệu suất (Efficiency)

- **Trục X**: Số luồng `p`.
- **Trục Y**: `Efficiency = Speedup / p`.
- **Kỳ vọng**: Hiệu suất lý tưởng là 1 (100%). Trong thực tế, hiệu suất sẽ giảm dần khi số luồng tăng lên. Đây là một chỉ số cho thấy mức độ "lãng phí" tài nguyên khi thêm nhiều luồng hơn.

### 3. Phân tích Ưu/Nhược điểm

#### Ưu điểm (Tại sao chương trình chạy nhanh hơn?)

1.  **"Embarrassingly Parallel"**: Vấn đề làm mờ ảnh có tính song song cao. Việc tính toán giá trị màu cho mỗi pixel gần như hoàn toàn độc lập với các pixel khác. Mỗi luồng có thể xử lý một vùng ảnh riêng biệt mà không cần giao tiếp hay đồng bộ hóa phức tạp với các luồng khác, làm giảm đáng kể chi phí overhead.
2.  **Tỷ lệ Tính toán/Truy cập bộ nhớ cao**: Đối với mỗi pixel, thuật toán thực hiện một lượng tính toán đáng kể (9 phép nhân và 8 phép cộng cho mỗi kênh màu). Tỷ lệ này đủ lớn để "che lấp" chi phí của việc tạo và quản lý luồng, giúp việc song song hóa mang lại lợi ích rõ rệt.

#### Nhược điểm (Tại sao Speedup không đạt mức lý tưởng?)

1.  **Định luật Amdahl**: Không phải tất cả các phần của chương trình đều được song song hóa. Các tác vụ như đọc file ảnh từ đĩa (`stbi_load`) và ghi file ảnh kết quả (`stbi_write_jpg`) vẫn là tuần tự. Dù có tăng số luồng lên bao nhiêu, thời gian cho các phần tuần tự này không thay đổi và trở thành "nút cổ chai" giới hạn tốc độ tổng thể.
2.  **Overhead của OpenMP**: Việc khởi tạo và quản lý các luồng bởi `#pragma omp parallel for` không phải là miễn phí. Với những ảnh có kích thước rất nhỏ, chi phí này có thể lớn hơn cả thời gian tính toán, dẫn đến hiện tượng "slowdown" (phiên bản song song chạy chậm hơn tuần tự).
3.  **False Sharing (Chia sẻ giả)**: Đây là một vấn đề tinh vi liên quan đến kiến trúc cache của CPU. Khi hai luồng chạy trên hai lõi khác nhau cùng ghi dữ liệu vào các vùng nhớ khác nhau nhưng lại nằm trên cùng một _dòng cache_ (cache line), hệ thống phần cứng sẽ phải liên tục vô hiệu hóa và đồng bộ hóa dòng cache đó giữa các lõi. Trong bài toán này, các luồng ghi vào các pixel liền kề trong mảng `output_img`, rất có khả năng gây ra false sharing, làm tăng độ trễ truy cập bộ nhớ và giảm hiệu năng.
4.  **Xử lý vùng biên**: Thuật toán bỏ qua việc xử lý các pixel ở đường viền của ảnh. Mặc dù phần này rất nhỏ, nó vẫn là một phần công việc không được song song hóa hoàn toàn, góp một phần nhỏ vào giới hạn của Định luật Amdahl.
