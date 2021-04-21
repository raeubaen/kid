import matplotlib.pyplot as plt
import pandas as pd

amps = {
  "up":   pd.read_csv("ampsu.csv"),
  "low": pd.read_csv("ampgiu.csv"),
}

for amp in amps.values(): amp.columns = ["n", "f", "a", "g", "p"]

# upper
df = amps["up"]
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

#lower
df = amps["low"]
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

LPFl.plot(amps["up"].f, amps["up"].g, 'ob-', linewidth=0.5, markersize=2)
LPFl.grid(True, which="both", ls="-", linewidth=0.5)
LPFl.plot(amps["low"].f, amps["low"].g, 'og-', linewidth=0.5, markersize=2)

LPFl.set_xscale('log')

plt.legend(['Upper amplifier', 'Lower amplifier'])

LPFl.set_xlabel('Frequency(Hz)')
LPFl.set_ylabel('Gain(dB)', color='k')

plt.title('Upper and lower amplifiers gain comparison')

plt.show()

#phase comparison

fig, LPFl = plt.subplots()

LPFl.plot(amps["up"].f, amps["up"].p, 'or-', linewidth=0.5, markersize=2)
LPFl.grid(True, which="both", ls="-", linewidth=0.5)
LPFl.plot(amps["low"].f, amps["low"].p, 'om-', linewidth=0.5, markersize=2)

LPFl.set_xscale('log')

plt.legend(['Upper amplifier', 'Lower amplifier'])

LPFl.set_xlabel('Frequency(Hz)')
LPFl.set_ylabel('Phase(deg)', color='k')

plt.title('Upper and lower amplifier phase comparison')

plt.show()
