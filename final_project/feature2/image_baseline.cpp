#include <iostream>
#include <vector>
#include <chrono> // Để đo thời gian

// Định nghĩa để STB triển khai các hàm (chỉ làm 1 lần)
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

// Định nghĩa kernel Gaussian Blur 3x3
// Đây là một ma trận trọng số
const double kernel[3][3] = {
    {1.0 / 16, 2.0 / 16, 1.0 / 16},
    {2.0 / 16, 4.0 / 16, 2.0 / 16},
    {1.0 / 16, 2.0 / 16, 1.0 / 16}};

int main() {
    int width, height, channels;

    // 1. Đọc ảnh đầu vào
    // stbi_load trả về con trỏ unsigned char* đến dữ liệu pixel
    unsigned char *img = stbi_load("input.jpg", &width, &height, &channels, 0);
    if (img == NULL) {
        printf("Lỗi: Không thể đọc file ảnh.\n");
        return 1;
    }
    printf("Đã đọc ảnh: %d x %d, %d channels\n", width, height, channels);

    // Kích thước ảnh (tổng số byte)
    size_t img_size = width * height * channels;
    
    // 2. Tạo bộ đệm (buffer) cho ảnh đầu ra
    unsigned char *output_img = (unsigned char *)malloc(img_size);
    if (output_img == NULL) {
        printf("Lỗi: Không thể cấp phát bộ nhớ cho ảnh đầu ra.\n");
        stbi_image_free(img);
        return 1;
    }
    
    // --- BẮT ĐẦU ĐO THỜI GIAN TUẦN TỰ ---
    auto start_time = std::chrono::high_resolution_clock::now();

    // 3. Áp dụng bộ lọc (Phần tính toán chính)
    // Chúng ta duyệt qua từng pixel (trừ các đường viền)
    for (int y = 1; y < height - 1; ++y) {
        for (int x = 1; x < width - 1; ++x) {
            
            // Áp dụng kernel cho từng kênh màu (R, G, B)
            for (int c = 0; c < channels; ++c) {
                double sum = 0.0;
                
                // Vòng lặp 3x3 của kernel
                for (int ky = -1; ky <= 1; ++ky) {
                    for (int kx = -1; kx <= 1; ++kx) {
                        // Lấy pixel gốc
                        unsigned char pixel_val = img[((y + ky) * width + (x + kx)) * channels + c];
                        // Nhân với trọng số kernel
                        sum += pixel_val * kernel[ky + 1][kx + 1];
                    }
                }
                
                // Gán giá trị pixel mới cho ảnh đầu ra
                output_img[(y * width + x) * channels + c] = (unsigned char)sum;
            }
        }
    }

    // --- KẾT THÚC ĐO THỜI GIAN ---
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end_time - start_time;
    printf("%f\n", diff.count());

    // 4. Ghi ảnh ra file
    stbi_write_jpg("output_sequential.jpg", width, height, channels, output_img, 100);

    // 5. Giải phóng bộ nhớ
    stbi_image_free(img);
    free(output_img);

    return 0;
}