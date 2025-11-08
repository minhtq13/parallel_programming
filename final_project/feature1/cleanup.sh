#!/bin/bash

echo "🧹 Cleaning up old test images and results..."

# Xóa các ảnh cũ (không phải 4 ảnh mục tiêu)
echo "Removing old image files..."
rm -f input_800x600.jpg input_1920x1080.jpg input_2560x1440.jpg input_3840x2160.jpg
rm -f input_large_4k.jpg input_small_640x480.jpg
rm -f *.jpg 2>/dev/null || true

# Xóa các kết quả cũ
echo "Removing old result files..."
rm -f *.png REPORT.md output_*.jpg

echo "✅ Cleanup completed!"
echo ""
echo "Now run: python3 create_test_images.py"
echo "Then run: python3 run_analysis.py"