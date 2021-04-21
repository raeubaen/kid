set terminal pngcairo size 1500,700 enhanced color
set output 'g.png'

set lmargin at screen 0.1
set bmargin at screen 0.1

set tics font "Helvetica,18"
#set xrange [13000:14000]
#set yrange [1200:4200]
#set xtics 13000,100,13900
set xlabel font "Helvetica,24" offset -1
set ylabel font "Helvetica,24" offset -2
set key font "Helvetica,16"
set xlabel 'Time (us)'
set ylabel 'ADC units'

plot 'data' u 3:1 w l title 'ch1', 'data' u 3:2 w l title 'ch2'



