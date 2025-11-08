#!/usr/bin/env python3
"""
Script để tạo các file ảnh test với kích thước khác nhau cho thực nghiệm.
Tạo ảnh với các độ phân giải khác nhau để test hiệu năng song song.
"""

import numpy as np
from PIL import Image
import os
import argparse

def create_test_image(width, height, filename, pattern='gradient'):
    """
    Tạo một ảnh test với kích thước và pattern chỉ định.
    
    Args:
        width (int): Chiều rộng ảnh
        height (int): Chiều cao ảnh  
        filename (str): Tên file đầu ra
        pattern (str): Loại pattern ('gradient', 'noise', 'checkerboard')
    """
    print(f"Creating {width}x{height} image: {filename}")
    
    if pattern == 'gradient':
        # Tạo gradient từ đen đến trắng
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(height):
            for j in range(width):
                # Gradient theo đường chéo
                value = int(255 * ((i + j) / (height + width - 2)))
                img_array[i, j] = [value, value, value]
                
    elif pattern == 'noise':
        # Tạo noise ngẫu nhiên
        img_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        
    elif pattern == 'checkerboard':
        # Tạo bàn cờ
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        block_size = min(32, width//8, height//8)  # Kích thước ô vuông
        for i in range(height):
            for j in range(width):
                if ((i // block_size) + (j // block_size)) % 2 == 0:
                    img_array[i, j] = [255, 255, 255]  # Trắng
                else:
                    img_array[i, j] = [0, 0, 0]        # Đen
                    
    elif pattern == 'colorful':
        # Tạo ảnh màu sắc phong phú
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(height):
            for j in range(width):
                r = int(255 * (i / height))
                g = int(255 * (j / width))
                b = int(255 * ((i + j) / (height + width)))
                img_array[i, j] = [r, g, b]
    else:
        raise ValueError(f"Unknown pattern: {pattern}")
    
    # Chuyển đổi thành ảnh PIL và lưu
    image = Image.fromarray(img_array, 'RGB')
    image.save(filename, 'JPEG', quality=95)
    
    # In kích thước file
    file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
    print(f"  Saved: {filename} ({file_size:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(description='Tạo các file ảnh test với kích thước khác nhau')
    parser.add_argument('--pattern', choices=['gradient', 'noise', 'checkerboard', 'colorful'], 
                       default='gradient', help='Pattern cho ảnh test')
    parser.add_argument('--custom', nargs='+', help='Kích thước custom theo format WIDTHxHEIGHT (vd: 1920x1080)')
    
    args = parser.parse_args()
    
    # Các kích thước ảnh chuẩn để test
    standard_sizes = [
        (640, 480, "input_640x480.jpg"),     # VGA - ảnh rất nhỏ
        (1024, 768, "input_1024x768.jpg"),  # XGA - ảnh nhỏ
        (2560, 1560, "input_2560x1560.jpg"), # 2.5K - ảnh lớn
        (4096, 3072, "input_4096x3072.jpg") # 4K+ - ảnh rất lớn
    ]
    
    print(f"Creating test images with pattern: {args.pattern}")
    print("=" * 50)
    
    # Tạo ảnh chuẩn
    for width, height, filename in standard_sizes:
        create_test_image(width, height, filename, args.pattern)
    
    # Tạo ảnh custom nếu có
    if args.custom:
        print("\nCreating custom size images:")
        for size_str in args.custom:
            try:
                width_str, height_str = size_str.split('x')
                width, height = int(width_str), int(height_str)
                filename = f"input_{width}x{height}.jpg"
                create_test_image(width, height, filename, args.pattern)
            except ValueError:
                print(f"Error: Invalid size format '{size_str}'. Use WIDTHxHEIGHT format.")
    
    print("\n" + "=" * 50)
    print("All test images created successfully!")
    print("You can now run:")
    print("  python run_analysis.py                    # Test all images")
    print("  python run_analysis.py input_*.jpg        # Test specific images")
    print("  python run_analysis.py --runs 5 input_1920x1080.jpg  # Custom settings")


if __name__ == "__main__":
    try:
        import PIL
    except ImportError:
        print("Error: PIL (Pillow) is required.")
        print("Install it using: pip install Pillow")
        exit(1)
    
    main()