import subprocess
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import re
import argparse
import sys

# --- Cấu hình thực nghiệm ---
NUM_RUNS = 3  # Giảm số lần chạy để nhanh hơn, có thể tăng lại sau
THREAD_COUNTS = [1, 2, 4, 8, 10, 12]
BASELINE_EXE = "./blur_baseline"
PARALLEL_EXE = "./blur_parallel"

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

def get_image_resolution(image_path):
    """Trích xuất độ phân giải từ tên file (ví dụ: input_1920x1080.jpg -> 1920x1080)."""
    match = re.search(r'_(\d+x\d+)', image_path)
    return match.group(1) if match else "unknown"

def generate_report(all_results):
    """Tạo file báo cáo Markdown từ kết quả thu thập được."""
    print("\n--- Generating REPORT.md ---")
    
    report_content = "# Báo cáo Phân tích Ảnh hưởng của Kích thước Bài toán\n\n"
    report_content += "Phân tích hiệu năng của thuật toán làm mờ ảnh song song với các kích thước ảnh đầu vào khác nhau.\n\n"
    report_content += f"**Cấu hình thực nghiệm:**\n"
    report_content += f"- Số lần chạy mỗi test: {NUM_RUNS}\n"
    report_content += f"- Số thread được test: {THREAD_COUNTS}\n"
    report_content += f"- Tổng số file ảnh được phân tích: {len(all_results)}\n\n"

    # Tạo bảng tóm tắt so sánh
    report_content += "## Tóm tắt so sánh\n\n"
    report_content += "| Tên file | Độ phân giải | Baseline (s) | Max Speedup | Max Efficiency | Threads tối ưu |\n"
    report_content += "|----------|--------------|--------------|-------------|----------------|----------------|\n"
    
    for image_path, data in all_results.items():
        resolution = get_image_resolution(image_path)
        if resolution == "unknown":
            resolution = os.path.basename(image_path).split('.')[0]
        
        baseline_time = data['baseline_time']
        max_speedup_idx = np.argmax(data['speedups'])
        max_speedup = data['speedups'][max_speedup_idx]
        max_efficiency = data['efficiencies'][max_speedup_idx]
        optimal_threads = data['threads'][max_speedup_idx]
        
        report_content += (
            f"| `{os.path.basename(image_path)}` | {resolution} | {baseline_time:.4f} | "
            f"{max_speedup:.2f}x | {max_efficiency:.1%} | {optimal_threads} |\n"
        )
    
    report_content += "\n"

    # Chi tiết cho từng ảnh
    for i, (image_path, data) in enumerate(all_results.items(), 1):
        resolution = get_image_resolution(image_path)
        if resolution == "unknown":
            resolution = os.path.basename(image_path).split('.')[0]
        
        baseline_time = data['baseline_time']
        
        report_content += f"## {i}. Kết quả cho ảnh: `{os.path.basename(image_path)}` ({resolution})\n\n"
        report_content += f"**Thời gian chạy tuần tự (baseline): {baseline_time:.4f} giây**\n\n"
        
        report_content += "| Threads | Time (s) | Speedup | Efficiency | So với lý tưởng |\n"
        report_content += "|---------|----------|---------|------------|-----------------|\n"
        
        for j, p in enumerate(data['threads']):
            ideal_speedup = p
            speedup_ratio = data['speedups'][j] / ideal_speedup
            report_content += (
                f"| {p:<7} | {data['times'][j]:<8.4f} | "
                f"{data['speedups'][j]:<7.2f}x | {data['efficiencies'][j]:<10.1%} | "
                f"{speedup_ratio:<15.1%} |\n"
            )
        
        # Phân tích chi tiết cho từng ảnh
        best_speedup_idx = np.argmax(data['speedups'])
        best_speedup = data['speedups'][best_speedup_idx]
        best_threads = data['threads'][best_speedup_idx]
        
        report_content += f"\n**Phân tích:**\n"
        report_content += f"- Speedup tốt nhất: **{best_speedup:.2f}x** với {best_threads} threads\n"
        report_content += f"- Hiệu suất đạt được: **{best_speedup/best_threads:.1%}** so với lý tưởng\n"
        
        # Tính overhead
        sequential_time = baseline_time
        parallel_time_1_thread = data['times'][0] if data['threads'][0] == 1 else None
        if parallel_time_1_thread:
            overhead = parallel_time_1_thread - sequential_time
            overhead_percent = overhead / sequential_time * 100
            report_content += f"- Overhead song song hóa: **{overhead:.4f}s** ({overhead_percent:.2f}%)\n"
        
        report_content += "\n"

    # So sánh tổng hợp và phân tích Amdahl
    report_content += "## So sánh tổng hợp và Phân tích Định luật Amdahl\n\n"
    report_content += "### Biểu đồ so sánh Baseline vs Parallel:\n\n"
    report_content += "![Speedup Comparison](speedup_comparison.png)\n"
    report_content += "*Biểu đồ speedup cho thấy sự cải thiện của parallel so với baseline (đường đen nằm ngang)*\n\n"
    report_content += "![Baseline vs Parallel Time](baseline_vs_parallel_time.png)\n"
    report_content += "*So sánh trực tiếp thời gian thực thi: đường đứt nét là baseline, đường liền là parallel*\n\n"
    report_content += "![Performance Gain](performance_gain.png)\n"
    report_content += "*Biểu đồ cột cho thấy mức cải thiện hiệu năng với từng kích thước ảnh*\n\n"
    report_content += "![Efficiency Comparison](efficiency_comparison.png)\n"
    report_content += "*Hiệu suất sử dụng tài nguyên với các số threads khác nhau*\n\n"
    
    report_content += "### Quan sát và Phân tích:\n\n"
    report_content += "#### 1. Ảnh hưởng của kích thước bài toán:\n"
    
    # Sắp xếp theo baseline time để phân tích
    sorted_results = sorted(all_results.items(), key=lambda x: x[1]['baseline_time'])
    smallest_image = sorted_results[0]
    largest_image = sorted_results[-1]
    
    small_max_speedup = max(smallest_image[1]['speedups'])
    large_max_speedup = max(largest_image[1]['speedups'])
    
    report_content += f"- **Ảnh nhỏ nhất** (`{os.path.basename(smallest_image[0])}`): Speedup tối đa = {small_max_speedup:.2f}x\n"
    report_content += f"- **Ảnh lớn nhất** (`{os.path.basename(largest_image[0])}`): Speedup tối đa = {large_max_speedup:.2f}x\n"
    report_content += f"- **Cải thiện**: Ảnh lớn đạt speedup cao hơn {((large_max_speedup/small_max_speedup-1)*100):.1f}%\n\n"
    
    report_content += "#### 2. Minh chứng Định luật Amdahl:\n"
    report_content += "Định luật Amdahl: `Speedup_max = 1 / (s + (1-s)/p)` với `s` là phần không song song được.\n\n"
    
    for image_path, data in all_results.items():
        resolution = get_image_resolution(image_path)
        if resolution == "unknown":
            resolution = os.path.basename(image_path).split('.')[0]
        
        # Ước tính phần tuần tự từ speedup với số thread cao nhất
        max_threads = max(data['threads'])
        speedup_max_threads = data['speedups'][np.where(data['threads'] == max_threads)[0][0]]
        estimated_s = (max_threads - speedup_max_threads) / (max_threads * speedup_max_threads - speedup_max_threads)
        estimated_s = max(0, min(1, estimated_s))  # Giới hạn trong [0,1]
        
        report_content += f"- **{resolution}**: Phần tuần tự ước tính ≈ {estimated_s:.1%}\n"
    
    report_content += "\n#### 3. Nguyên nhân overhead thấp hơn với ảnh lớn:\n"
    report_content += "- **Overhead cố định**: Thời gian tạo/hủy thread, đồng bộ hóa không thay đổi theo kích thước ảnh\n"
    report_content += "- **Khối lượng tính toán tỷ lệ**: Với ảnh lớn hơn, thời gian xử lý pixel tăng tuyến tính\n"
    report_content += "- **Tỷ lệ overhead/computation**: Giảm đáng kể với ảnh lớn → Speedup tiến gần đến lý tưởng\n\n"
    
    report_content += "#### 4. Điểm bão hòa:\n"
    report_content += "Tất cả các kích thước đều cho thấy hiện tượng 'bão hòa' khi tăng số thread quá mức:\n"
    report_content += "- **Nguyên nhân**: Overhead quản lý thread vượt qua lợi ích song song hóa\n"
    report_content += "- **Số thread tối ưu**: Thường từ 4-8 threads trên hệ thống này\n"
    report_content += "- **Khuyến nghị**: Nên chọn số thread = số lõi vật lý của CPU\n\n"
    
    report_content += "### Kết luận:\n"
    report_content += "Thực nghiệm này minh chứng rõ ràng cho **Định luật Amdahl** và tầm quan trọng của việc chọn kích thước bài toán phù hợp khi đánh giá hiệu năng song song. Với các ứng dụng thực tế, việc tối ưu hóa thuật toán song song nên tập trung vào các bài toán có kích thước lớn để đạt hiệu quả tốt nhất.\n"

    with open("REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    print("Generated detailed REPORT.md successfully.")


def main(image_files=None):
    """Hàm chính điều phối toàn bộ quá trình."""
    if not compile_code():
        return

    # Xác định danh sách file ảnh để xử lý
    if image_files:
        # Sử dụng file được chỉ định từ command line
        input_images = []
        for img_file in image_files:
            if os.path.exists(img_file):
                input_images.append(img_file)
            else:
                print(f"Warning: File {img_file} không tồn tại. Bỏ qua.")
    else:
        # Tự động tìm tất cả file ảnh
        input_images = glob.glob("input_*.jpg") + glob.glob("*.jpg") + glob.glob("*.png")
    
    if not input_images:
        print("Error: Không tìm thấy file ảnh nào.")
        print("Sử dụng: python run_analysis.py <image1> <image2> ... hoặc đặt các file ảnh có dạng 'input_*.jpg' vào thư mục này.")
        return

    all_results = {}
    plt.figure(figsize=(12, 8)) # Tạo figure cho biểu đồ tổng hợp

    for image_path in sorted(input_images):
        resolution = get_image_resolution(image_path)
        if resolution == "unknown":
            # Nếu không trích xuất được từ tên file, thử lấy kích thước thực tế
            resolution = os.path.basename(image_path).split('.')[0]
        
        print(f"\n--- Analyzing image: {image_path} ({resolution}) ---")

        # --- Chạy bản tuần tự (baseline) ---
        print(f"  Running Baseline ({NUM_RUNS} runs)...")
        baseline_time = run_benchmark(BASELINE_EXE, [image_path])
        if baseline_time is None:
            print(f"  Failed to get baseline time for {image_path}. Skipping.")
            continue
        print(f"  Average sequential time: {baseline_time:.6f}s")

        # --- Chạy bản song song ---
        parallel_times = []
        valid_threads = []
        print(f"  Running Parallel ({NUM_RUNS} runs each)...")
        for p in THREAD_COUNTS:
            print(f"    Testing with {p} threads...")
            avg_time = run_benchmark(PARALLEL_EXE, [image_path, str(p)])
            if avg_time is not None:
                parallel_times.append(avg_time)
                valid_threads.append(p)
        
        if not parallel_times:
            print(f"  No successful parallel runs for {image_path}. Skipping.")
            continue

        # --- Tính toán và lưu kết quả ---
        threads_np = np.array(valid_threads)
        times_np = np.array(parallel_times)
        speedups = baseline_time / times_np
        efficiencies = speedups / threads_np
        
        all_results[image_path] = {
            'baseline_time': baseline_time,
            'threads': threads_np,
            'times': times_np,
            'speedups': speedups,
            'efficiencies': efficiencies
        }

        # Thêm đường speedup vào biểu đồ tổng hợp
        plt.figure(1) # Quay lại figure đã tạo lúc đầu
        plt.plot(threads_np, speedups, 'o-', label=f'Speedup ({resolution})', linewidth=2, markersize=6)

    # --- Hoàn thiện các biểu đồ tổng hợp ---
    if all_results:
        # 1. Biểu đồ so sánh Speedup với đường baseline
        plt.figure(figsize=(12, 8))
        
        for image_path, data in all_results.items():
            resolution = get_image_resolution(image_path)
            if resolution == "unknown":
                resolution = os.path.basename(image_path).split('.')[0]
            threads = data['threads']
            speedups = data['speedups']
            plt.plot(threads, speedups, 'o-', label=f'{resolution}', linewidth=2, markersize=6)
        
        # Vẽ đường baseline (speedup = 1 cho tất cả threads) và đường lý tưởng
        max_threads = max(len(data['threads']) for data in all_results.values())
        ideal_line_threads = THREAD_COUNTS[:max_threads]
        plt.axhline(y=1.0, color='black', linestyle='-', linewidth=3, label='Baseline (Sequential)', alpha=0.8)
        plt.plot(ideal_line_threads, ideal_line_threads, 'r--', label='Ideal Speedup', linewidth=2)
        
        plt.title('Speedup Comparison: Baseline vs Parallel vs Ideal', fontsize=14)
        plt.xlabel('Number of Threads (p)', fontsize=12)
        plt.ylabel('Speedup', fontsize=12)
        plt.grid(True, alpha=0.3); plt.legend(fontsize=11); plt.xticks(THREAD_COUNTS)
        plt.ylim(0, max(ideal_line_threads) * 1.1)
        plt.tight_layout()
        plt.savefig("speedup_comparison.png", dpi=300, bbox_inches='tight')
        print("\nSaved speedup comparison chart to speedup_comparison.png")
        plt.close()

        # 2. Biểu đồ so sánh thời gian thực thi (Baseline vs Parallel)
        plt.figure(figsize=(12, 8))
        
        for image_path, data in all_results.items():
            resolution = get_image_resolution(image_path)
            if resolution == "unknown":
                resolution = os.path.basename(image_path).split('.')[0]
            
            threads = data['threads']
            parallel_times = data['times']
            baseline_time = data['baseline_time']
            
            # Vẽ đường baseline (thời gian tuần tự không đổi)
            plt.axhline(y=baseline_time, linestyle='--', linewidth=2, 
                       label=f'Baseline {resolution}', alpha=0.7)
            
            # Vẽ đường parallel
            plt.plot(threads, parallel_times, 'o-', label=f'Parallel {resolution}', 
                    linewidth=2, markersize=6)
        
        plt.title('Execution Time: Baseline vs Parallel', fontsize=14)
        plt.xlabel('Number of Threads (p)', fontsize=12)
        plt.ylabel('Execution Time (seconds)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=10)
        plt.yscale('log')  # Dùng log scale vì chênh lệch lớn
        plt.xticks(THREAD_COUNTS)
        plt.tight_layout()
        plt.savefig("baseline_vs_parallel_time.png", dpi=300, bbox_inches='tight')
        print("Saved baseline vs parallel time chart to baseline_vs_parallel_time.png")
        plt.close()

        # 3. Biểu đồ so sánh Efficiency
        plt.figure(figsize=(12, 8))
        
        for image_path, data in all_results.items():
            resolution = get_image_resolution(image_path)
            if resolution == "unknown":
                resolution = os.path.basename(image_path).split('.')[0]
            threads = data['threads']
            efficiencies = data['efficiencies']
            plt.plot(threads, efficiencies, 'o-', label=f'{resolution}', linewidth=2, markersize=6)
        
        plt.axhline(y=1.0, color='r', linestyle='--', label='Ideal Efficiency (100%)', linewidth=2)
        plt.title('Efficiency Comparison Across Different Image Sizes', fontsize=14)
        plt.xlabel('Number of Threads (p)', fontsize=12)
        plt.ylabel('Efficiency', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=11)
        plt.ylim(0, 1.1)
        plt.xticks(THREAD_COUNTS)
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0%}'))
        plt.tight_layout()
        plt.savefig("efficiency_comparison.png", dpi=300, bbox_inches='tight')
        print("Saved efficiency comparison chart to efficiency_comparison.png")
        plt.close()

        # 4. Biểu đồ Performance Gain (so sánh trực tiếp baseline vs best parallel)
        plt.figure(figsize=(10, 6))
        
        resolutions = []
        baseline_times = []
        best_parallel_times = []
        speedups = []
        
        for image_path, data in all_results.items():
            resolution = get_image_resolution(image_path)
            if resolution == "unknown":
                resolution = os.path.basename(image_path).split('.')[0]
            
            resolutions.append(resolution)
            baseline_times.append(data['baseline_time'])
            
            # Tìm thời gian parallel tốt nhất
            best_idx = np.argmax(data['speedups'])
            best_parallel_times.append(data['times'][best_idx])
            speedups.append(data['speedups'][best_idx])
        
        x = np.arange(len(resolutions))
        width = 0.35
        
        bars1 = plt.bar(x - width/2, baseline_times, width, label='Baseline (Sequential)', 
                       color='lightcoral', alpha=0.8)
        bars2 = plt.bar(x + width/2, best_parallel_times, width, label='Best Parallel', 
                       color='lightblue', alpha=0.8)
        
        # Thêm text hiển thị speedup trên mỗi cặp bar
        for i, (baseline, parallel, speedup) in enumerate(zip(baseline_times, best_parallel_times, speedups)):
            plt.text(i, max(baseline, parallel) * 1.1, f'{speedup:.1f}x faster', 
                    ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        plt.xlabel('Image Resolution')
        plt.ylabel('Execution Time (seconds)')
        plt.title('Performance Gain: Baseline vs Best Parallel')
        plt.xticks(x, resolutions, rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig("performance_gain.png", dpi=300, bbox_inches='tight')
        print("Saved performance gain chart to performance_gain.png")
        plt.close()

        # Tạo báo cáo
        generate_report(all_results)

        # In tóm tắt kết quả
        print("\n=== TÓM TẮT KẾT QUẢ ===")
        for image_path in sorted(all_results.keys()):
            resolution = get_image_resolution(image_path)
            if resolution == "unknown":
                resolution = os.path.basename(image_path).split('.')[0]
            data = all_results[image_path]
            max_speedup = max(data['speedups'])
            max_efficiency = max(data['efficiencies'])
            print(f"{image_path} ({resolution}): Max Speedup = {max_speedup:.2f}x, Max Efficiency = {max_efficiency:.1%}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Phân tích hiệu năng của thuật toán làm mờ ảnh song song')
    parser.add_argument('images', nargs='*', help='Các file ảnh đầu vào để phân tích')
    parser.add_argument('--runs', '-r', type=int, default=NUM_RUNS, help=f'Số lần chạy để lấy trung bình (mặc định: {NUM_RUNS})')
    parser.add_argument('--threads', '-t', nargs='+', type=int, default=THREAD_COUNTS, help=f'Danh sách số thread để test (mặc định: {THREAD_COUNTS})')
    return parser.parse_args()


if __name__ == "__main__":
    try:
        import matplotlib
        import numpy
    except ImportError:
        print("Error: 'matplotlib' and 'numpy' are required.")
        print("Please install them using: pip install matplotlib numpy")
        sys.exit(1)
    else:
        # Parse arguments
        args = parse_arguments()
        
        # Update global variables if provided
        if args.runs:
            NUM_RUNS = args.runs
        if args.threads:
            THREAD_COUNTS = args.threads

        # Chuyển vào thư mục của script để các đường dẫn tương đối hoạt động đúng
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run main function with specified images
        main(args.images if args.images else None)
