import subprocess
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

# --- Cấu hình thực nghiệm ---
NUM_RUNS = 5  # Số lần chạy mỗi cấu hình để lấy trung bình
THREAD_COUNTS = [1, 2, 4, 8, 12, 16]  # Các số luồng cần kiểm tra
BASELINE_EXE = "./blur_baseline"
STATIC_EXE = "./blur_static"
DYNAMIC_EXE = "./blur_dynamic"

def compile_code():
    """Biên dịch code C++ bằng Makefile."""
    print("--- Compiling C++ code ---")
    try:
        subprocess.run(["make", "clean"], check=True, capture_output=True, text=True)
        subprocess.run(["make"], check=True, capture_output=True, text=True)
        print("Compilation successful.")
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"Error during compilation: {e}")
        if hasattr(e, 'stderr'): print(e.stderr)
        return False

def run_benchmark(executable, args=[]):
    """Chạy một file thực thi nhiều lần và trả về thời gian trung bình."""
    timings = []
    for _ in range(NUM_RUNS):
        try:
            result = subprocess.run(
                [executable] + args, check=True, capture_output=True, text=True
            )
            timings.append(float(result.stdout.strip().split('\n')[-1]))
        except (subprocess.CalledProcessError, ValueError, IndexError) as e:
            print(f"Error running {executable} with args {args}: {e}")
            if hasattr(e, 'stderr'): print(e.stderr)
            return None
    return np.mean(timings) if timings else None

def generate_report(baseline_time, static_results, dynamic_results):
    """Tạo file báo cáo Markdown từ kết quả thu thập được."""
    print("\n--- Generating REPORT.md ---")
    
    report_content = "# Báo cáo So sánh Schedule Policy trong OpenMP\n\n"
    report_content += "Phân tích hiệu năng giữa `schedule(static)` và `schedule(dynamic)` trong OpenMP.\n\n"

    report_content += "## 1. Giới thiệu về Schedule Policy\n\n"
    report_content += "**Schedule Policy** là cách OpenMP quyết định phân chia vòng lặp `for` cho các luồng:\n\n"
    report_content += "- **`schedule(static)`**: Chia trước các iteration cho từng luồng một cách đều nhau. Overhead thấp nhất.\n"
    report_content += "- **`schedule(dynamic)`**: Các luồng sẽ 'xin' công việc mới khi hoàn thành iteration hiện tại. Overhead cao hơn nhưng cân bằng tải tốt hơn cho bài toán không đều.\n\n"

    # Thông tin baseline
    report_content += f"## 2. Kết quả Thực nghiệm\n\n"
    report_content += f"**Thời gian chạy tuần tự (baseline):** {baseline_time:.4f} giây\n\n"
    
    # Bảng so sánh
    report_content += "### So sánh chi tiết\n\n"
    report_content += "| Threads | Static Time (s) | Dynamic Time (s) | Static Speedup | Dynamic Speedup | Static vs Dynamic |\n"
    report_content += "|---------|-----------------|------------------|----------------|-----------------|-------------------|\n"
    
    for i, p in enumerate(static_results['threads']):
        static_speedup = baseline_time / static_results['times'][i]
        dynamic_speedup = baseline_time / dynamic_results['times'][i]
        ratio = dynamic_results['times'][i] / static_results['times'][i]
        advantage = "Static faster" if ratio > 1.0 else "Dynamic faster"
        
        report_content += (
            f"| {p:<7} | {static_results['times'][i]:<15.4f} | {dynamic_results['times'][i]:<16.4f} | "
            f"{static_speedup:<14.2f}x | {dynamic_speedup:<15.2f}x | {ratio:<6.2f}x ({advantage}) |\n"
        )
    
    report_content += "\n![Schedule Comparison - Execution Time](schedule_time_comparison.png)\n"
    report_content += "![Schedule Comparison - Speedup](schedule_speedup_comparison.png)\n\n"

    # Phân tích
    report_content += "## 3. Phân tích Kết quả\n\n"
    report_content += "### 3.1. Tại sao `static` thường nhanh hơn trong bài toán này?\n\n"
    report_content += "1. **Tính chất bài toán đồng đều**: Xử lý ảnh blur có đặc điểm là mỗi pixel đòi hỏi lượng tính toán gần như nhau (9 phép nhân + 9 phép cộng). Do đó không có vấn đề \"load imbalance\" (mất cân bằng tải).\n\n"
    report_content += "2. **Overhead thấp nhất**: `static` chia sẵn công việc từ đầu, các luồng không cần phải \"communication\" với scheduler trong quá trình thực thi.\n\n"
    report_content += "3. **Cache locality tốt hơn**: Mỗi luồng xử lý một vùng pixel liên tiếp, giúp tận dụng cache hiệu quả.\n\n"
    
    report_content += "### 3.2. Khi nào `dynamic` có lợi thế?\n\n"
    report_content += "`schedule(dynamic)` sẽ có lợi thế khi:\n"
    report_content += "- Các iteration có thời gian thực thi không đều nhau\n"
    report_content += "- Có sự can thiệp từ hệ điều hành (context switching)\n"
    report_content += "- Bài toán có các vùng tính toán phức tạp khác nhau\n\n"
    
    report_content += "### 3.3. Trade-off giữa Overhead và Load Balancing\n\n"
    report_content += "- **Static**: Overhead thấp ← → Load balancing kém (nếu bài toán không đều)\n"
    report_content += "- **Dynamic**: Overhead cao ← → Load balancing tốt\n\n"
    report_content += "Đối với bài toán xử lý ảnh (tính chất đồng đều), **static** là lựa chọn tối ưu.\n\n"

    with open("REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    print("Generated REPORT.md successfully.")

def main():
    """Hàm chính điều phối toàn bộ quá trình."""
    if not compile_code():
        return

    # Kiểm tra file ảnh đầu vào
    input_images = glob.glob("../input*.jpg")  # Tìm ảnh trong thư mục cha
    if not input_images:
        # Nếu không có, thử tìm trong thư mục hiện tại
        input_images = glob.glob("input*.jpg")
        if not input_images:
            print("Error: Không tìm thấy file ảnh nào. Đang tạo ảnh mẫu...")
            # Tạo ảnh mẫu đơn giản
            try:
                subprocess.run([
                    "convert", "-size", "1920x1080", "xc:white", "input_test.jpg"
                ], check=True, capture_output=True)
                input_images = ["input_test.jpg"]
                print("Đã tạo ảnh mẫu input_test.jpg")
            except:
                print("Không thể tạo ảnh mẫu. Vui lòng cung cấp file ảnh input.")
                return

    # Sử dụng ảnh đầu tiên cho thực nghiệm
    test_image = input_images[0]
    if test_image.startswith("../"):
        # Copy ảnh vào thư mục hiện tại để dễ quản lý
        import shutil
        new_name = test_image.replace("../", "")
        shutil.copy(test_image, new_name)
        test_image = new_name
    
    print(f"Using test image: {test_image}")

    # --- Chạy baseline (tuần tự) ---
    print(f"\n--- Running Baseline (Sequential) - {NUM_RUNS} runs ---")
    baseline_time = run_benchmark(BASELINE_EXE, [test_image])
    if baseline_time is None:
        print("Failed to get baseline time. Exiting.")
        return
    print(f"Average sequential time: {baseline_time:.6f}s")

    # --- Chạy static scheduling ---
    static_times = []
    valid_threads_static = []
    print(f"\n--- Running Static Schedule ({NUM_RUNS} runs each) ---")
    for p in THREAD_COUNTS:
        print(f"  Testing with {p} threads...")
        avg_time = run_benchmark(STATIC_EXE, [test_image, str(p)])
        if avg_time is not None:
            static_times.append(avg_time)
            valid_threads_static.append(p)
            print(f"    Average time: {avg_time:.6f}s")

    # --- Chạy dynamic scheduling ---
    dynamic_times = []
    valid_threads_dynamic = []
    print(f"\n--- Running Dynamic Schedule ({NUM_RUNS} runs each) ---")
    for p in THREAD_COUNTS:
        print(f"  Testing with {p} threads...")
        avg_time = run_benchmark(DYNAMIC_EXE, [test_image, str(p)])
        if avg_time is not None:
            dynamic_times.append(avg_time)
            valid_threads_dynamic.append(p)
            print(f"    Average time: {avg_time:.6f}s")

    if not static_times or not dynamic_times:
        print("No successful runs for comparison. Exiting.")
        return

    # --- Chuẩn bị dữ liệu cho phân tích ---
    static_results = {
        'threads': np.array(valid_threads_static),
        'times': np.array(static_times)
    }
    dynamic_results = {
        'threads': np.array(valid_threads_dynamic),
        'times': np.array(dynamic_times)
    }

    # --- In kết quả so sánh ---
    print(f"\n--- Schedule Comparison Results ---")
    print(f"{'Threads':<8} {'Static (s)':<12} {'Dynamic (s)':<13} {'Ratio (D/S)':<12} {'Winner':<10}")
    print("-" * 60)
    
    for i, p in enumerate(static_results['threads']):
        if i < len(dynamic_results['threads']):
            ratio = dynamic_results['times'][i] / static_results['times'][i]
            winner = "Static" if ratio > 1.0 else "Dynamic"
            print(f"{p:<8} {static_results['times'][i]:<12.6f} {dynamic_results['times'][i]:<13.6f} {ratio:<12.3f} {winner:<10}")

    # --- Vẽ biểu đồ ---
    print(f"\n--- Generating charts ---")

    # 1. So sánh thời gian chạy
    plt.figure(figsize=(12, 6))
    plt.plot(static_results['threads'], static_results['times'], 'o-', label='Static Schedule', color='blue')
    plt.plot(dynamic_results['threads'], dynamic_results['times'], 's-', label='Dynamic Schedule', color='red')
    plt.title('Execution Time Comparison: Static vs Dynamic Schedule')
    plt.xlabel('Number of Threads')
    plt.ylabel('Execution Time (seconds)')
    plt.grid(True)
    plt.legend()
    plt.xticks(THREAD_COUNTS)
    plt.savefig("schedule_time_comparison.png")
    print("Saved time comparison chart to schedule_time_comparison.png")
    plt.close()

    # 2. So sánh Speedup
    static_speedups = baseline_time / static_results['times']
    dynamic_speedups = baseline_time / dynamic_results['times']
    
    plt.figure(figsize=(12, 6))
    plt.plot(static_results['threads'], static_speedups, 'o-', label='Static Schedule', color='blue')
    plt.plot(dynamic_results['threads'], dynamic_speedups, 's-', label='Dynamic Schedule', color='red')
    plt.plot(THREAD_COUNTS, THREAD_COUNTS, 'k--', alpha=0.5, label='Ideal Speedup')
    plt.title('Speedup Comparison: Static vs Dynamic Schedule')
    plt.xlabel('Number of Threads')
    plt.ylabel('Speedup')
    plt.grid(True)
    plt.legend()
    plt.xticks(THREAD_COUNTS)
    plt.savefig("schedule_speedup_comparison.png")
    print("Saved speedup comparison chart to schedule_speedup_comparison.png")
    plt.close()

    # --- Tạo báo cáo ---
    generate_report(baseline_time, static_results, dynamic_results)

if __name__ == "__main__":
    try:
        import matplotlib
        import numpy
    except ImportError:
        print("Error: 'matplotlib' and 'numpy' are required.")
        print("Please install them using: pip install matplotlib numpy")
    else:
        # Chuyển vào thư mục của script để các đường dẫn tương đối hoạt động đúng
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        main()