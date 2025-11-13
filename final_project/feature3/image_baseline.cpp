#include <iostream>
#include <vector>
#include <chrono> // Đo thời gian

// Thư viện xử lý ảnh
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

// Bộ lọc Gaussian 3x3 để làm mờ ảnh
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
    
    // Bắt đầu đo thời gian
    auto start_time = std::chrono::high_resolution_clock::now();

    // Áp dụng bộ lọc tuần tự (bỏ viền 1 pixel)
    for (int y = 1; y < height - 1; ++y) {
        for (int x = 1; x < width - 1; ++x) {
            // Xử lý từng kênh màu (R, G, B)
            for (int c = 0; c < channels; ++c) {
                double sum = 0.0;
                // Tính convolution với 9 pixel lân cận
                for (int ky = -1; ky <= 1; ++ky) {
                    for (int kx = -1; kx <= 1; ++kx) {
                        unsigned char pixel_val = img[((y + ky) * width + (x + kx)) * channels + c];
                        sum += pixel_val * kernel[ky + 1][kx + 1];
                    }
                }
                output_img[(y * width + x) * channels + c] = (unsigned char)sum;
            }
        }
    }

    // Kết thúc đo thời gian và in ra
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end_time - start_time;
    printf("%f\n", diff.count());

    // Ghi ảnh kết quả
    stbi_write_jpg("output_sequential.jpg", width, height, channels, output_img, 100);

    // Giải phóng bộ nhớ
    stbi_image_free(img);
    free(output_img);

    return 0;
}