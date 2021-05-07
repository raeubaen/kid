from scipy import optimize
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import sys
import warnings
import time

warnings.filterwarnings("ignore")
print("oiboib")
matplotlib.rc('xtick', labelsize=16)
matplotlib.rc('ytick', labelsize=16)

plt.style.use('ggplot')

plt.rcParams['axes.facecolor'] = '#f7f9fc'
matplotlib.rcParams.update({'font.size': 20})

# tot dBm di RF al mixer (VNA): -8.79 dBm
# va plottato quello senza circuito a basse frequence per misurare i parametri del mixer

df = pd.read_csv(sys.stdin, sep=" ")
df.columns = ["i", "q", "t"]

df.i, df.q = df.i/4096*3.3, df.q/4096*3.3

'''
def loss(par):
  width = par[0]*1e4 + 1.05e5
  t0 = df.t.min()
  loss = 0
  for i in range(2, 50):
    loss += (df[df.t > t0 + i*width])[df.t < t0 + (i+1)*width].i.var()
  return loss

out = optimize.minimize(loss, (1), options={"maxiter":100})
print(out)
width = out.x[0]*1e4 + 1.05e5
'''

width = 1.05e5 +  1e4 * (-0.0023668)
t0 = df.t.min()

res = np.zeros((100, 5))
for i in range(100):
  temp = (df[df.t > t0 + i*width])[df.t < t0 + (i+1)*width]
  res[i, 1] = temp.i.std()/np.sqrt(len(temp))
  res[i, 3] = temp.q.std()/np.sqrt(len(temp))
  res[i, 0] = temp.i.mean()
  res[i, 2] = temp.q.mean()
  res[i, 4] = temp.t.mean()
  #plt.axvline(t0 + i*width)

pd.DataFrame(res).to_csv("res.csv")

plt.scatter(df.t[::100], df.i[::100], label="I")
plt.scatter(df.t[::100], df.q[::100], label="Q")

plt.hlines(res[:, 0], res[:, 4] - width/2, res[:, 4] + width/2, color="black", label="Fit")
plt.hlines(res[:, 2], res[:, 4] - width/2, res[:, 4] + width/2, color="black")

plt.xlabel('Time (us)')
plt.ylabel('Voltage (V)')

plt.legend()
#plt.savefig("fig.pdf")
plt.show()

i, q = res[:, 0], res[:, 2]
freq = 2.18 +  np.arange(0, 100)*(2.217 - 2.18)

plt.plot(freq*1000, i, label="I")
plt.plot(freq*1000, q, label="Q")

plt.xlabel("Frequency [MHz]")
plt.ylabel("Voltage (V)")
plt.legend()
plt.show()
