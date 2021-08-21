import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import sys
import random
from tqdm import tqdm


plt.style.use("ggplot")
plt.rcParams['axes.facecolor'] = '#f7f9fc'

plt.rcParams.update({'font.size': 50})
matplotlib.rc('xtick', labelsize=40)
matplotlib.rc('ytick', labelsize=40)

i_c, q_c = 1.934521753372309, 0.617395316850268
iq_ratio = 0.9261851848012432

def get_phase(data):
    q = (data.q - q_c) * iq_ratio + q_c
    return np.unwrap(2*np.arctan((q-q_c)/(data.i-i_c)))/2

def get_amp(data):
    q = (data.q - q_c) * iq_ratio + q_c
    return np.sqrt((q-q_c)**2 + (data.i-i_c)**2)/radius


files = np.loadtxt("files_num.txt").astype("int")[:300]

big_pulses = []

little_pulses = []

k = 0
for i in tqdm(files): #in teoria tutto
    try:
      df = pd.read_csv(f"signal{i}.dat", sep=' ')
      df.columns = ["i", "q", "t"]
    except:
      continue
    df.columns = ["i", "q", "t"]
    if np.sum(df.i > 4096): continue
    df = df.sort_values(["t"])
    df = df.reset_index()
    df = df.iloc[10:3310]

    df["phase"] = get_phase(df)*1000
    df.phase = df.phase.iloc[:500].mean() - df.phase
    m = df.phase.max()
    if m < 6:
        fig, ax = plt.subplots(figsize=(20, 13))
        ax.plot((df.t - df.t.iloc[0])/1000, df.phase)
        df.phase = df.phase.rolling(70).mean()
        ax.plot((df.t - df.t.iloc[0])/1000, df.phase)
        plt.xlabel("Time (ms)")
        plt.ylabel("Phase (mrad)")
        fig.savefig(f"figure{k}.png", pad_inches=0)
        k += 1
