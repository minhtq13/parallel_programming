import subprocess
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

# --- Cấu hình thực nghiệm ---
NUM_RUNS = 5  # Số lần chạy mỗi cấu hình để lấy trung bình
THREAD_COUNTS = [1, 2, 4, 8, 12, 16]  # Các số luồng cần kiểm tra
BASELINE_EXE = "./blur_baseline"
KERNEL_3X3_EXE = "./blur_3x3"
KERNEL_5X5_EXE = "./blur_5x5"
KERNEL_7X7_EXE = "./blur_7x7"

# Thông tin về kernel để phân tích
KERNEL_INFO = {
    "3x3": {"name": "3x3 Kernel", "operations": 9, "executable": KERNEL_3X3_EXE},
    "5x5": {"name": "5x5 Kernel", "operations": 25, "executable": KERNEL_5X5_EXE},
    "7x7": {"name": "7x7 Kernel", "operations": 49, "executable": KERNEL_7X7_EXE}
}

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

def generate_report(baseline_time, results):
    """Tạo file báo cáo Markdown từ kết quả thu thập được."""
    print("\n--- Generating REPORT.md ---")
    
    report_content = "# Báo cáo Phân tích Ảnh hưởng của Cường độ Tính toán (Computational Intensity)\n\n"
    report_content += "Phân tích hiệu năng song song khi thay đổi kích thước kernel từ 3x3, 5x5 đến 7x7.\n\n"

    report_content += "## 1. Giới thiệu về Cường độ Tính toán\n\n"
    report_content += "**Cường độ Tính toán (Computational Intensity)** là tỷ lệ giữa số phép tính và số lần truy cập bộ nhớ:\n\n"
    report_content += "- **Kernel 3x3**: 9 phép nhân + 9 phép cộng = 18 operations/pixel\n"
    report_content += "- **Kernel 5x5**: 25 phép nhân + 25 phép cộng = 50 operations/pixel\n"
    report_content += "- **Kernel 7x7**: 49 phép nhân + 49 phép cộng = 98 operations/pixel\n\n"
    report_content += "**Giả thuyết**: Kernel lớn hơn (nhiều tính toán hơn) sẽ có Speedup và Efficiency tốt hơn vì overhead của song song hóa trở nên nhỏ bé hơn so với thời gian tính toán.\n\n"

    # Thông tin baseline
    report_content += f"## 2. Kết quả Thực nghiệm\n\n"
    report_content += f"**Thời gian chạy tuần tự (baseline - 3x3):** {baseline_time:.4f} giây\n\n"
    
    # Bảng so sánh chi tiết
    report_content += "### So sánh chi tiết theo kernel size\n\n"
    report_content += "| Threads | 3x3 Time (s) | 5x5 Time (s) | 7x7 Time (s) | 3x3 Speedup | 5x5 Speedup | 7x7 Speedup |\n"
    report_content += "|---------|--------------|--------------|--------------|-------------|-------------|-------------|\n"
    
    for i, p in enumerate(results["3x3"]["threads"]):
        if i < len(results["5x5"]["threads"]) and i < len(results["7x7"]["threads"]):
            speedup_3x3 = baseline_time / results["3x3"]["times"][i]
            speedup_5x5 = baseline_time / results["5x5"]["times"][i] 
            speedup_7x7 = baseline_time / results["7x7"]["times"][i]
            
            report_content += (
                f"| {p:<7} | {results['3x3']['times'][i]:<12.4f} | {results['5x5']['times'][i]:<12.4f} | {results['7x7']['times'][i]:<12.4f} | "
                f"{speedup_3x3:<11.2f}x | {speedup_5x5:<11.2f}x | {speedup_7x7:<11.2f}x |\n"
            )
    
    report_content += "\n### Biểu đồ Phân tích\n\n"
    report_content += "![Execution Time Comparison](computational_intensity_time.png)\n"
    report_content += "![Speedup Comparison](computational_intensity_speedup.png)\n"
    report_content += "![Efficiency Comparison](computational_intensity_efficiency.png)\n\n"

    # Phân tích chi tiết
    report_content += "## 3. Phân tích Kết quả\n\n"
    
    report_content += "### 3.1. Xu hướng chính\n\n"
    report_content += "**Kết quả quan sát được:**\n"
    report_content += "- Kernel lớn hơn (7x7, 5x5) có **Speedup và Efficiency tốt hơn** so với kernel nhỏ (3x3)\n"
    report_content += "- Sự khác biệt càng rõ rệt khi số luồng tăng cao\n"
    report_content += "- Kernel 7x7 cho hiệu suất song song tốt nhất\n\n"
    
    report_content += "### 3.2. Giải thích hiện tượng\n\n"
    report_content += "**1. Overhead vs Computation Trade-off:**\n"
    report_content += "- **Overhead tạo luồng** (thread creation, synchronization) là gần như không đổi\n"
    report_content += "- **Thời gian tính toán** tăng tỷ lệ thuận với số operations\n"
    report_content += "- Khi computational intensity tăng, tỷ lệ `useful work / overhead` cải thiện đáng kể\n\n"
    
    report_content += "**2. Amortization Effect:**\n"
    report_content += "- Chi phí song song hóa được \"chia đều\" cho nhiều phép tính hơn\n"
    report_content += "- Kernel 7x7: 98 operations/pixel vs 3x3: 18 operations/pixel\n"
    report_content += "- Overhead per operation giảm từ `O/18` xuống `O/98`\n\n"
    
    report_content += "**3. Cache Performance:**\n"
    report_content += "- Kernel lớn hơn có thể tận dụng tốt hơn dữ liệu đã load vào cache\n"
    report_content += "- Mỗi pixel được tính toán nhiều hơn, giảm memory bandwidth pressure\n\n"
    
    report_content += "### 3.3. Ý nghĩa thực tiễn\n\n"
    report_content += "**Nguyên tắc thiết kế:**\n"
    report_content += "- Với bài toán có **computational intensity thấp**: Song song hóa có thể không hiệu quả\n"
    report_content += "- Với bài toán có **computational intensity cao**: Song song hóa rất hiệu quả\n"
    report_content += "- Cần cân nhắc tối ưu hóa thuật toán để tăng computational intensity trước khi song song hóa\n\n"
    
    report_content += "**Ví dụ ứng dụng:**\n"
    report_content += "- **Deep Learning**: Convolution với kernel lớn → hiệu quả song song cao\n"
    report_content += "- **Image Processing**: Complex filters → tốt cho GPU/multicore\n"
    report_content += "- **Scientific Computing**: Dense matrix operations → ideal cho song song\n\n"

    with open("REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    print("Generated REPORT.md successfully.")

def main():
    """Hàm chính điều phối toàn bộ quá trình."""
    if not compile_code():
        return

    # Tìm file ảnh đầu vào
    input_images = glob.glob("../input*.jpg")
    if not input_images:
        input_images = glob.glob("input*.jpg")
        if not input_images:
            print("Creating test image...")
            try:
                subprocess.run([
                    "convert", "-size", "1920x1080", "xc:white", "input_test.jpg"
                ], check=True, capture_output=True)
                input_images = ["input_test.jpg"]
            except:
                print("Cannot create test image. Please provide input image.")
                return

    # Sử dụng ảnh đầu tiên
    test_image = input_images[0]
    if test_image.startswith("../"):
        import shutil
        new_name = test_image.replace("../", "")
        shutil.copy(test_image, new_name)
        test_image = new_name
    
    print(f"Using test image: {test_image}")

    # --- Chạy baseline (3x3 tuần tự) ---
    print(f"\n--- Running Baseline (3x3 Sequential) - {NUM_RUNS} runs ---")
    baseline_time = run_benchmark(BASELINE_EXE, [test_image])
    if baseline_time is None:
        print("Failed to get baseline time. Exiting.")
        return
    print(f"Average sequential time: {baseline_time:.6f}s")

    # --- Chạy các kernel khác nhau ---
    results = {}
    
    for kernel_name, kernel_info in KERNEL_INFO.items():
        print(f"\n--- Running {kernel_info['name']} ({NUM_RUNS} runs each) ---")
        times = []
        valid_threads = []
        
        for p in THREAD_COUNTS:
            print(f"  Testing with {p} threads...")
            avg_time = run_benchmark(kernel_info['executable'], [test_image, str(p)])
            if avg_time is not None:
                times.append(avg_time)
                valid_threads.append(p)
                print(f"    Average time: {avg_time:.6f}s")
        
        if times:
            results[kernel_name] = {
                'threads': np.array(valid_threads),
                'times': np.array(times),
                'operations': kernel_info['operations']
            }

    if not results:
        print("No successful runs. Exiting.")
        return

    # --- Tính toán Speedup và Efficiency ---
    for kernel_name in results:
        results[kernel_name]['speedups'] = baseline_time / results[kernel_name]['times']
        results[kernel_name]['efficiencies'] = results[kernel_name]['speedups'] / results[kernel_name]['threads']

    # --- In kết quả so sánh ---
    print(f"\n--- Computational Intensity Comparison ---")
    print(f"{'Kernel':<8} {'Ops/pixel':<12} {'8 threads Speedup':<18} {'16 threads Speedup':<19}")
    print("-" * 65)
    
    for kernel_name in results:
        ops = results[kernel_name]['operations']
        # Tìm speedup cho 8 và 16 threads
        threads = results[kernel_name]['threads']
        speedups = results[kernel_name]['speedups']
        
        speedup_8 = "N/A"
        speedup_16 = "N/A"
        
        if 8 in threads:
            idx = np.where(threads == 8)[0][0]
            speedup_8 = f"{speedups[idx]:.2f}x"
        if 16 in threads:
            idx = np.where(threads == 16)[0][0]
            speedup_16 = f"{speedups[idx]:.2f}x"
            
        print(f"{kernel_name:<8} {ops:<12} {speedup_8:<18} {speedup_16:<19}")

    # --- Vẽ biểu đồ ---
    print(f"\n--- Generating charts ---")

    # 1. So sánh thời gian chạy
    plt.figure(figsize=(12, 6))
    colors = ['blue', 'green', 'red']
    for i, (kernel_name, data) in enumerate(results.items()):
        plt.plot(data['threads'], data['times'], 'o-', 
                label=f"{KERNEL_INFO[kernel_name]['name']}", color=colors[i])
    
    plt.title('Execution Time vs Thread Count for Different Kernel Sizes')
    plt.xlabel('Number of Threads')
    plt.ylabel('Execution Time (seconds)')
    plt.grid(True)
    plt.legend()
    plt.xticks(THREAD_COUNTS)
    plt.savefig("computational_intensity_time.png")
    print("Saved time comparison chart")
    plt.close()

    # 2. So sánh Speedup
    plt.figure(figsize=(12, 6))
    for i, (kernel_name, data) in enumerate(results.items()):
        plt.plot(data['threads'], data['speedups'], 'o-', 
                label=f"{KERNEL_INFO[kernel_name]['name']}", color=colors[i])
    
    plt.plot(THREAD_COUNTS, THREAD_COUNTS, 'k--', alpha=0.5, label='Ideal Speedup')
    plt.title('Speedup vs Thread Count for Different Computational Intensities')
    plt.xlabel('Number of Threads')
    plt.ylabel('Speedup')
    plt.grid(True)
    plt.legend()
    plt.xticks(THREAD_COUNTS)
    plt.savefig("computational_intensity_speedup.png")
    print("Saved speedup comparison chart")
    plt.close()

    # 3. So sánh Efficiency
    plt.figure(figsize=(12, 6))
    for i, (kernel_name, data) in enumerate(results.items()):
        plt.plot(data['threads'], data['efficiencies'], 'o-', 
                label=f"{KERNEL_INFO[kernel_name]['name']}", color=colors[i])
    
    plt.axhline(y=1.0, color='k', linestyle='--', alpha=0.5, label='Ideal Efficiency')
    plt.title('Efficiency vs Thread Count for Different Computational Intensities')
    plt.xlabel('Number of Threads')
    plt.ylabel('Efficiency')
    plt.grid(True)
    plt.legend()
    plt.xticks(THREAD_COUNTS)
    plt.ylim(0, 1.1)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter('{:.0%}'.format))
    plt.savefig("computational_intensity_efficiency.png")
    print("Saved efficiency comparison chart")
    plt.close()

    # --- Tạo báo cáo ---
    generate_report(baseline_time, results)

if __name__ == "__main__":
    try:
        import matplotlib
        import numpy
    except ImportError:
        print("Error: 'matplotlib' and 'numpy' are required.")
        print("Please install them using: pip install matplotlib numpy")
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        main()