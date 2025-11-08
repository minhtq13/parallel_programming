CXX = g++-15
CXXFLAGS = -O3 -fopenmp -std=c++11
LDFLAGS = -fopenmp

# Target executables
BASELINE_TARGET = blur_baseline
KERNEL_3X3_TARGET = blur_3x3
KERNEL_5X5_TARGET = blur_5x5
KERNEL_7X7_TARGET = blur_7x7

# Source files
BASELINE_SRC = image_baseline.cpp
KERNEL_3X3_SRC = image_parallel_3x3.cpp
KERNEL_5X5_SRC = image_parallel_5x5.cpp
KERNEL_7X7_SRC = image_parallel_7x7.cpp

# Default target: build all
all: $(BASELINE_TARGET) $(KERNEL_3X3_TARGET) $(KERNEL_5X5_TARGET) $(KERNEL_7X7_TARGET)

# Sequential version
$(BASELINE_TARGET): $(BASELINE_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

# 3x3 kernel version
$(KERNEL_3X3_TARGET): $(KERNEL_3X3_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

# 5x5 kernel version
$(KERNEL_5X5_TARGET): $(KERNEL_5X5_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

# 7x7 kernel version
$(KERNEL_7X7_TARGET): $(KERNEL_7X7_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

# Clean up
clean:
	rm -f $(BASELINE_TARGET) $(KERNEL_3X3_TARGET) $(KERNEL_5X5_TARGET) $(KERNEL_7X7_TARGET) *.jpg

.PHONY: all clean