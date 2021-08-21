import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import sys
import random
from tqdm import tqdm

i_c, q_c = 1.934521753372309, 0.617395316850268
iq_ratio = 0.9261851848012432


plt.style.use("ggplot")
plt.rcParams['axes.facecolor'] = '#f7f9fc'

plt.rcParams.update({'font.size': 28})
matplotlib.rc('xtick', labelsize=24)
matplotlib.rc('ytick', labelsize=24)

def get_phase(data):
    q = (data.q - q_c) * iq_ratio + q_c
    return np.unwrap(2*np.arctan((q-q_c)/(data.i-i_c)))/2

def get_amp(data):
    q = (data.q - q_c) * iq_ratio + q_c
    return np.sqrt((q-q_c)**2 + (data.i-i_c)**2)/radius

data = np.loadtxt("files_num.txt").astype("int")
print(max(data))
print(len(data))

thresholds = np.arange(12, 16, 1) #oppure da 0 a 30 per iil grafico grande

window = 70

prec, rec = [], []
for threshold in thresholds:
  results = []
  for i in tqdm(range(max(data)+1)): #in teoria tutto
      try:
        df = pd.read_csv(f"signal{i}.dat", sep=' ')
        df.columns = ["i", "q", "t"]
      except:
        continue
      if np.sum(df.i > 4096): continue
      df = df.sort_values(["t"])
      df = df.reset_index()
      df = df.iloc[10:3310]
      df.i *= 3.3/4095
      df.q *= 3.3/4095
      df["phase"] = get_phase(df)*1000
      df.phase = df.phase.iloc[:500].mean() - df.phase
      if df.phase.rolling(window).mean().diff(window).max() > threshold:
        results.append(i)


  tp = len(np.intersect1d(results, data))
  print(tp, len(results), len(data))
  fp = len(data) - tp
  fn = len(results) - tp
  prec.append(tp/(tp+fp))
  rec.append(tp/(tp+fn))

sc = plt.scatter(rec, prec, c=thresholds)


plt.colorbar(sc, label="Threshold (mrad)")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.show()

np.savetxt("precision.txt", np.asarray(prec))
np.savetxt("recall.txt", np.asarray(rec))
