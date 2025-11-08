# Parallel Image Processing Performance Analysis

Dự án phân tích hiệu năng của thuật toán làm mờ ảnh song song với các kích thước ảnh đầu vào khác nhau, minh chứng cho Định luật Amdahl và ảnh hưởng của overhead.

## 📋 Mục tiêu

- Phân tích hiệu năng song song hóa thuật toán xử lý ảnh
- So sánh Speedup và Efficiency với các kích thước ảnh khác nhau
- Minh chứng Định luật Amdahl trong thực tế
- Phân tích ảnh hưởng của overhead và kích thước bài toán

## 🛠 Yêu cầu hệ thống

### Phần mềm cần thiết:

- **C++ compiler** (gcc, clang) với hỗ trợ C++11
- **Make** build system
- **Python 3.x** với các thư viện:
  - `numpy` - Tính toán số học
  - `matplotlib` - Vẽ biểu đồ
  - `Pillow` (PIL) - Tạo ảnh test (tùy chọn)

### Cài đặt dependencies:

```bash
# Trên macOS với Homebrew
brew install python3
pip3 install numpy matplotlib Pillow

# Trên Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip make gcc
pip3 install numpy matplotlib Pillow

# Trên Windows với Python đã cài
pip install numpy matplotlib Pillow
```

## 🚀 Cách sử dụng

### 1. Phương pháp tự động (Khuyến nghị)

```bash
# Cấp quyền thực thi cho script
chmod +x run_experiment.sh

# Chạy toàn bộ thực nghiệm
./run_experiment.sh
```

Script này sẽ:

- Kiểm tra dependencies
- Tạo ảnh test với các kích thước khác nhau
- Biên dịch code C++
- Chạy benchmark cho tất cả ảnh
- Tạo báo cáo và biểu đồ

### 2. Phương pháp thủ công

#### Bước 1: Biên dịch project

```bash
make clean && make
```

#### Bước 2: Tạo ảnh test (tùy chọn)

```bash
# Tạo ảnh với pattern gradient (mặc định)
python3 create_test_images.py

# Tạo ảnh với pattern khác
python3 create_test_images.py --pattern noise
python3 create_test_images.py --pattern checkerboard
python3 create_test_images.py --pattern colorful

# Tạo ảnh với kích thước custom
python3 create_test_images.py --custom 1024x768 2048x1536
```

#### Bước 3: Chạy phân tích

```bash
# Chạy với ảnh cụ thể
python3 run_analysis.py input_1024x768.jpg input_4096x3072.jpg

# Tùy chỉnh số lần chạy và số threads
python3 run_analysis.py --runs 5 --threads 1 2 4 8 16

# Chỉ chạy với ảnh được chỉ định
python3 run_analysis.py my_image.jpg another_image.png
```

## 📊 Kết quả đầu ra

Sau khi chạy xong, bạn sẽ có:

### Files kết quả:

- **`REPORT.md`** - Báo cáo chi tiết với phân tích và bảng số liệu
- **`speedup_comparison.png`** - Biểu đồ so sánh speedup của 4 kích thước ảnh
- **`efficiency_comparison.png`** - Biểu đồ so sánh efficiency của 4 kích thước ảnh
- **`execution_time_comparison.png`** - Biểu đồ so sánh thời gian thực thi
- **`speedup_ratio_comparison.png`** - Biểu đồ tỷ lệ speedup so với lý tưởng

````

#### Bước 4: Tạo biểu đồ nâng cao (tùy chọn)

```bash
# Tạo các biểu đồ phân tích chi tiết
python3 advanced_analysis.py

# Chỉ hiển thị thống kê, không tạo biểu đồ
python3 advanced_analysis.py --no-charts
````

## 📊 Kết quả đầu ra

Sau khi chạy xong, bạn sẽ có:

### Files kết quả:

- **`REPORT.md`** - Báo cáo chi tiết với phân tích và bảng số liệu
- **`speedup_comparison.png`** - So sánh speedup với đường baseline (đen) và lý tưởng (đỏ)
- **`baseline_vs_parallel_time.png`** - So sánh trực tiếp thời gian: baseline vs parallel
- **`performance_gain.png`** - Biểu đồ cột hiển thị mức cải thiện hiệu năng
- **`efficiency_comparison.png`** - So sánh efficiency của 4 kích thước ảnh
- **`speedup_ratio_comparison.png`** - Tỷ lệ so với lý tưởng
- **`execution_time_comparison.png`** - So sánh thời gian thực thi
- **`efficiency_heatmap.png`** - Heatmap hiệu suất

## 🔬 Phân tích kết quả

### Những điều bạn sẽ quan sát được:

1. **Ảnh hưởng của kích thước ảnh:**

   - Ảnh lớn hơn → Speedup cao hơn
   - Ảnh lớn hơn → Efficiency gần với lý tưởng hơn

2. **Minh chứng Định luật Amdahl:**

   - Overhead song song hóa gần như cố định
   - Tỷ lệ overhead/computation giảm với ảnh lớn
   - Phần tuần tự hiệu quả giảm với ảnh lớn

3. **Điểm bão hòa:**
   - Speedup không tăng tuyến tính với số threads
   - Có điểm tối ưu (thường 8-12 threads)
   - Sau đó hiệu quả giảm do overhead quản lý

### Ví dụ kết quả mong đợi:

```
Resolution       Max Speedup    Best Efficiency    Optimal Threads
640x480         2.78x          23.1%              12
1024x768        2.94x          24.5%              12
2560x1560       3.51x          29.2%              12
4096x3072       3.32x          41.6%              8
```

**Minh chứng Định luật Amdahl rõ ràng:**

- Speedup tăng từ 2.78x → 3.51x khi kích thước ảnh tăng từ 640x480 → 2560x1560
- Cải thiện khoảng 26% trong hiệu năng song song với ảnh lớn hơn
- Số threads tối ưu thường là 8-12 threads trên hệ thống này
- Overhead tương đối giảm đáng kể với kích thước bài toán lớn

## 🎯 Ứng dụng thực tế

Kết quả này giúp:

- **Chọn kích thước bài toán phù hợp** cho đánh giá hiệu năng song song
- **Tối ưu hóa số threads** cho ứng dụng thực tế
- **Hiểu rõ overhead** và cách giảm thiểu
- **Thiết kế benchmark** hiệu quả cho thuật toán song song

## 🛠 Tùy chỉnh

### Thay đổi cấu hình trong `run_analysis.py`:

```python
NUM_RUNS = 5              # Số lần chạy để lấy trung bình
THREAD_COUNTS = [1, 2, 4, 8, 10, 12]  # Danh sách số threads test
```

### Tạo ảnh test custom:

```python
# Trong create_test_images.py, thêm kích thước mới:
custom_sizes = [
    (1024, 768, "input_1024x768.jpg"),
    (4096, 3072, "input_4096x3072.jpg")
]
```

## 🐛 Xử lý lỗi

### Lỗi biên dịch:

```bash
# Kiểm tra compiler
gcc --version
make --version

# Clean và rebuild
make clean
make
```

### Lỗi Python dependencies:

```bash
# Kiểm tra Python
python3 --version

# Cài đặt lại dependencies
pip3 install --upgrade numpy matplotlib Pillow
```

### Lỗi không tìm thấy ảnh:

```bash
# Tạo ảnh test
python3 create_test_images.py

# Hoặc đặt ảnh có sẵn vào thư mục và chạy:
python3 run_analysis.py your_image.jpg
```

## 📚 Tài liệu tham khảo

- [Định luật Amdahl](https://en.wikipedia.org/wiki/Amdahl%27s_law)
- [Parallel Computing Performance Metrics](https://en.wikipedia.org/wiki/Speedup)
- [OpenMP Programming](https://www.openmp.org/)

## 📞 Liên hệ

Nếu gặp vấn đề, hãy kiểm tra:

1. Dependencies đã cài đặt đúng chưa
2. Code C++ biên dịch thành công chưa
3. File ảnh có tồn tại không
4. Quyền thực thi các file script

Chúc bạn thử nghiệm thành công! 🎉
