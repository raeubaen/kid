
import numpy as np
import matplotlib.pyplot as plt
	
Butter = np.loadtxt('scope_8.txt' , delimiter=',')
#number = Butter[:, 0]
#freqHz = Butter[:, 1]
#ampVpp = Butter[:, 2]
#gaindB = Butter[:, 3]
#phasedeg = Butter[:, 4]

Bessel = np.loadtxt('scope_6.csv' , delimiter=',')
#number = Bessel[:, 0]
#freqHz = Bessel[:, 1]
#ampVpp = Bessel[:, 2]
#gaindB = Bessel[:, 3]
#phasedeg = Bessel[:, 4]

#plot
fig, LPF = plt.subplots()

LPF1 = LPF.twinx()
LPF.plot(Butter[:, 1], Butter[:, 3], 'ob-', linewidth=0.5, markersize=2)
LPF.grid(True, which="both", ls="-", linewidth=0.5)
LPF1.plot(Butter[:, 1], Butter[:, 4], 'or-', linewidth=0.5, markersize=2)

LPF.set_xscale('log')
LPF1.set_xscale('log')

LPF.set_xlabel('Frequency(Hz)')
LPF.set_ylabel('Gain(dB)', color='b')
LPF1.set_ylabel('Phase(deg)', color='r')

plt.title('Butterworth/Sallen-Key 2nd order low pass filter')

plt.show()

#plot bessel

fig, LPF = plt.subplots()

LPF1 = LPF.twinx()
LPF.plot(Bessel[:, 1], Bessel[:, 3], 'ob-', linewidth=0.5, markersize=2)
LPF.grid(True, which="both", ls="-", linewidth=0.5)
LPF1.plot(Bessel[:, 1], Bessel[:, 4], 'or-', linewidth=0.5, markersize=2)

LPF.set_xscale('log')
LPF1.set_xscale('log')

LPF.set_xlabel('Frequency(Hz)')
LPF.set_ylabel('Gain(dB)', color='b')
LPF1.set_ylabel('Phase(deg)', color='r')

plt.title('Bessel 3nd order low pass filter')

plt.show()

#plot gain comparison
fig, LPF = plt.subplots()

LPF.plot(Butter[:, 1], Butter[:, 3], 'ob-', linewidth=0.5, markersize=2)
LPF.grid(True, which="both", ls="-", linewidth=0.5)
LPF.plot(Bessel[:, 1], Bessel[:, 3], 'og-', linewidth=0.5, markersize=2)

LPF.set_xscale('log')

plt.legend(['Butterworth 2nd order', 'Bessel 3d order'])

LPF.set_xlabel('Frequency(Hz)')
LPF.set_ylabel('Gain(dB)', color='k')

plt.title('Low Pass filters gain comparison')

plt.show()

#phase comparison
fig, LPF = plt.subplots()

LPF.plot(Butter[:, 1], Butter[:, 4], 'or-', linewidth=0.5, markersize=2)
LPF.grid(True, which="both", ls="-", linewidth=0.5)
LPF.plot(Bessel[:, 1], Bessel[:, 4], 'om-', linewidth=0.5, markersize=2)

#LPF.set_xscale('log')

plt.legend(['Butterworth 2nd order', 'Bessel 3d order'])

LPF.set_xlabel('Frequency(Hz)')
LPF.set_ylabel('Phase(deg)', color='k')

plt.title('Low Pass filters phase comparison')

plt.show()

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
    print(f'{par_names[i]} : {par[i]:.3f} +- {par_s[i]:.3f}')

  ax1.errorbar(x, y, xerr=sx, yerr=sy,
    ecolor='red', fmt='o', color='red', markersize=4
  )
  d_x = max(x)-min(x)
  x = np.linspace(min(x)-d_x/10, max(x)+d_x/10, xres)
  d_y = max(y)-min(y)
  ax1.set_ylim(min(y)-d_y/10, max(y)+d_y/10)
  ax1.plot(x, function(par, x), color='black', antialiased=True)
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

def linear(par, f):
  return par[0]*f+par[1]

Bessel = Butter[Butter[:, 1]<50000]

fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots(figsize=(5, 5))
out = fit(linear, x = Bessel[:, 1], y = Bessel[:, 4], sy = np.ones((Bessel.shape[0]))*0.01, sx = np.ones((Bessel.shape[0]))*0.01,
    par0 = [1, 1], par_names=['a', 'b'],
    ax1=ax1, ax2=ax2, xlabel=r"$Freq. $ [Hz]", ylabel="Phase",
    title=r'Phase response', xres=500)
plt.show()

