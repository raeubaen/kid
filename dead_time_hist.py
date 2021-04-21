import pandas as pd
import matplotlib.pyplot as plt
from sys import stdin
from brokenaxes import brokenaxes
import numpy as np

plt.style.use('ggplot')
plt.rcParams['axes.facecolor'] = '#f7f9fc'

df = pd.read_csv(stdin, sep=" ")
df.dropna()
df.columns = ["t"]

plt.hist(df.t, bins=(list(np.linspace(4400, 4480, 20)) + list(np.linspace(4500, 90000, 20)) ), density=True)
plt.show()
