import numpy as np
import matplotlib.pyplot as plt
import matplotlib

plt.rcParams.update({'font.size': 28})
matplotlib.rc('xtick', labelsize=20)
matplotlib.rc('ytick', labelsize=20)


Besselgiu = np.loadtxt('besselgiu.csv' , delimiter=',')
#number = Besselgiu[:, 0]
#freqHz = Besselgiu[:, 1]
#ampVpp = Besselgiu[:, 2]
#gaindB = Besselgiu[:, 3]
#phasedeg = Besselgiu[:, 4]

Besselsu = np.loadtxt('besselsu.csv' , delimiter=',')
#number = Bessel[:, 0]
#freqHz = Bessel[:, 1]
#ampVpp = Bessel[:, 2]
#gaindB = Bessel[:, 3]
#phasedeg = Bessel[:, 4]

x = np.arange(201, dtype=int)

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
        xlabel="", ylabel="", title="", xres = 100, ax1=None, ax2=None):

  fit_data = odr.RealData(x, y=y, sx=sx, sy=sy)
  model = odr.Model(function)
  fit = odr.ODR(fit_data, 
                model, 
                beta0=par0)
  out = fit.run()

  par = out.beta
  par_s = out.sd_beta
  for i in range(len(par_names)):
    print(f'{par_names[i]} : {par[i]} +- {par_s[i]}')

  ax1.errorbar(x, y, xerr=sx, yerr=sy,
    ecolor='red', fmt='o', color='red', markersize=4
  )
  d_x = max(x)-min(x)
  x = np.linspace(min(x)-d_x/10, max(x)+d_x/10, xres)
  d_y = max(y)-min(y)
  ax1.set_ylim(min(y)-d_y/10, max(y)+d_y/10)
  ax1.plot(x, function(par, x), color='black', antialiased=True)
  print(function(par, 10))

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
  print(f"Chi squared: {np.linalg.norm(y_res_norm)**2/len(y_res_norm)}")
  ax2.set_title("Residuals histogram")
  pvalue = kstest(y_res_norm, 'norm').pvalue
  print(f"p_value: {pvalue:.3f}")
  return out

f0 = 50000
def tf(par, f):
  s = 1j*f/f0
  return - 20 * np.log10(np.abs((par[0]*s**2 + par[1]*s + 1)*(par[2]*s + 1)))

Besselgiu = Besselgiu[Besselgiu[:, 1]<4e5]
Besselsu = Besselsu[Besselsu[:, 1]<4e5]

fig1, axs = plt.subplots(2, 1, tight_layout=True, sharex = True)
fig2, ax2 = plt.subplots(figsize=(5, 5))

axs[0].set_xscale("log")
axs[1].set_xscale("log")

sigmagiu = Besselgiu[:, 4] * 0 + 0.1
sigmasu = Besselsu[:, 4] * 0 + 0.1

par0 = [6, 15, 1]
print(tf(par0, 0))

outgiu = fit(tf, x = Besselgiu[:, 1], y = Besselgiu[:, 3], sy = sigmagiu, sx = sigmagiu,
    par0 = par0, par_names=['a', 'b', 'c'],
    ax1=axs[0], ax2=ax2, xlabel="", ylabel="Gain",
    title=r'Phase response Bessel #1', xres=500)

outsu = fit(tf, x = Besselsu[:, 1], y = Besselsu[:, 3], sy = sigmasu, sx = sigmasu,
    par0 = par0, par_names=['a', 'b', 'c'],
    ax1=axs[1], ax2=ax2, xlabel=r"Frequency (Hz)", ylabel="Gain",
    title=r'Phase response Bessel #2', xres=500)
plt.show()

pargiu = outgiu.beta
def _tf(par, shift):
  return lambda f: tf(par, f) + shift

from scipy.optimize import fsolve
print(fsolve(_tf(pargiu, 20), 50000))

parsu = outsu.beta
print(fsolve(_tf(parsu, 20), 50000))


