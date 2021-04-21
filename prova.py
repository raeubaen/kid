import matplotlib.pyplot as plt
from brokenaxes import brokenaxes
import numpy as np

fig = plt.figure(figsize=(5, 2))
bax = brokenaxes(xlims=((0, .1), (.4, .7)), hspace=.05)#, ylims=((-1, .7), (.79, 1)))
x = np.linspace(0, 1, 100)
bax.hist(x)
bax.legend(loc=3)
bax.set_xlabel('time')
bax.set_ylabel('value')
plt.show()

