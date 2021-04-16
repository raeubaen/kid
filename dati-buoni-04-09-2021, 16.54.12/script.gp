set term postscript
set output "g.ps"
unset key
set tics font "Helvetica,16"
set xlabel font "Helvetica,24"
set ylabel font "Helvetica,24"
set xlabel 'Time (us)'
set ylabel 'ADC units'
plot '<cat' using 3:1 w l
