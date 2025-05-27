import matplotlib.pyplot as plt
import numpy as np
from io import StringIO

eq = lambda x: np.exp(x)

x = np.linspace(-.2, 2.1)

plt.rcParams["figure.figsize"] = (15, 5)

xa = 1.5
ya = 7
k = 0.3
ka = xa - k
ak = xa + k

fig, ax = plt.subplots(1, 3)
for i in range(3):
  ax[i].axhline(0, color='gray') # x = 0
  ax[i].axvline(0, color='gray') # y = 0
  ax[i].spines['top'].set_visible(False)
  ax[i].spines['right'].set_visible(False)
  ax[i].spines['bottom'].set_visible(False)
  ax[i].spines['left'].set_visible(False)
  ax[i].plot(x, eq(x), '-r', lw=4)
  ax[i].set_xlim(min(x), max(x))
  ax[i].set_xticks([])
  ax[i].set_yticks([])
  ax[i].plot([ka, ka], [0, eq(ka)], 'g:')
  ax[i].plot([0, ka], [eq(ka), eq(ka)], 'g:')
  ax[i].plot([ak, ak], [0, eq(ak)], 'g:')
  ax[i].plot([0, ak], [eq(ak), eq(ak)], 'g:')
  ax[i].text(xa, -0.5, 'a', horizontalalignment='center', fontsize=15)
  ax[i].text(ka, -0.5, '$a-\delta$', horizontalalignment='center', fontsize=15)
  ax[i].text(ak, -0.5, '$a+\delta$', horizontalalignment='center', fontsize=15)
  ax[i].text(0, eq(ka), '$L-\epsilon$', horizontalalignment='right', verticalalignment='center', fontsize=15)
  ax[i].text(0, eq(ak), '$L+\epsilon$', horizontalalignment='right', verticalalignment='center', fontsize=15)
  
ax[0].plot([xa, xa], [0, eq(xa)], 'b:')
ax[0].plot([0, xa], [eq(xa), eq(xa)], 'b:')
ax[0].plot(xa, eq(xa), 'ro', ms=15)
ax[0].text(0, eq(xa), 'L=f(a)', horizontalalignment='right', verticalalignment='center', fontsize=15)
ax[1].plot([xa, xa], [0, eq(xa)], 'b:')
ax[1].plot([0, xa], [eq(xa), eq(xa)], 'm:')
ax[1].plot(xa, eq(xa), marker='o', ms=15, mec='red', color='white')
ax[1].text(0, eq(xa), 'L', horizontalalignment='right', verticalalignment='center', fontsize=15)
ax[2].plot(xa, eq(xa), marker='o', ms=15, mec='white', color='white')
ax[2].plot([xa, xa], [0, ya], 'b:')
ax[2].plot([0, xa], [ya, ya], 'b:')
ax[2].plot([0, xa], [eq(xa), eq(xa)], 'm:')
ax[2].plot(xa, eq(xa), marker='o', ms=15, mec='red', color='white')
ax[2].plot(xa, ya, 'ro', ms=15)
ax[2].text(0, ya, 'f(a)', horizontalalignment='right', verticalalignment='center', fontsize=15)
ax[2].text(0, eq(xa), 'L', horizontalalignment='right', verticalalignment='center', fontsize=15)

fig.tight_layout()

buffer = StringIO()
plt.savefig(buffer, format="svg", transparent=True)
print(buffer.getvalue())