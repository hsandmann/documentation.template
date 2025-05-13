from datetime import datetime
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
import pandas as pd
from io import StringIO

num_days = 250
num_simulations = 200
order_poly = 1

ticker = '^BVSP'

info = yf.Ticker(ticker)
data = info.history(period='2y')

close = data['Close']
daily_return = close.pct_change()

x = np.linspace(1, len(close), len(close))
f = np.poly1d(np.polyfit(x, close, order_poly))
xs = np.linspace(max(x), max(x) + num_days, num_days)

sigma = daily_return.std()
mu = daily_return.mean()

simulated_prices = np.zeros((num_days, num_simulations))

for i in range(num_simulations):
    simulated_prices[0][i] = close[-1]
    for j in range(1, num_days):
        daily_return = np.random.normal(mu, sigma)
        simulated_prices[j][i] = simulated_prices[j-1][i] * (1 + daily_return)

simulated_means = np.mean(simulated_prices, axis=1)
simulated_stds = np.std(simulated_prices, axis=1)

fig, ax = plt.subplots(1, 1, figsize=(12, 8))
ax.plot(
    x, close,
    x, f(x), 'r:',
    xs, simulated_prices,
    xs, simulated_means,
    xs, simulated_means + 1*simulated_stds, 'w:',
    xs, simulated_means - 1*simulated_stds, 'w:',
    xs, simulated_means + 2*simulated_stds, 'k:',
    xs, simulated_means - 2*simulated_stds, 'k:',
    xs, f(xs), 'g',
)
ax.set_xlim(min(x), max(xs))

buffer = StringIO()
plt.savefig(buffer, format="svg")
print(buffer.getvalue())