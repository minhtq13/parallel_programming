#!/bin/bash

# Number of runs for averaging
NUM_RUNS=5

# Thread counts to test
THREAD_COUNTS=(1 2 4 8 10 12)

# Output file for results
RESULTS_FILE="results.dat"

# --- 1. Compile the code ---
echo "Compiling the code..."
make clean
make
if [ $? -ne 0 ]; then
    echo "Compilation failed. Exiting."
    exit 1
fi
echo "Compilation successful."

# Check for input image
if [ ! -f "input.jpg" ]; then
    echo "Warning: input.jpg not found. Creating a dummy 1920x1080 image."
    # Create a dummy image using ImageMagick if available, or just fail
    if command -v convert &> /dev/null; then
        convert -size 1920x1080 xc:white input.jpg
    else
        echo "Error: ImageMagick 'convert' command not found. Please provide an 'input.jpg' file."
        exit 1
    fi
fi


# --- 2. Run Sequential Version ---
echo "Running sequential version..."
total_seq_time=0
for i in $(seq 1 $NUM_RUNS); do
    # Extract time from the program's output
    seq_time=$(./blur_seq | grep "Thời gian chạy" | awk '{print $5}')
    total_seq_time=$(echo "$total_seq_time + $seq_time" | bc)
    echo "  Run $i: $seq_time s"
done
# Calculate average
avg_seq_time=$(echo "scale=6; $total_seq_time / $NUM_RUNS" | bc)
echo "Average Sequential Time: $avg_seq_time s"
echo ""

# Write header to results file
echo "# Threads   Time(s)" > $RESULTS_FILE
# Write sequential time as time for 1 thread (for baseline)
# Note: We run the parallel version with 1 thread for a fair comparison of overhead
# echo "1 $avg_seq_time" >> $RESULTS_FILE


# --- 3. Run Parallel Version ---
echo "Running parallel version with different thread counts..."
for p in "${THREAD_COUNTS[@]}"; do
    echo "Testing with $p threads..."
    total_para_time=0
    # Modify the parallel code to set the number of threads
    sed -i.bak "s/int num_threads = [0-9]*;/int num_threads = $p;/" image_parallel.cpp
    # Recompile the parallel code with the new thread count
    make $(PARA_TARGET) > /dev/null 2>&1

    for i in $(seq 1 $NUM_RUNS); do
        para_time=$(./blur_para | grep "Thời gian chạy" | awk '{print $5}')
        total_para_time=$(echo "$total_para_time + $para_time" | bc)
        echo "  Run $i: $para_time s"
    done
    # Calculate average
    avg_para_time=$(echo "scale=6; $total_para_time / $NUM_RUNS" | bc)
    echo "Average Parallel Time ($p threads): $avg_para_time s"
    
    # Save result to file
    echo "$p $avg_para_time" >> $RESULTS_FILE
    echo ""
done

# Restore original parallel file
mv image_parallel.cpp.bak image_parallel.cpp

echo "Experiment finished. Results saved to $RESULTS_FILE"
echo "Sequential time for calculations: $avg_seq_time"

# Pass sequential time to the plotting script
export SEQ_TIME=$avg_seq_time
