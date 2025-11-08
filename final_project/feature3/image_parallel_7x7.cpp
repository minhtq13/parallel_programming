#include <iostream>
#include <vector>
#include <omp.h>

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

// Kernel 7x7 Gaussian Blur (cường độ tính toán cao)
const double kernel_7x7[7][7] = {
    {0.00000067, 0.00002292, 0.00019117, 0.00038771, 0.00019117, 0.00002292, 0.00000067},
    {0.00002292, 0.00078633, 0.00655965, 0.01330373, 0.00655965, 0.00078633, 0.00002292},
    {0.00019117, 0.00655965, 0.05472157, 0.11098164, 0.05472157, 0.00655965, 0.00019117},
    {0.00038771, 0.01330373, 0.11098164, 0.22508352, 0.11098164, 0.01330373, 0.00038771},
    {0.00019117, 0.00655965, 0.05472157, 0.11098164, 0.05472157, 0.00655965, 0.00019117},
    {0.00002292, 0.00078633, 0.00655965, 0.01330373, 0.00655965, 0.00078633, 0.00002292},
    {0.00000067, 0.00002292, 0.00019117, 0.00038771, 0.00019117, 0.00002292, 0.00000067}};

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

    double start_time = omp_get_wtime();

    // Áp dụng kernel 7x7 - Cường độ tính toán: 49 phép nhân + 49 phép cộng mỗi pixel
    #pragma omp parallel for schedule(static) collapse(2)
    for (int y = 3; y < height - 3; ++y) {
        for (int x = 3; x < width - 3; ++x) {
            for (int c = 0; c < channels; ++c) {
                double sum = 0.0;
                for (int ky = -3; ky <= 3; ++ky) {
                    for (int kx = -3; kx <= 3; ++kx) {
                        unsigned char pixel_val = img[((y + ky) * width + (x + kx)) * channels + c];
                        sum += pixel_val * kernel_7x7[ky + 3][kx + 3];
                    }
                }
                output_img[(y * width + x) * channels + c] = (unsigned char)sum;
            }
        }
    }

    double end_time = omp_get_wtime();
    printf("%f\n", (end_time - start_time));

    stbi_write_jpg("output_7x7.jpg", width, height, channels, output_img, 100);

    stbi_image_free(img);
    free(output_img);

    return 0;
}