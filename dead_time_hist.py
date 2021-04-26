import pandas as pd
import matplotlib.pyplot as plt
from sys import stdin
from brokenaxes import brokenaxes
import numpy as np
import matplotlib


plt.style.use('ggplot')
plt.rcParams['axes.facecolor'] = '#f7f9fc'
plt.rcParams.update({'font.size': 20})

df = pd.read_csv(stdin, sep=" ")
df.dropna()
df.columns = ["t"]

def plot_histogram(data, cutoff):
    fig, ax = plt.subplots(figsize=(10, 2))
    _, bins, patches = plt.hist(np.clip(data, 0, cutoff), bins = [4401.5, 4402.5, 4403.5, 4404.5, 4405.5])

    xticks = bins[:-1] + 0.5

    xlabels = xticks.astype("int").astype(str)
    xlabels[-1] = '>=' + xlabels[-1]

    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels)

    plt.setp(patches, linewidth=0)
    plt.legend(loc='upper left')
    fig.tight_layout()

plot_histogram(df.t, 4405)
plt.xlabel("Time (us)")
plt.ylabel("Absolute Frequency")
plt.show()

plt.close()

fig, ax = plt.subplots(figsize=(10, 2))
plt.gca().set_aspect(0.1)

logbins = np.geomspace(df.t.min(), df.t.max(), 30)
ax.hist(df.t, bins = logbins)

ax.set_xlim(4400, 40000)
ax.set_xscale("log")
ax.set_xticks([4400, 6000, 8000, 10000, 20000, 40000])
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.get_xaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())

ax.set_yscale("log")
ax.set_yticks([1, 5, 10, 100, 500])
ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

plt.xlabel("Time (us)")
plt.ylabel("Absolute Frequency")
plt.show()
