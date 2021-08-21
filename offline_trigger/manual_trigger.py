import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import sys
import random
from tqdm import tqdm

i_c, q_c = 1.934521753372309, 0.617395316850268
iq_ratio = 0.9261851848012432

def get_phase(data):
    q = (data.q - q_c) * iq_ratio + q_c
    return np.unwrap(2*np.arctan((q-q_c)/(data.i-i_c)))/2

def get_amp(data):
    q = (data.q - q_c) * iq_ratio + q_c
    return np.sqrt((q-q_c)**2 + (data.i-i_c)**2)/radius


files = []
for i in tqdm(1000): #in teoria tutto
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
    plt.plot((df.t - df.t.iloc[0])/1000, df.phase)
    plt.show(block=False)
    if plt.waitforbuttonpress(timeout=1):
      files_new.append(i)
    plt.close()

np.savetxt("files_num.txt", np.asarray(files_new))
