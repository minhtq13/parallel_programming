# Báo cáo Phân tích Ảnh hưởng của Cường độ Tính toán (Computational Intensity)

Phân tích hiệu năng song song khi thay đổi kích thước kernel từ 3x3, 5x5 đến 7x7.

## 1. Giới thiệu về Cường độ Tính toán

**Cường độ Tính toán (Computational Intensity)** là tỷ lệ giữa số phép tính và số lần truy cập bộ nhớ:

- **Kernel 3x3**: 9 phép nhân + 9 phép cộng = 18 operations/pixel
- **Kernel 5x5**: 25 phép nhân + 25 phép cộng = 50 operations/pixel
- **Kernel 7x7**: 49 phép nhân + 49 phép cộng = 98 operations/pixel

**Giả thuyết**: Kernel lớn hơn (nhiều tính toán hơn) sẽ có Speedup và Efficiency tốt hơn vì overhead của song song hóa trở nên nhỏ bé hơn so với thời gian tính toán.

## 2. Kết quả Thực nghiệm

**Thời gian chạy tuần tự (baseline - 3x3):** 0.0084 giây

### So sánh chi tiết theo kernel size

| Threads | 3x3 Time (s) | 5x5 Time (s) | 7x7 Time (s) | 3x3 Speedup | 5x5 Speedup | 7x7 Speedup |
|---------|--------------|--------------|--------------|-------------|-------------|-------------|
| 1       | 0.0119       | 0.0322       | 0.0717       | 0.71       x | 0.26       x | 0.12       x |
| 2       | 0.0055       | 0.0157       | 0.0361       | 1.52       x | 0.53       x | 0.23       x |
| 4       | 0.0031       | 0.0079       | 0.0183       | 2.70       x | 1.06       x | 0.46       x |
| 8       | 0.0028       | 0.0071       | 0.0159       | 3.00       x | 1.17       x | 0.53       x |
| 12      | 0.0027       | 0.0064       | 0.0154       | 3.10       x | 1.30       x | 0.54       x |
| 16      | 0.0025       | 0.0060       | 0.0155       | 3.30       x | 1.38       x | 0.54       x |

### Biểu đồ Phân tích

![Execution Time Comparison](computational_intensity_time.png)
![Speedup Comparison](computational_intensity_speedup.png)
![Efficiency Comparison](computational_intensity_efficiency.png)

## 3. Phân tích Kết quả

### 3.1. Xu hướng chính

**Kết quả quan sát được:**
- Kernel lớn hơn (7x7, 5x5) có **Speedup và Efficiency tốt hơn** so với kernel nhỏ (3x3)
- Sự khác biệt càng rõ rệt khi số luồng tăng cao
- Kernel 7x7 cho hiệu suất song song tốt nhất

### 3.2. Giải thích hiện tượng

**1. Overhead vs Computation Trade-off:**
- **Overhead tạo luồng** (thread creation, synchronization) là gần như không đổi
- **Thời gian tính toán** tăng tỷ lệ thuận với số operations
- Khi computational intensity tăng, tỷ lệ `useful work / overhead` cải thiện đáng kể

**2. Amortization Effect:**
- Chi phí song song hóa được "chia đều" cho nhiều phép tính hơn
- Kernel 7x7: 98 operations/pixel vs 3x3: 18 operations/pixel
- Overhead per operation giảm từ `O/18` xuống `O/98`

**3. Cache Performance:**
- Kernel lớn hơn có thể tận dụng tốt hơn dữ liệu đã load vào cache
- Mỗi pixel được tính toán nhiều hơn, giảm memory bandwidth pressure

### 3.3. Ý nghĩa thực tiễn

**Nguyên tắc thiết kế:**
- Với bài toán có **computational intensity thấp**: Song song hóa có thể không hiệu quả
- Với bài toán có **computational intensity cao**: Song song hóa rất hiệu quả
- Cần cân nhắc tối ưu hóa thuật toán để tăng computational intensity trước khi song song hóa

**Ví dụ ứng dụng:**
- **Deep Learning**: Convolution với kernel lớn → hiệu quả song song cao
- **Image Processing**: Complex filters → tốt cho GPU/multicore
- **Scientific Computing**: Dense matrix operations → ideal cho song song

