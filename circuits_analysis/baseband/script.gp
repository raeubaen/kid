set term postscript
set output "g.ps"
set tics font "Helvetica,18"
set xrange [10000:130000]
set xlabel font "Helvetica,24"
set ylabel font "Helvetica,24"
set xlabel 'Time (us)'
set ylabel 'ADC units'
plot 'data' using 3:1 w l title "ch1", 'data' using 3:2 w l title "ch2"
