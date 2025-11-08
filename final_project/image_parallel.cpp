#include <iostream>
#include <vector>
// #include <chrono> // Không dùng chrono nữa
#include <omp.h> // 1. Thêm thư viện OpenMP

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

// 1. Định nghĩa kernel (bộ lọc)
const double kernel[3][3] = {
    {1.0 / 16, 2.0 / 16, 1.0 / 16},
    {2.0 / 16, 4.0 / 16, 2.0 / 16},
    {1.0 / 16, 2.0 / 16, 1.0 / 16}};

int main(int argc, char *argv[]) {
    int width, height, channels;
    unsigned char *img = stbi_load("input.jpg", &width, &height, &channels, 0);
    if (img == NULL) {
        printf("Lỗi: Không thể mở file input.jpg\n");
        return 1;
    }
    size_t img_size = width * height * channels;
    unsigned char *output_img = (unsigned char *)malloc(img_size);
    if (output_img == NULL) {
        printf("Lỗi: Không thể cấp phát bộ nhớ cho ảnh output.\n");
        stbi_image_free(img);
        return 1;
    }

    // Lấy số luồng từ tham số dòng lệnh, mặc định là 4 nếu không có
    int num_threads = 4;
    if (argc > 1) {
        num_threads = atoi(argv[1]);
    }
    omp_set_num_threads(num_threads);
    printf("Chạy song song với %d luồng...\n", num_threads);

    // --- BẮT ĐẦU ĐO THỜI GIAN SONG SONG ---
    double start_time = omp_get_wtime(); // 2. Dùng hàm của OpenMP

    // 3. Áp dụng bộ lọc (Phần tính toán chính)
    
    // 3. THAY ĐỔI DUY NHẤT LÀ DÒNG NÀY!
    #pragma omp parallel for schedule(static) collapse(2)
    for (int y = 1; y < height - 1; ++y) {
        for (int x = 1; x < width - 1; ++x) {
            
            // ... (Phần code bên trong vòng lặp giữ nguyên y hệt) ...
            for (int c = 0; c < channels; ++c) {
                double sum = 0.0;
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

    // --- KẾT THÚC ĐO THỜI GIAN ---
    double end_time = omp_get_wtime(); // 4. Dùng hàm của OpenMP
    printf("%f\n", (end_time - start_time));

    // 4. Ghi ảnh ra file
    stbi_write_jpg("output_parallel.jpg", width, height, channels, output_img, 100);

    // 5. Giải phóng bộ nhớ
    stbi_image_free(img);
    free(output_img);

    return 0;
}