#!/bin/bash

echo "🎯 DEMO: Parallel Image Processing Performance Analysis"
echo "======================================================"

# Demo với tạo ảnh custom
echo "1. Tạo thêm một số ảnh test với kích thước khác nhau..."
python3 create_test_images.py --custom 640x480 1024x768 2560x1560 4096x3072 --pattern colorful

echo ""
echo "2. Chạy phân tích với 4 ảnh..."
python3 run_analysis.py input_640x480.jpg input_1024x768.jpg input_2560x1560.jpg input_4096x3072.jpg --runs 3 --threads 1 2 4 8 10 12

echo ""
echo "📊 Các file kết quả đã được tạo:"
echo "------------------------------"
echo "📋 REPORT.md - Báo cáo chi tiết"
echo "📈 speedup_comparison.png - So sánh speedup (có đường baseline)"
echo "⚡ baseline_vs_parallel_time.png - So sánh thời gian thực thi"
echo "🚀 performance_gain.png - Biểu đồ cải thiện hiệu năng"
echo "📊 efficiency_comparison.png - So sánh efficiency"
echo ""
echo "✨ Demo hoàn tất! Kiểm tra các file để xem kết quả phân tích."