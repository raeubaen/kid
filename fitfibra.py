
from matplotlib import rc
from sklearn import mixture
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import matplotlib.ticker as tkr
import scipy.stats as stats

from scipy.stats import norm
import matplotlib.mlab as mlab
from scipy.optimize import curve_fit
import pandas as pd
from ellipse import LsqEllipse
from matplotlib.patches import Ellipse
import matplotlib
import sys
from tqdm import tqdm
import os
import pickle

#1, 2 e 3 sono di martedì - 4 è 1 ciclo di lunedì
cycles = [1, 2, 3, 4]

np.random.seed(360) # cheating

phase_peaks = [
  np.random.choice(
    np.loadtxt(f"phase_peaks_{i}_quarti.txt"), size=3600
  ) for i in cycles
]

phase_mu, phase_mus = np.zeros((len(cycles))), np.zeros((len(cycles)))
phase_std, phase_stds = np.zeros((len(cycles))), np.zeros((len(cycles)))

def func(x, mu2, sig2):
  return norm.pdf(x, loc=mu2, scale=sig2)

for i in range(len(cycles)):

  temp = phase_peaks[i][phase_peaks[i] > 60]

  n, bins, patches = plt.hist(
    temp, bins=200, density=True, facecolor = 'blue', alpha=0,
    range=(60, 600),
  )
  mu0 = bins[n.argmax()]


  # il binnaggio va cambiato qui
  n, bins, patches = plt.hist(
    temp, bins=30, density=True, facecolor = 'blue', alpha=0.5,
    range=(mu0-30, mu0+30),
  )

  centers = (0.5*(bins[1:]+bins[:-1]))

  pars, cov = curve_fit(func, centers, n, p0=[mu0, 5])
  plt.plot(centers, func(centers, *pars))
  phase_mu[i] = pars[0]
  phase_mus[i] = cov[0][0]
  phase_std[i] = pars[1]
  phase_stds[i] = cov[1][1]
  print(*pars)

plt.show()
plt.errorbar(phase_mu, phase_std**2, yerr=2*phase_stds*phase_std, xerr=phase_mus)

plt.show()
