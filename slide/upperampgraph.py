import matplotlib.pyplot as plt
import pandas as pd

amp = pd.read_csv("ampsu.csv")

amp.columns = ["n", "f", "a", "g", "p"]

# upper
df = amp
fig, LPFl = plt.subplots()

LPFr = LPFl.twinx()
LPFl.plot(df.f, df.g, 'ob-', linewidth=0.5, markersize=2)
LPFl.grid(True, which="both", ls="-", linewidth=0.5)
LPFr.plot(df.f, df.p, 'or-', linewidth=0.5, markersize=2)

LPFl.set_xscale('log')
LPFr.set_xscale('log')

LPFl.set_xlabel('Frequency(Hz)')
LPFl.set_ylabel('Gain(dB)', color='b')
LPFr.set_ylabel('Phase(deg)', color='r')

plt.title('Amplifier')

plt.show()

#plot gain comparison
#upper
fig, LPFl = plt.subplots()

LPFl.plot(amp.f, amp.g, 'ob-', linewidth=0.5, markersize=2)

LPFl.set_xscale('log')

plt.legend(['Upper amplifier', 'Lower amplifier'])

LPFl.set_xlabel('Frequency(Hz)')
LPFl.set_ylabel('Gain(dB)', color='k')

plt.title('Upper and lower amplifiers gain comparison')

plt.show()

#phase comparison

fig, LPFl = plt.subplots()

LPFl.plot(amp.f, amp.p, 'or-', linewidth=0.5, markersize=2)

LPFl.set_xscale('log')

plt.legend(['Upper amplifier', 'Lower amplifier'])

LPFl.set_xlabel('Frequency(Hz)')
LPFl.set_ylabel('Phase(deg)', color='k')

plt.title('Upper and lower amplifier phase comparison')

plt.show()
