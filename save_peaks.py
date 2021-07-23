import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import sys
import random
from tqdm import tqdm

i_c, q_c = 1.5747, 0.61972
iq_ratio = 0.898844
radius = 0.3994476

def get_phase(data):
    q = (data.q - q_c) * iq_ratio + q_c
    return np.unwrap(2*np.arctan((q-q_c)/(data.i-i_c)))/2

def get_amp(data):
    q = (data.q - q_c) * iq_ratio + q_c
    return np.sqrt((q-q_c)**2 + (data.i-i_c)**2)/radius

cut = []

count = 0
phase_peaks = []
for i in tqdm(range(10000)): #in teoria tutto
    try:
      df = pd.read_csv(f"signal{i}.dat", sep=' ')
    except:
      continue
    df.columns = ["i", "q", "t"]
    if np.sum(df.i > 4096): continue
    df = df.sort_values(["t"])
    df = df.reset_index()
    df = df.iloc[10:3310]

    df["phase"] = get_phase(df)*1000

    # mediamo 100 - 50 punti sono quelli che il segnale impiega a "salire"
    # la soglia è orientativamente sui mrad minimi del picco per non essere considerato rumore
    # una soglia troppo bassa non ci fa vedere la pedestal
    if df.phase.rolling(100).mean().diff(periods=50).max() > 1.6:
      df.phase = df.phase.rolling(100).mean()
      df.dropna(inplace=True)
      baseline_end = df.phase.argmin() - 100
      phase_m = (df.phase.iloc[:baseline_end].mean() - df.phase).max()
      phase_peaks.append(phase_m)
      count +=1
      if 2 < phase_m < 10:
        cut.append(df)
print(count)

phase_peaks = np.asarray(phase_peaks)
np.savetxt("phase_peaks_lunga.txt", phase_peaks)

to_plot = random.choices(cut, k=100)
n = 10
fig, axs = plt.subplots(n, n, figsize=(50, 50))
for i in range(n):
  for j in range(n):
    df = to_plot[n*1+j]
    axs[i][j].plot(df.t - df.t.iloc[0], df.phase.iloc[:200].mean() - df.phase)
plt.show()
