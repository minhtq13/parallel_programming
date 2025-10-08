# Parallel Programming with C++

## Cách compile file C++

### Compile file C++ thông thường:

```bash
g++ -o output_file source_file.cpp -std=c++17
```

### Compile file C++ với OpenMP (parallel):

```bash
/opt/homebrew/bin/g++-15 -o output_file source_file.cpp -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib -std=c++17
```

### Ví dụ:

# Parallel Programming with C++

## 🚀 Các Thuật Toán Sắp Xếp Parallel

### 📊 Thuật toán được implement:

- **Bubble Sort**: Sequential vs Parallel
- **Merge Sort**: Sequential vs Parallel (Divide & Conquer)
- **Quick Sort**: Sequential vs Parallel (Divide & Conquer)

## 🔧 Cách compile file C++

### Compile file C++ thông thường:

```bash
g++ -o output_file source_file.cpp -std=c++17
```

### Compile file C++ với OpenMP (parallel):

```bash
/opt/homebrew/bin/g++-15 -o output_file source_file.cpp -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib -std=c++17
```

### Ví dụ compile các file:

```bash
# Bubble Sort basic
/opt/homebrew/bin/g++-15 -o bubble_sort bubbleSort.cpp -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib -std=c++17


# Merge Sort
/opt/homebrew/bin/g++-15 -o merge_sort merge_sort.cpp -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib -std=c++17

# So sánh tất cả thuật toán
/opt/homebrew/bin/g++-15 -o comparison_sorts comparison_sorts.cpp -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib -std=c++17

# Run
./bubble_sort
./merge_sort
./comparison_sorts
```

## 📁 Các file trong project:

- `bubble_sort.cpp` - Bubble sort với OpenMP parallel
- `merge_sort.cpp` - Merge sort với OpenMP parallel
- `comparison_sorts.cpp` - **So sánh tất cả thuật toán sắp xếp**

## 🏆 Kết quả Performance (20,000 phần tử):

| Thuật toán      | Sequential | Parallel | Speedup | Nhận xét               |
| --------------- | ---------- | -------- | ------- | ---------------------- |
| **Bubble Sort** | 1.614s     | 1.189s   | 1.36x   | Chậm nhất, ít hiệu quả |
| **Merge Sort**  | 0.007s     | 0.004s   | 1.88x   | Ổn định, hiệu quả      |
| **Quick Sort**  | 0.003s     | 0.002s   | 1.47x   | **Nhanh nhất!**        |
