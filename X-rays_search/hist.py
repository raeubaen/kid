import numpy as np
import matplotlib.pyplot as plt
import matplotlib

plt.style.use("ggplot")
plt.rcParams['axes.facecolor'] = '#f7f9fc'

plt.rcParams.update({'font.size': 28})
matplotlib.rc('xtick', labelsize=24)
matplotlib.rc('ytick', labelsize=24)



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

  '''
  ax1.errorbar(x, y, xerr=sx, yerr=sy,
    fmt='o', markersize=4, color=color,
  )
  '''
  d_x = max(x)-min(x)
  #x = np.linspace(min(x)-d_x/10, max(x)+d_x/10, xres)
  x = np.arange(0, 200, 0.2)
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
  '''
  ax2.hist(y_res_norm)
  ax2.set_title("Residuals histogram")
  '''
  pvalue = kstest(y_res_norm, 'norm').pvalue
  print(f"p_value: {pvalue:.3f}")
  return out


def gauss(par, x):
    amp, mean, sigma = par
    return amp*np.exp(-(((x-mean)**2)/(2*sigma**2)))/(sigma*np.sqrt(2*np.pi))

pp = np.loadtxt("phase_peaks_new.dat")/5.7

pp_withnoise = np.loadtxt("phase_peaks_thres_7_new.dat")/5.7

p_max = pp.max()

semires = 0.5

fig, ax = plt.subplots()

binned_data, bins, _ = ax.hist(pp_withnoise, range=(0, p_max), bins=int(p_max/semires), histtype="step", label="Threshold: 7 mrad", color="red")
center_bins = [ bins[i]+0.5*semires for i in range(len(bins)-1) ]
#ax.errorbar(center_bins, binned_data, yerr=np.sqrt(binned_data), fmt=".", color="red")

binned_data, bins, _ = ax.hist(pp, range=(0, p_max), bins=int(p_max/semires), histtype="step", label="Threshold: 14 mrad", color="cyan")
center_bins = np.asarray([ bins[i]+0.5*semires for i in range(len(bins)-1) ])
#ax.errorbar(center_bins, binned_data, yerr=np.sqrt(binned_data), fmt=".", color="cyan")

'''
ind = np.logical_and(center_bins < 9, center_bins > 3.5)
out = fit(gauss, y = binned_data[ind], x = center_bins[ind], sy = np.sqrt(binned_data[ind]), sx = 0.0001,
    par0 = [50, 5.9, 0.5], par_names=['amp', 'mean', 'sigma'],
    ax1=ax, ax2=ax, xlabel=r"Phase (mrad)", ylabel="Counts",
    title=r'Histogram', color="blue")
'''
plt.title("Histogram")
plt.xlim(0, p_max)
plt.ylim(0, 50)
plt.xlabel("Energy (keV)")
plt.ylabel(f"Counts / {semires} keV")
plt.legend()
plt.show()
