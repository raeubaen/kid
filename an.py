from scipy.stats import norm
import matplotlib.mlab as mlab
from scipy.optimize import curve_fit
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from ellipse import LsqEllipse
from matplotlib.patches import Ellipse
import matplotlib
import sys
import random
from tqdm import tqdm
import os
import pickle

i_c, q_c = 1.5747, 0.61972
iq_ratio = 0.898844
radius = 0.3994476

df_array = []

folder = "."

def get_phase(data):
    q = (data.q - q_c) * iq_ratio + q_c
    return np.unwrap(2*np.arctan((q-q_c)/(data.i-i_c)))/2

def get_amp(data):
    q = (data.q - q_c) * iq_ratio + q_c
    return np.sqrt((q-q_c)**2 + (df.i-i_c)**2)

df_array = []

for file in os.listdir(folder):
  if not file.endswith(".dat"):
    continue
  try:
    df = pd.read_csv(f"{folder}/{file}", sep=' ')
  except:
   print("Qualcosa è andato male..sticazzi")
   continue
  df.columns = ["i", "q", "t"]
  if np.sum(df.i > 4096): continue
  df = df.sort_values(["t"])
  df = df.reset_index()
  df.i *= 3.3/4095
  df.q *= 3.3/4095
  df_array.append(df)

'''
pickle.dump(df_array, open( "save.p", "wb" ))

df_array = pickle.load(open( "save.p", "rb" ))

dfs = random.sample(df_array, 25)

fig, axs = plt.subplots(5, 5, figsize=(30, 30))
for i in range(5):
  for j in range(5):
    n  = 5*i+j
    phase = get_phase(dfs[n])*1000
    amp = get_amp(dfs[n])*1000
    axs[i][j].plot(amp[:100].mean() - amp[:2000], label="Amplitude", color="red")
    axs[i][j].plot(phase[:100].mean() - phase[:2000], label="Phase")
    axs[i][j].set(xlabel="Time (arb. units)", ylabel="Phase (mrad)")
    axs[i][j].legend()

fig.savefig("pulses.pdf")
plt.close()
'''

phase_peaks = []
amp_peaks = []
for df in df_array:
  phase = get_phase(df)*1000
  phase_m = (phase[:100].mean() - phase[:2000]).max()
  amp = get_amp(df)*1000
  amp_m = (amp[:100].mean() - amp[:2000]).max()
  phase_peaks.append(phase_m)
  amp_peaks.append(amp_m)

phase_peaks = np.asarray(phase_peaks)
amp_peaks = np.asarray(amp_peaks)

phase_peaks = phase_peaks[phase_peaks > 300]

phase_peaks = np.random.choice(phase_peaks, size=200)

mu, std = norm.fit(phase_peaks)

n, bins, patches = plt.hist(
  phase_peaks, bins=50, density=True, facecolor = 'blue', alpha=0.5,
  range = (mu - 100, mu + 100),
)

centers = (0.5*(bins[1:]+bins[:-1]))

pars, cov = curve_fit(
  lambda x, mu, sig : norm.pdf(x, loc=mu, scale=sig), 
  centers, n, p0=[mu, std]
)

print(*pars)
print(*cov)

plt.plot(centers, norm.pdf(centers,*pars), 'k--',linewidth = 2) 

plt.show()
