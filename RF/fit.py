from scipy import optimize
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from ellipse import LsqEllipse
from matplotlib.patches import Ellipse
import matplotlib

matplotlib.rc('xtick', labelsize=16)
matplotlib.rc('ytick', labelsize=16)

plt.style.use('ggplot')

plt.rcParams['axes.facecolor'] = '#f7f9fc'
matplotlib.rcParams.update({'font.size': 20})

# tot dBm di RF al mixer (VNA): -8.79 dBm

df = pd.read_csv("scope_12.csv")
df.columns = ["t", "q", "i"]

X = np.array(list(zip(df.i, df.q)))

reg = LsqEllipse().fit(X)
center, width, height, phi = reg.as_parameters()

print(f'center: {center[0]:.3f}, {center[1]:.3f}')
print(f'width: {width:.3f}')
print(f'height: {height:.3f}')
print(f'phi: {phi:.3f}')

fig = plt.figure(figsize=(6, 6))
ax = plt.subplot()
ax.axis('equal')
ax.scatter(df.i, df.q, c = np.asarray(df.index), zorder=1)
ellipse = Ellipse(
    xy=center, width=2*width, height=2*height, angle=np.rad2deg(phi),
    edgecolor='b', fc='None', lw=2, label='Fit', zorder=2
)
ax.add_patch(ellipse)

plt.xlabel('I (V)')
plt.ylabel('Q (V)')

plt.legend()
plt.show()

