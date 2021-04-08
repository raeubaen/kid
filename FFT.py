from scipy.fft import fft, fftfreq
import numpy as np
import matplotlib.pyplot as plt
import csv

data = np.loadtxt('ardudata.txt' , delimiter=',')

I = data[:, 0]
Q = data[:, 1]

print(len(data), "righe lette")

# Number of samplepoints
N = len(data)
# sample spacing
T =  9.414*10**(-6)					# 1/frequenza di campionamento
x = np.linspace(0.0, N*T, N, endpoint=False)  
If = fft(I)						# trasformata di fourier
Qf = fft(Q)
xf = fftfreq(N, T)[:N//2]				# array delle frequenze

from scipy.signal import blackman
w = blackman(N)						# windowing con funzione di blackman
Iwf = fft(I*w)

#plot
fig, S = plt.subplots()
S.plot(x, I, 'r--')
plt.ylabel('volts')
plt.xlabel('seconds')
plt.grid
plt.show()

fig, FFT = plt.subplots()
FFT.semilogy(xf[1:N//2], 2.0/N * np.abs(If[1:N//2]), '-b')
FFT.semilogy(xf[1:N//2], 2.0/N * np.abs(Iwf[1:N//2]), '-r')
plt.legend(['FFT', 'FFT w. window'])
plt.xlabel('Hz')
plt.grid()
plt.show()
