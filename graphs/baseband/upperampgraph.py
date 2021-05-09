import matplotlib.pyplot as plt
import pandas as pd

amp = pd.read_csv("ampsu.csv")

amp.columns = ["n", "f", "a", "g", "p"]

# upper
df = amp
fig, LPFl = plt.subplots(figsize = (10, 5))

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
