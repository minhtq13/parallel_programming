import subprocess
import numpy as np
import matplotlib.pyplot as plt
import os

# --- Cấu hình thực nghiệm ---
NUM_RUNS = 5  # Số lần chạy mỗi cấu hình để lấy trung bình
THREAD_COUNTS = [1, 2, 4, 8, 10, 12]  # Các số luồng cần kiểm tra
BASELINE_EXE = "./blur_baseline"
PARALLEL_EXE = "./blur_parallel"
RESULTS_FILE = "results.dat"
SPEEDUP_CHART_FILE = "speedup_chart.png"
EFFICIENCY_CHART_FILE = "efficiency_chart.png"

def compile_code():
    """Biên dịch code C++ bằng Makefile."""
    print("--- Compiling C++ code ---")
    try:
        # Chạy 'make clean' và 'make'
        subprocess.run(["make", "clean"], check=True, capture_output=True, text=True)
        result = subprocess.run(["make"], check=True, capture_output=True, text=True)
        print("Compilation successful.")
        return True
    except FileNotFoundError:
        print("Error: 'make' command not found. Please ensure make is installed.")
        return False
    except subprocess.CalledProcessError as e:
        print("Error during compilation:")
        print(e.stderr)
        return False

def check_input_image():
    """Kiểm tra sự tồn tại của input.jpg, nếu không có thì tạo ảnh giả."""
    if not os.path.exists("input.jpg"):
        print("Warning: input.jpg not found. Creating a dummy 1920x1080 image.")
        try:
            # Sử dụng ImageMagick để tạo ảnh
            subprocess.run(
                ["convert", "-size", "1920x1080", "xc:white", "input.jpg"],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(
                "Error: Failed to create a dummy image. "
                "Please provide an 'input.jpg' file or install ImageMagick ('convert' command)."
            )
            return False
    return True

def run_benchmark(executable, args=[]):
    """Chạy một file thực thi nhiều lần và trả về thời gian trung bình."""
    timings = []
    for _ in range(NUM_RUNS):
        try:
            result = subprocess.run(
                [executable] + args, check=True, capture_output=True, text=True
            )
            # Lấy dòng output cuối cùng chứa thời gian
            time_str = result.stdout.strip().split('\n')[-1]
            timings.append(float(time_str))
        except (subprocess.CalledProcessError, ValueError, IndexError) as e:
            print(f"Error running {executable} with args {args}: {e}")
            if hasattr(e, 'stderr'):
                print(e.stderr)
            return None
    return np.mean(timings) if timings else None

def main():
    """Hàm chính điều phối toàn bộ quá trình."""
    if not compile_code():
        return
    if not check_input_image():
        return

    # --- Chạy bản tuần tự (baseline) ---
    print(f"\n--- Running Baseline ({NUM_RUNS} runs) ---")
    baseline_time = run_benchmark(BASELINE_EXE)
    if baseline_time is None:
        print("Failed to get baseline time. Exiting.")
        return
    print(f"Average sequential time: {baseline_time:.6f}s")

    parallel_times = []
    print(f"\n--- Running Parallel ({NUM_RUNS} runs for each thread count) ---")
    for p in THREAD_COUNTS:
        print(f"Testing with {p} threads...")
        avg_time = run_benchmark(PARALLEL_EXE, [str(p)])
        if avg_time is None:
            print(f"Failed for {p} threads. Skipping.")
            continue
        parallel_times.append(avg_time)
        print(f"  Average time: {avg_time:.6f}s")

    # --- Xử lý dữ liệu và tính toán ---
    # Chuyển đổi sang numpy array để tính toán dễ dàng
    thread_counts_np = np.array(THREAD_COUNTS[:len(parallel_times)])
    parallel_times_np = np.array(parallel_times)

    speedup = baseline_time / parallel_times_np
    efficiency = speedup / thread_counts_np

    # --- In kết quả ra màn hình ---
    print("\n--- Benchmark Results ---")
    print(f"{'Threads':<10} {'Time (s)':<15} {'Speedup':<15} {'Efficiency':<15}")
    print("-" * 55)
    print(f"{'1 (Seq)':<10} {baseline_time:<15.6f} {'1.00x':<15} {'1.00':<15}")
    for i, p in enumerate(thread_counts_np):
        print(f"{p:<10} {parallel_times_np[i]:<15.6f} {speedup[i]:<15.2f}x {efficiency[i]:<15.2%}")

    # --- Vẽ biểu đồ ---
    print(f"\n--- Generating charts ---")

    # 1. Biểu đồ Tăng tốc (Speedup)
    plt.figure(figsize=(10, 6))
    plt.plot(thread_counts_np, speedup, 'o-', label='Actual Speedup')
    plt.plot(thread_counts_np, thread_counts_np, 'r--', label='Ideal Speedup')
    plt.title('Speedup vs. Number of Threads')
    plt.xlabel('Number of Threads (p)')
    plt.ylabel('Speedup (Sequential Time / Parallel Time)')
    plt.grid(True)
    plt.legend()
    plt.xticks(thread_counts_np)
    plt.savefig(SPEEDUP_CHART_FILE)
    print(f"Saved speedup chart to {SPEEDUP_CHART_FILE}")

    # 2. Biểu đồ Hiệu suất (Efficiency)
    plt.figure(figsize=(10, 6))
    plt.plot(thread_counts_np, efficiency, 'o-', label='Actual Efficiency')
    plt.axhline(y=1.0, color='r', linestyle='--', label='Ideal Efficiency (100%)')
    plt.title('Efficiency vs. Number of Threads')
    plt.xlabel('Number of Threads (p)')
    plt.ylabel('Efficiency (Speedup / p)')
    plt.grid(True)
    plt.legend()
    plt.xticks(thread_counts_np)
    plt.ylim(0, 1.1) # Giới hạn trục Y từ 0 đến 110%
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter('{:.0%}'.format)) # Format Y axis as percentage
    plt.savefig(EFFICIENCY_CHART_FILE)
    print(f"Saved efficiency chart to {EFFICIENCY_CHART_FILE}")


if __name__ == "__main__":
    # Kiểm tra thư viện cần thiết
    try:
        import matplotlib
        import numpy
    except ImportError:
        print("Error: 'matplotlib' and 'numpy' are required.")
        print("Please install them using: pip install matplotlib numpy")
    else:
        main()
