CXX = g++-15
CXXFLAGS = -O3 -fopenmp -std=c++11
LDFLAGS = -fopenmp

# Target executables
BASELINE_TARGET = blur_baseline
STATIC_TARGET = blur_static
DYNAMIC_TARGET = blur_dynamic

# Source files
BASELINE_SRC = image_baseline.cpp
STATIC_SRC = image_parallel_static.cpp
DYNAMIC_SRC = image_parallel_dynamic.cpp

# Default target: build all
all: $(BASELINE_TARGET) $(STATIC_TARGET) $(DYNAMIC_TARGET)

# Sequential version
$(BASELINE_TARGET): $(BASELINE_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

# Static scheduling version
$(STATIC_TARGET): $(STATIC_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

# Dynamic scheduling version
$(DYNAMIC_TARGET): $(DYNAMIC_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

# Clean up
clean:
	rm -f $(BASELINE_TARGET) $(STATIC_TARGET) $(DYNAMIC_TARGET) *.jpg

.PHONY: all clean