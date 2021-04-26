from scipy.optimize import curve_fit
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def func(x, k, i0, q0):
    i, q = x
    return k*np.sqrt((i-i0)**2 + (q-q0)**2)

df = pd.read_csv("iq.csv")
df.columns = ["a", "i", "q"]

print(df)


out = curve_fit(func, (df.i, df.q), df.a, bounds = ([0.5, -18, 19], [5, -16, 21]))
print(out)

popt, _ = out
k, i0, q0 = popt
plt.scatter(df.a, np.sqrt((df.i-i0)**2 + (df.q-q0)**2))

x = np.linspace(0, 10, 30)
plt.plot(x, x/k)
plt.show()
