#include <iostream>
#include <vector>
#include <omp.h> // OpenMP cho xử lý song song

// Thư viện xử lý ảnh
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

const double kernel[3][3] = {
    {1.0 / 16, 2.0 / 16, 1.0 / 16},
    {2.0 / 16, 4.0 / 16, 2.0 / 16},
    {1.0 / 16, 2.0 / 16, 1.0 / 16}};

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

    // Static scheduling: chia đều công việc cho các luồng ngay từ đầu
    #pragma omp parallel for schedule(static) collapse(2)
    for (int y = 1; y < height - 1; ++y) {
        for (int x = 1; x < width - 1; ++x) {
            // Xử lý từng kênh màu
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
    double end_time = omp_get_wtime();
    printf("%f\n", (end_time - start_time));

    // Ghi ảnh kết quả
    stbi_write_jpg("output_static.jpg", width, height, channels, output_img, 100);

    // Giải phóng bộ nhớ
    stbi_image_free(img);
    free(output_img);

    return 0;
}