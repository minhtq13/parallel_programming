#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>
#include <random>
#include <iomanip>
#include <omp.h>
#include <string>
#include <functional>

using namespace std;

// ==================== BUBBLE SORT ====================
void sequentialBubbleSort(vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                swap(arr[j], arr[j + 1]);
            }
        }
    }
}

void parallelBubbleSort(vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        int first = i % 2;
        #pragma omp parallel for shared(arr, n, first)
        for (int j = first; j < n - 1; j += 2) {
            if (arr[j] > arr[j + 1]) {
                swap(arr[j], arr[j + 1]);
            }
        }
    }
}

// ==================== MERGE SORT ====================
void merge(vector<int>& arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    
    vector<int> L(n1), R(n2);
    
    for (int i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (int j = 0; j < n2; j++)
        R[j] = arr[mid + 1 + j];
    
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
    
    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }
    
    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }
}

void sequentialMergeSortHelper(vector<int>& arr, int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        sequentialMergeSortHelper(arr, left, mid);
        sequentialMergeSortHelper(arr, mid + 1, right);
        merge(arr, left, mid, right);
    }
}

void parallelMergeSortHelper(vector<int>& arr, int left, int right, int depth = 0) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        
        if (depth < 3) {
            #pragma omp parallel sections
            {
                #pragma omp section
                {
                    parallelMergeSortHelper(arr, left, mid, depth + 1);
                }
                #pragma omp section
                {
                    parallelMergeSortHelper(arr, mid + 1, right, depth + 1);
                }
            }
        } else {
            sequentialMergeSortHelper(arr, left, mid);
            sequentialMergeSortHelper(arr, mid + 1, right);
        }
        
        merge(arr, left, mid, right);
    }
}

void sequentialMergeSort(vector<int>& arr) {
    sequentialMergeSortHelper(arr, 0, arr.size() - 1);
}

void parallelMergeSort(vector<int>& arr) {
    parallelMergeSortHelper(arr, 0, arr.size() - 1, 0);
}

// ==================== QUICK SORT ====================
int partition(vector<int>& arr, int low, int high) {
    int pivot = arr[high];
    int i = (low - 1);
    
    for (int j = low; j <= high - 1; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i + 1], arr[high]);
    return (i + 1);
}

void sequentialQuickSortHelper(vector<int>& arr, int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        sequentialQuickSortHelper(arr, low, pi - 1);
        sequentialQuickSortHelper(arr, pi + 1, high);
    }
}

void parallelQuickSortHelper(vector<int>& arr, int low, int high, int depth = 0) {
    if (low < high) {
        int pi = partition(arr, low, high);
        
        if (depth < 3) {
            #pragma omp parallel sections
            {
                #pragma omp section
                {
                    parallelQuickSortHelper(arr, low, pi - 1, depth + 1);
                }
                #pragma omp section
                {
                    parallelQuickSortHelper(arr, pi + 1, high, depth + 1);
                }
            }
        } else {
            sequentialQuickSortHelper(arr, low, pi - 1);
            sequentialQuickSortHelper(arr, pi + 1, high);
        }
    }
}

void sequentialQuickSort(vector<int>& arr) {
    sequentialQuickSortHelper(arr, 0, arr.size() - 1);
}

void parallelQuickSort(vector<int>& arr) {
    parallelQuickSortHelper(arr, 0, arr.size() - 1, 0);
}

// ==================== UTILITY FUNCTIONS ====================
bool isSorted(const vector<int>& arr) {
    for (size_t i = 0; i < arr.size() - 1; i++) {
        if (arr[i] > arr[i + 1]) {
            return false;
        }
    }
    return true;
}

void generateRandomArray(vector<int>& arr, int n, int seed = 42) {
    arr.resize(n);
    mt19937 rng(seed);
    uniform_int_distribution<int> dist(0, 9999);
    for (int i = 0; i < n; i++) {
        arr[i] = dist(rng);
    }
}

// Struct để lưu kết quả test
struct TestResult {
    string algorithm;
    string type;
    double time_seconds;
    bool correct;
    double speedup;
};

// Hàm test một thuật toán
TestResult testAlgorithm(const string& name, const string& type, 
                        function<void(vector<int>&)> sortFunc, 
                        const vector<int>& originalArr) {
    vector<int> arr = originalArr;  // Copy mảng để test
    auto start = chrono::high_resolution_clock::now();
    sortFunc(arr);
    auto end = chrono::high_resolution_clock::now();
    
    auto duration = chrono::duration_cast<chrono::microseconds>(end - start);
    double time_sec = duration.count() / 1000000.0;
    
    return {name, type, time_sec, isSorted(arr), 0.0};
}

int main() {
    vector<int> sizes = {1000, 5000, 10000, 20000};
    
    cout << "========================================" << endl;
    cout << "    SO SÁNH CÁC THUẬT TOÁN SẮP XẾP" << endl;
    cout << "========================================" << endl;
    cout << "Số threads OpenMP: " << omp_get_max_threads() << endl;
    cout << "Các thuật toán: Bubble Sort, Merge Sort, Quick Sort" << endl;
    cout << "Mỗi thuật toán có 2 phiên bản: Sequential và Parallel" << endl;
    cout << "========================================" << endl << endl;
    
    for (int size : sizes) {
        cout << "🔍 TESTING VỚI KÍCH THƯỚC: " << size << " phần tử" << endl;
        cout << "----------------------------------------" << endl;
        
        // Tạo mảng test
        vector<int> originalArr;
        generateRandomArray(originalArr, size, 42);
        
        vector<TestResult> results;
        
        // Test tất cả thuật toán
        results.push_back(testAlgorithm("Bubble Sort", "Sequential", sequentialBubbleSort, originalArr));
        results.push_back(testAlgorithm("Bubble Sort", "Parallel", parallelBubbleSort, originalArr));
        results.push_back(testAlgorithm("Merge Sort", "Sequential", sequentialMergeSort, originalArr));
        results.push_back(testAlgorithm("Merge Sort", "Parallel", parallelMergeSort, originalArr));
        results.push_back(testAlgorithm("Quick Sort", "Sequential", sequentialQuickSort, originalArr));
        results.push_back(testAlgorithm("Quick Sort", "Parallel", parallelQuickSort, originalArr));
        
        // Tính speedup cho parallel versions
        for (int i = 1; i < results.size(); i += 2) {
            results[i].speedup = results[i-1].time_seconds / results[i].time_seconds;
        }
        
        // In kết quả dạng bảng
        cout << left << setw(15) << "Thuật toán" 
             << setw(12) << "Loại" 
             << setw(12) << "Thời gian(s)" 
             << setw(10) << "Đúng" 
             << setw(10) << "Speedup" << endl;
        cout << string(60, '-') << endl;
        
        for (const auto& result : results) {
            cout << left << setw(15) << result.algorithm
                 << setw(12) << result.type
                 << setw(12) << fixed << setprecision(6) << result.time_seconds
                 << setw(10) << (result.correct ? "✓" : "✗");
            
            if (result.type == "Parallel") {
                cout << setw(10) << fixed << setprecision(2) << result.speedup << "x";
            } else {
                cout << setw(10) << "-";
            }
            cout << endl;
        }
        
        // Tìm thuật toán nhanh nhất
        auto fastest = min_element(results.begin(), results.end(), 
            [](const TestResult& a, const TestResult& b) {
                return a.time_seconds < b.time_seconds;
            });
        
        cout << "\n🏆 Nhanh nhất: " << fastest->algorithm << " (" << fastest->type << ") - " 
             << fixed << setprecision(6) << fastest->time_seconds << "s" << endl;
        
        cout << "\n📊 Nhận xét:" << endl;
        cout << "• Bubble Sort: Chậm nhất, parallel không hiệu quả" << endl;
        cout << "• Merge Sort: Ổn định, parallel hiệu quả với mảng lớn" << endl;
        cout << "• Quick Sort: Nhanh nhất trung bình, parallel tốt" << endl;
        
        cout << "\n" << string(60, '=') << endl << endl;
    }
    
    return 0;
}