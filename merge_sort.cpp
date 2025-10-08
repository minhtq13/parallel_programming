#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>
#include <omp.h>

using namespace std;

// Hàm merge cho merge sort
void merge(vector<int>& arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    
    // Tạo temporary arrays
    vector<int> L(n1), R(n2);
    
    // Copy data vào temporary arrays
    for (int i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (int j = 0; j < n2; j++)
        R[j] = arr[mid + 1 + j];
    
    // Merge temporary arrays back vào arr[left..right]
    int i = 0, j = 0, k = left;
    
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        } else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }
    
    // Copy remaining elements của L[]
    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }
    
    // Copy remaining elements của R[]
    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }
}

// Sequential Merge Sort
void sequentialMergeSort(vector<int>& arr, int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        
        sequentialMergeSort(arr, left, mid);
        sequentialMergeSort(arr, mid + 1, right);
        
        merge(arr, left, mid, right);
    }
}

// Parallel Merge Sort với OpenMP
void parallelMergeSort(vector<int>& arr, int left, int right, int depth = 0) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        
        // Sử dụng parallel chỉ khi depth nhỏ để tránh tạo quá nhiều threads
        if (depth < 3) {  // Giới hạn độ sâu để tránh overhead
            #pragma omp parallel sections
            {
                #pragma omp section
                {
                    parallelMergeSort(arr, left, mid, depth + 1);
                }
                #pragma omp section  
                {
                    parallelMergeSort(arr, mid + 1, right, depth + 1);
                }
            }
        } else {
            // Chuyển về sequential khi quá sâu
            sequentialMergeSort(arr, left, mid);
            sequentialMergeSort(arr, mid + 1, right);
        }
        
        merge(arr, left, mid, right);
    }
}

// Wrapper functions
void sequentialMergeSort(vector<int>& arr) {
    sequentialMergeSort(arr, 0, arr.size() - 1);
}

void parallelMergeSort(vector<int>& arr) {
    parallelMergeSort(arr, 0, arr.size() - 1, 0);
}

// Hàm kiểm tra mảng đã sắp xếp
bool isSorted(const vector<int>& arr) {
    for (size_t i = 0; i < arr.size() - 1; i++) {
        if (arr[i] > arr[i + 1]) {
            return false;
        }
    }
    return true;
}

// Hàm in mảng
void printArray(const vector<int>& arr) {
    for (int x : arr) {
        cout << x << " ";
    }
    cout << endl;
}

int main() {
    vector<int> arr = {38, 27, 43, 3, 9, 82, 10, 1, 15, 25};
    
    cout << "=== MERGE SORT DEMONSTRATION ===" << endl;
    cout << "Số threads OpenMP: " << omp_get_max_threads() << endl;
    
    cout << "\nMảng ban đầu:" << endl;
    printArray(arr);
    
    // Test Sequential Merge Sort
    vector<int> arr1 = arr;
    auto start = chrono::high_resolution_clock::now();
    sequentialMergeSort(arr1);
    auto end = chrono::high_resolution_clock::now();
    auto duration = chrono::duration_cast<chrono::microseconds>(end - start);
    
    cout << "\nSequential Merge Sort:" << endl;
    cout << "Kết quả: ";
    printArray(arr1);
    cout << "Thời gian: " << duration.count() << " microseconds" << endl;
    cout << "Đã sắp xếp đúng: " << (isSorted(arr1) ? "Có" : "Không") << endl;
    
    // Test Parallel Merge Sort
    vector<int> arr2 = arr;
    start = chrono::high_resolution_clock::now();
    parallelMergeSort(arr2);
    end = chrono::high_resolution_clock::now();
    duration = chrono::duration_cast<chrono::microseconds>(end - start);
    
    cout << "\nParallel Merge Sort:" << endl;
    cout << "Kết quả: ";
    printArray(arr2);
    cout << "Thời gian: " << duration.count() << " microseconds" << endl;
    cout << "Đã sắp xếp đúng: " << (isSorted(arr2) ? "Có" : "Không") << endl;
    
    // Kiểm tra hai kết quả có giống nhau không
    cout << "\nKết quả hai thuật toán: " << (arr1 == arr2 ? "Giống nhau" : "Khác nhau") << endl;
    
    return 0;
}
