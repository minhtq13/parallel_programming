#include <iostream>
#include <vector>
#include <omp.h> // OpenMP cho xử lý song song

// Thư viện xử lý ảnh
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

// Kernel 5x5 - Cường độ tính toán trung bình (25 phép tính/pixel)
const double kernel_5x5[5][5] = {
    {1.0/273, 4.0/273,  7.0/273,  4.0/273, 1.0/273},
    {4.0/273, 16.0/273, 26.0/273, 16.0/273, 4.0/273},
    {7.0/273, 26.0/273, 41.0/273, 26.0/273, 7.0/273},
    {4.0/273, 16.0/273, 26.0/273, 16.0/273, 4.0/273},
    {1.0/273, 4.0/273,  7.0/273,  4.0/273, 1.0/273}};

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Usage: %s <image_file> <num_threads>\n", argv[0]);
        return 1;
    }
    char* input_filename = argv[1];
    int num_threads = atoi(argv[2]);

    int width, height, channels;
    unsigned char *img = stbi_load(input_filename, &width, &height, &channels, 0);
    if (img == NULL) {
        return 1;
    }
    size_t img_size = width * height * channels;
    unsigned char *output_img = (unsigned char *)malloc(img_size);
    if (output_img == NULL) {
        stbi_image_free(img);
        return 1;
    }

    omp_set_num_threads(num_threads);

    // Bắt đầu đo thời gian
    double start_time = omp_get_wtime();

    // Áp dụng kernel 5x5 song song (bỏ viền 2 pixel)
    #pragma omp parallel for schedule(static) collapse(2)
    for (int y = 2; y < height - 2; ++y) {
        for (int x = 2; x < width - 2; ++x) {
            // Xử lý từng kênh màu
            for (int c = 0; c < channels; ++c) {
                double sum = 0.0;
                // Tính convolution với 25 pixel lân cận
                for (int ky = -2; ky <= 2; ++ky) {
                    for (int kx = -2; kx <= 2; ++kx) {
                        unsigned char pixel_val = img[((y + ky) * width + (x + kx)) * channels + c];
                        sum += pixel_val * kernel_5x5[ky + 2][kx + 2];
                    }
                }
                output_img[(y * width + x) * channels + c] = (unsigned char)sum;
            }
        }
    }

    // Kết thúc đo thời gian và in ra
    double end_time = omp_get_wtime();
    printf("%f\n", (end_time - start_time));

    // Ghi ảnh kết quả
    stbi_write_jpg("output_5x5.jpg", width, height, channels, output_img, 100);

    // Giải phóng bộ nhớ
    stbi_image_free(img);
    free(output_img);

    return 0;
}