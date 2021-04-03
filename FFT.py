%matplotlib inline
import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
import csv

with open(r"C:\Users\orlca\OneDrive\Desktop\dati.txt") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 1
    I = []
    Q = []
    for row in csv_reader:
            I.append(row[0])
            Q.append(row[1])
            line_count += 1
    print(line_count)

# Number of samplepoints
N = 1000
# sample spacing
T = 9.414
x = np.linspace(0.0, N*T, N)
#y = np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x) # sostituire con dati delle y
#yf = scipy.fftpack.fft(y)
If = scipy.fftpack.fft(I)
Qf = scipy.fftpack.fft(Q)
xf = np.linspace(0.0, 1.0/(2.0*T), int(N/2))

fig, FFTI = plt.subplots()
FFTI.plot(xf, 2.0/N * np.abs(If[:N//2]))
plt.show()
fig, IdiT = plt.subplots()
IdiT.plot(x, I)
plt.show()
fig, FFTQ = plt.subplots()
FFTQ.plot(xf, 2.0/N * np.abs(Qf[:N//2]))
plt.show()
fig, QdiT = plt.subplots()
QdiT.plot(x, Q)
plt.show()