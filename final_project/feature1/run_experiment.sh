#!/bin/bash

# Script để chạy toàn bộ thực nghiệm phân tích hiệu năng
# với các kích thước ảnh khác nhau

echo "=================================================="
echo "  PARALLEL IMAGE PROCESSING PERFORMANCE ANALYSIS"
echo "=================================================="

# Kiểm tra các dependencies cần thiết
echo "Checking dependencies..."

# Kiểm tra Python và các thư viện
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not installed."
    exit 1
fi

# Kiểm tra numpy và matplotlib
python3 -c "import numpy, matplotlib" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: numpy and matplotlib are required."
    echo "Install them using: pip install numpy matplotlib"
    exit 1
fi

# Kiểm tra PIL cho việc tạo ảnh test
python3 -c "import PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Warning: PIL (Pillow) not found. Cannot create test images."
    echo "Install it using: pip install Pillow"
    echo "Or manually place test images in this directory."
    CREATE_IMAGES=false
else
    CREATE_IMAGES=true
fi

# Kiểm tra file thực thi
if [ ! -f "./blur_baseline" ] || [ ! -f "./blur_parallel" ]; then
    echo "Executable files not found. Trying to compile..."
    if [ ! -f "Makefile" ]; then
        echo "Error: Makefile not found. Cannot compile the project."
        exit 1
    fi
    make clean && make
    if [ $? -ne 0 ]; then
        echo "Error: Compilation failed."
        exit 1
    fi
fi

echo "All dependencies checked successfully!"
echo ""

# Tạo ảnh test nếu có thể
if [ "$CREATE_IMAGES" = true ]; then
    echo "Creating test images..."
    python3 create_test_images.py --pattern gradient
    echo ""
fi

# Kiểm tra xem có file ảnh nào không
IMAGE_FILES=$(ls input_*.jpg 2>/dev/null || ls *.jpg 2>/dev/null || ls *.png 2>/dev/null || true)
if [ -z "$IMAGE_FILES" ]; then
    echo "Error: No image files found."
    echo "Please place test images in this directory or install Pillow to create them."
    exit 1
fi

echo "Found image files:"
for img in $IMAGE_FILES; do
    if [ -f "$img" ]; then
        SIZE=$(ls -lh "$img" | awk '{print $5}')
        echo "  - $img ($SIZE)"
    fi
done
echo ""

# Chạy phân tích
echo "Starting performance analysis..."
echo "This may take several minutes depending on image sizes and number of runs..."
echo ""

# Tùy chọn chạy nhanh hoặc chi tiết
read -p "Quick test (3 runs) or detailed analysis (5 runs)? [q/d]: " TEST_TYPE
case $TEST_TYPE in
    [Dd]* )
        echo "Running detailed analysis (5 runs per test)..."
        python3 run_analysis.py --runs 5
        ;;
    * )
        echo "Running quick test (3 runs per test)..."
        python3 run_analysis.py --runs 3
        ;;
esac

# Kiểm tra kết quả
if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "  ANALYSIS COMPLETED SUCCESSFULLY!"
    echo "=================================================="
    echo ""
    echo "Generated files:"
    
    # Liệt kê các file kết quả
    if [ -f "REPORT.md" ]; then
        echo "  📋 REPORT.md - Detailed analysis report"
    fi
    
    if [ -f "speedup_combined.png" ]; then
        echo "  📊 speedup_combined.png - Combined speedup comparison"
    fi
    
    # Liệt kê biểu đồ cho từng ảnh
    for chart in speedup_*.png efficiency_*.png; do
        if [ -f "$chart" ] && [ "$chart" != "speedup_combined.png" ]; then
            echo "  📈 $chart"
        fi
    done
    
    echo ""
    echo "📖 Open REPORT.md to view detailed analysis results."
    echo "🖼️  View the .png files to see performance charts."
    echo ""
    
    # Hiển thị tóm tắt nếu có
    if [ -f "REPORT.md" ]; then
        echo "Quick summary:"
        echo "----------------------------------------"
        grep -A 20 "Tóm tắt so sánh" REPORT.md | head -n 10 || true
        echo "----------------------------------------"
        echo ""
    fi
    
else
    echo ""
    echo "❌ Analysis failed. Please check error messages above."
    exit 1
fi

# Tùy chọn mở báo cáo
if command -v open &> /dev/null; then
    read -p "Open report file? [y/N]: " OPEN_REPORT
    case $OPEN_REPORT in
        [Yy]* )
            open REPORT.md 2>/dev/null || echo "Could not open report automatically."
            ;;
    esac
fi

echo "Analysis completed! 🎉"