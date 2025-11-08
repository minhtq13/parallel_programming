# Compiler
# On macOS, install gcc with Homebrew: `brew install gcc`
# Then use g++-13 (or your installed version)
CXX = g++-15
# Compiler flags
CXXFLAGS = -Wall -O3
# OpenMP flag
OMPFLAGS = -fopenmp

# Target executables
SEQ_TARGET = blur_baseline
PARA_TARGET = blur_parallel

.PHONY: all clean

# Default rule
all: $(SEQ_TARGET) $(PARA_TARGET)

# Rule to build the sequential version
$(SEQ_TARGET): image_baseline.cpp stb_image.h stb_image_write.h
	$(CXX) $(CXXFLAGS) -o $(SEQ_TARGET) image_baseline.cpp

# Rule to build the parallel version
$(PARA_TARGET): image_parallel.cpp stb_image.h stb_image_write.h
	$(CXX) $(CXXFLAGS) $(OMPFLAGS) -o $(PARA_TARGET) image_parallel.cpp

# Clean up build files
clean:
	rm -f $(SEQ_TARGET) $(PARA_TARGET) *.o output_*.jpg results.dat *.png
