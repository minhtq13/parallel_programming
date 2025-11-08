#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>
#include <omp.h>

using namespace std;

void parallelBubbleSort(vector<int>& a) {
    int n = a.size();
    int temp;
    // Lặp qua tất cả các phần tử
    for (int i = 0; i < n - 1; i++) {
        int first = i % 2; // Quyết định lượt chẵn/lẻ
        #pragma omp parallel for private(temp) shared(a, n, first)
        for (int j = first; j < n - 1; j += 2) {
            if (a[j] > a[j + 1]) {
                swap(a[j], a[j + 1]); // Sử dụng std::swap
            }
        }
    }
}

int main() {
    vector<int> a = {9, 4, 7, 3, 1, 8, 5, 2, 10, 6};
    
    cout << "Mang truoc khi sap xep:" << endl;
    for (int x : a) {
        cout << x << " ";
    }
    cout << endl;

    auto start = chrono::high_resolution_clock::now();
    parallelBubbleSort(a);
    auto end = chrono::high_resolution_clock::now();
    
    auto duration = chrono::duration_cast<chrono::microseconds>(end - start);
    
    cout << "Mang sau khi sap xep:" << endl;
    for (int x : a) {
        cout << x << " ";
    }
    cout << endl;

    cout << "Thoi gian thuc thi: " << duration.count() << " microseconds" << endl;
    cout << "Thoi gian thuc thi: " << duration.count() / 1000000.0 << " giay" << endl;
    
    return 0;
}
