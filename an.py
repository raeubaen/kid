import pymc3 as pm

from scipy.stats import kstest

from astropy.visualization import hist

from scipy.optimize import curve_fit
from matplotlib import rc
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import matplotlib.ticker as tkr
from lmfit.models import GaussianModel

import matplotlib.mlab as mlab
import pandas as pd
import matplotlib
import sys
from tqdm import tqdm
import os
import pickle

plt.style.use("ggplot")
plt.rcParams['axes.facecolor'] = '#f7f9fc'

cycles = [1, 2, 3,  6]
colors = ["red", "green", "blue", "brown", "purple"]

phase_peaks = [
    np.loadtxt(f"phase_peaks_{i}_quarti_70_rolling_mean.txt") for i in cycles
]

phase_mu, phase_mus = np.zeros((len(cycles))), np.zeros((len(cycles)))
phase_std, phase_stds = np.zeros((len(cycles))), np.zeros((len(cycles)))

import scipy.odr as odr
from scipy.stats import kstest

''' Performs the fit
Needed Parameters (key-word):
  function: function with 2 arguments:
    array-like object for parameters (float-like)
    array-like object for variables (float-like)
  par0: array-like object for parameters prior (float-like)
  par_names: array-like object for parameters prior (string)
  file_name: csv with data
Returns:
  tuple with array of parameters and pvalue
'''

def fit(function=None, par0=None, par_names=None,
        x=None, y=None, sx=None, sy=None,
        xlabel="", ylabel="", color="", title="", xres = 1000, ax1=None, ax2=None):

  fit_data = odr.RealData(x, y=y, sx=sx, sy=sy)
  model = odr.Model(function)
  fit = odr.ODR(fit_data, 
                model, 
                beta0=par0)
  out = fit.run()

  par = out.beta
  par_s = out.sd_beta
  for i in range(len(par_names)):
    print(f'{par_names[i]} : {par[i]:.3f} +- {par_s[i]:.3f}')

  ax1.errorbar(x, y, xerr=sx, yerr=sy,
    fmt='o', markersize=4, color=color,
  )
  d_x = max(x)-min(x)
  x = np.linspace(min(x)-d_x/10, max(x)+d_x/10, xres)
  d_y = max(y)-min(y)
  ax1.set_ylim(min(y)-d_y/10, max(y)+d_y/10)
  ax1.plot(x, function(par, x), color=color, antialiased=True)
  ax1.set(xlabel=xlabel, ylabel=ylabel, title=title)
  '''
  kolmogorov-smirnov test on normalized residuals is performed
  it tests the similarity between normalized residuals and a normalized gaussian
  this similarity implies a reasonable belief in goodnes of fit and
  correct estimation of uncertainties
  if pvalue is > 0.05 the fit is accepted
  '''
  y_res_norm = out.eps/sy
  ax2.hist(y_res_norm)
  ax2.set_title("Residuals histogram")
  pvalue = kstest(y_res_norm, 'norm').pvalue
  print(f"p_value: {pvalue:.3f}")
  return out


def gauss(par, x):
    amp, mean, sigma = par
    return amp*np.exp(-(((x-mean)**2)/(2*sigma**2)))/(sigma*np.sqrt(2*np.pi))

A = [89, 177, 261, 490]

fig3, ax2 = plt.subplots(figsize=(20, 10))
fig4, axs2 = plt.subplots(len(cycles), 1, figsize=(5, 5))

fig1, axs0 = plt.subplots(1, len(cycles), figsize=(20, 10))
fig2, axs1 = plt.subplots(1, len(cycles), figsize=(5, 5))

#esempio per phase_peaks
for i in range(len(cycles)):

  temp = phase_peaks[i]
  temp = temp[~np.isnan(temp)]

  temp = temp * 1.153
  amp = 5000     # bisogna inserire dei valori approssimativi per la gaussiana da fittare
  mean = A[i]
  sigma = 5

  x_min = 50     # vanno regolati in base alla necessità
  x_max = 550
  n_bins = 300
  bin_width = (x_max - x_min)/n_bins


  binned_data, bins, _ = ax2.hist(temp, bins=n_bins, label=f'{cycles[i]} cycles', histtype='step', range = (x_min, x_max), color=colors[i])
  center_bins = [ bins[i]+0.5*bin_width for i in range(len(bins)-1) ]

  out = fit(gauss, y = binned_data, x = center_bins, sy = np.sqrt(binned_data+1), sx = 0.0001,
    par0 = [amp, mean, sigma], par_names=['amp', 'mean', 'sigma'],
    ax1=ax2, ax2=axs2[i], xlabel=r"Phase (mrad)", ylabel="Counts",
    title=r'Histogram', color=colors[i])

  n_bins = 20
  x_min, x_max = out.beta[1]-3*out.beta[2], out.beta[1]+5*out.beta[2]
  bin_width = (x_max - x_min)/n_bins
  binned_data, bins, _ = axs0[i].hist(temp, bins=n_bins, label=f'{cycles[i]} cycles', histtype='step', range = (x_min, x_max), color=colors[i])
  center_bins = [ bins[i]+0.5*bin_width for i in range(len(bins)-1) ]

  out = fit(gauss, y = binned_data, x = center_bins, sy = np.sqrt(binned_data+1), sx = 0.0001,
    par0 = [amp, mean, sigma], par_names=['amp', 'mean', 'sigma'],
    ax1=axs0[i], ax2=axs1[i], xlabel=r"Phase (mrad)", ylabel="Counts",
    title=r'Histogram', color=colors[i])

  axs0[i].set_ylim(0, 600)
  axs0[i].legend()

  phase_mu[i] = out.beta[1]
  phase_mus[i] = out.sd_beta[1]
  phase_std[i] = out.beta[2]
  phase_stds[i] = out.sd_beta[2]

plt.show()

fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots()

out = fit(
  lambda par, x: par[0]+par[1]*x,
  x = cycles, y=phase_mu,
  sy = phase_std, sx=0.0001,
  par0=[0, 5.8], par_names=["a", "b"],
  ax1=ax1, ax2=ax2, xlabel=r"Cycles", ylabel=r"Phase (mrad)", title="", color="blue")

plt.show()

fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots()

out = fit(
  lambda par, x: par[0]+par[1]*0.0031*x,
  x = phase_mu, y=phase_std**2,
  sy = 2*phase_stds*phase_std, sx=0.01*phase_mus,
  par0=[0, 5.5], par_names=["a", "k"],
  ax1=ax1, ax2=ax2, xlabel=r"Phase (mrad)", ylabel=r"Variance ($mrad^2$)", title="Calibration fit", color="blue")

plt.show()
