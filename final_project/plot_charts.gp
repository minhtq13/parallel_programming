set terminal pngcairo enhanced font 'Verdana,10'
set output 'speedup_chart.png'
set title "Speedup vs. Number of Threads"
set xlabel "Number of Threads (p)"
set ylabel "Speedup (T_seq / T_para)"
set grid
set key top left

# Get the sequential time from the environment variable
# If it's not set, use a default value (you might need to adjust this)
T_seq = system("echo $SEQ_TIME")
if (T_seq eq "") { T_seq = 1.0 } else { T_seq = real(T_seq) }


# Plot Speedup: T_sequential / T_parallel(p)
# Plot Ideal Speedup: y = x
plot "results.dat" using 1:(T_seq/\$2) with linespoints title "Actual Speedup", \
     x with lines title "Ideal Speedup"

# --- Efficiency Chart ---
set output 'efficiency_chart.png'
set title "Efficiency vs. Number of Threads"
set ylabel "Efficiency (Speedup / p)"
set yrange [0:1.2] # Efficiency is usually between 0 and 1 (100%)

# Plot Efficiency: (T_sequential / T_parallel(p)) / p
# Plot Ideal Efficiency: y = 1
plot "results.dat" using 1:((T_seq/\$2)/\$1) with linespoints title "Actual Efficiency", \
     1.0 with lines title "Ideal Efficiency (100%)"

print "Charts generated: speedup_chart.png, efficiency_chart.png"
