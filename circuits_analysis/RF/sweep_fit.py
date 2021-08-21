from matplotlib.patches import Ellipse
from ellipse import LsqEllipse
from scipy import optimize
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import sys
import warnings
import time

warnings.filterwarnings("ignore")

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

# fit results
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
'''

# mean results (std are of order 1e-5)
res = np.loadtxt("res.csv", delimiter=",", skiprows=1, usecols=(1, 2, 3, 4, 5))

i, q = res[:, 0], res[:, 2]

X = np.array(list(zip(i, q)))
reg = LsqEllipse().fit(X)
center, width, height, phi = reg.as_parameters()

fig = plt.figure(figsize=(8, 8))
ax = plt.subplot()
ax.scatter(i, q, zorder=1)
ellipse = Ellipse(
    xy=center, width=2*width, height=2*height, angle=np.rad2deg(phi),
    edgecolor='b', fc='None', lw=2, label='Fit', zorder=2
)
ax.add_patch(ellipse)

ax.set_xlim(0, 3.3)
ax.set_ylim(0, 3.3)
ax.axis('equal')
plt.xlabel('I (V)')
plt.ylabel('Q (V)')

plt.legend()
plt.show()

i_c, q_c = center
iq_ratio = width/height
q = (q - q_c) * iq_ratio + q_c

freq = 2.18 +  np.arange(0, 100)*(2.217 - 2.18)/100

plt.plot(freq*1000, i-i_c, label="I")
plt.plot(freq*1000, q-q_c, label="Q")

plt.xlabel("Frequency [MHz]")
plt.ylabel("Voltage (V)")
plt.legend()
plt.show()

phase = np.unwrap(
  2*np.arctan((q-q_c)/(i-i_c))
)/2
phase_shift = phase[0] - phase

plt.plot(freq*1000, phase_shift/np.pi * 180, label="Phase shift")

time_delay, offset = np.polyfit(2*np.pi * freq, phase_shift, 1)

print(f"Time delay (ns): {time_delay}")

plt.plot(freq*1000, (offset + time_delay*2*np.pi * freq) / np.pi * 180, label="Linear fit")

plt.xlabel("Frequency [MHz]")
plt.ylabel("Phase-shift (deg)")
plt.legend()
plt.show()

amp = np.sqrt((q-q_c)**2 + (i-i_c)**2)

plt.plot(freq*1000, amp, label="Amplitude")

plt.xlabel("Frequency [MHz]")
plt.ylabel("Amplitude (V)")
plt.legend()
plt.show()
