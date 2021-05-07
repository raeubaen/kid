import pandas as pd
import matplotlib.pyplot as plt
from sys import stdin

plt.style.use('ggplot')
plt.rcParams['axes.facecolor'] = '#f7f9fc'

fig, ax = plt.subplots(figsize=(8,3))

df = pd.read_csv(stdin, sep=" ")
ax.hist(df)
ax.set(
  xlabel= "Average time between readings (us)",
  ylabel = "Absolute frequency",
  title = "Sampling time average spacing"
)

ratio = 0.3
xleft, xright = ax.get_xlim()
ybottom, ytop = ax.get_ylim()
ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)

plt.show()

