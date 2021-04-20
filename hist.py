import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from sys import stdin

plt.style.use('ggplot')
plt.rcParams['axes.facecolor'] = '#f7f9fc'

fig, ax = plt.subplots(figsize=(8,4))

ax.xaxis.set_major_locator(MaxNLocator(integer=True))

df = pd.read_csv(stdin, sep=" ")
df.dropna()
df.columns = ["i", "q", "t"]
df = df.sort_values(["t"])
df = df.iloc[df.t.diff().argmax():]
ax.hist(df.t.diff().dropna().astype("int"), bins=4)
ax.set(
  xlabel= "Time between readings",
  ylabel = "Absolute frequency",
  title = "Sampling time spacing"
)
plt.show()

