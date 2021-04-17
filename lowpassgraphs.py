import numpy as np
import matplotlib.pyplot as plt
	
Butter = np.loadtxt('scope_8.txt' , delimiter=',')
#number = Butter[:, 0]
#freqHz = Butter[:, 1]
#ampVpp = Butter[:, 2]
#gaindB = Butter[:, 3]
#phasedeg = Butter[:, 4]

Bessel = np.loadtxt('scope_9.txt' , delimiter=',')
#number = Bessel[:, 0]
#freqHz = Bessel[:, 1]
#ampVpp = Bessel[:, 2]
#gaindB = Bessel[:, 3]
#phasedeg = Bessel[:, 4]

#plot
fig, LPF = plt.subplots()

LPF1 = LPF.twinx()
LPF.plot(Butter[:, 1], Butter[:, 3], 'ob-', linewidth=0.5, markersize=2)
LPF.grid(True, which="both", ls="-", linewidth=0.5)
LPF1.plot(Butter[:, 1], Butter[:, 4], 'or-', linewidth=0.5, markersize=2)

LPF.set_xscale('log')
LPF1.set_xscale('log')

LPF.set_xlabel('Frequency(Hz)')
LPF.set_ylabel('Gain(dB)', color='b')
LPF1.set_ylabel('Phase(deg)', color='r')

plt.title('Butterworth/Sallen-Key 2nd order low pass filter')

plt.show()

#plot bessel

fig, LPF = plt.subplots()

LPF1 = LPF.twinx()
LPF.plot(Bessel[:, 1], Bessel[:, 3], 'ob-', linewidth=0.5, markersize=2)
LPF.grid(True, which="both", ls="-", linewidth=0.5)
LPF1.plot(Bessel[:, 1], Bessel[:, 4], 'or-', linewidth=0.5, markersize=2)

LPF.set_xscale('log')
LPF1.set_xscale('log')

LPF.set_xlabel('Frequency(Hz)')
LPF.set_ylabel('Gain(dB)', color='b')
LPF1.set_ylabel('Phase(deg)', color='r')

plt.title('Bessel 3nd order low pass filter')

plt.show()

#plot gain comparison
fig, LPF = plt.subplots()

LPF.plot(Butter[:, 1], Butter[:, 3], 'ob-', linewidth=0.5, markersize=2)
LPF.grid(True, which="both", ls="-", linewidth=0.5)
LPF.plot(Bessel[:, 1], Bessel[:, 3], 'og-', linewidth=0.5, markersize=2)

LPF.set_xscale('log')

plt.legend(['Butterworth 2nd order', 'Bessel 3d order'])

LPF.set_xlabel('Frequency(Hz)')
LPF.set_ylabel('Gain(dB)', color='k')

plt.title('Low Pass filters gain comparison')

plt.show()

#phase comparison
fig, LPF = plt.subplots()

LPF.plot(Butter[:, 1], Butter[:, 4], 'or-', linewidth=0.5, markersize=2)
LPF.grid(True, which="both", ls="-", linewidth=0.5)
LPF.plot(Bessel[:, 1], Bessel[:, 4], 'om-', linewidth=0.5, markersize=2)

LPF.set_xscale('log')

plt.legend(['Butterworth 2nd order', 'Bessel 3d order'])

LPF.set_xlabel('Frequency(Hz)')
LPF.set_ylabel('Phase(deg)', color='k')

plt.title('Low Pass filters phase comparison')

plt.show()