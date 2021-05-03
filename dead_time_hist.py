import pandas as pd
import matplotlib.pyplot as plt
from sys import stdin
from brokenaxes import brokenaxes
import numpy as np
import matplotlib


plt.style.use('ggplot')
plt.rcParams['axes.facecolor'] = '#f7f9fc'
plt.rcParams.update({'font.size': 18})
plt.rcParams.update({'xtick.labelsize': 14})
plt.rcParams.update({'ytick.labelsize': 14})


df = pd.read_csv(stdin, sep=" ")
df.dropna()
df.columns = ["t"]

def plot_histogram(data, cutoff, ax):
    _, bins, patches = ax.hist(np.clip(data, 0, cutoff), bins = [4401.5, 4402.5, 4403.5, 4404.5, 4405.5])

    xticks = bins[:-1] + 0.5

    xlabels = xticks.astype("int").astype(str)
    xlabels[-1] = '>=' + xlabels[-1]

    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels)

    ax.legend(loc='upper left')

fig, axs = plt.subplots(1, 2, figsize=(10, 3), tight_layout=True)

ax = axs[1]
plot_histogram(df.t, 4405, ax)
ax.set_xlabel("Time (us)")

ax = axs[0]

logbins = np.geomspace(df.t.min(), df.t.max(), 30)
ax.hist(df.t, bins = logbins)

ax.set_xlim(4400, 40000)
ax.set_xscale("log")
ax.set_xticks([4400, 6000, 10000, 40000])
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.get_xaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())

ax.set_yscale("log")
ax.set_yticks([1, 5, 10, 100, 500])
ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

ax.set_xlabel("Time (us)")
ax.set_ylabel("Absolute Frequency")
plt.show()
