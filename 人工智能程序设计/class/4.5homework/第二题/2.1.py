import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# 2.1
pufa = ts.get_hist_data('600000', '2019-01-01', '2019-03-31')
pufa = pufa.loc[:, ['open', 'high', 'close', 'low', 'volume']]
pufa['date'] = pufa.index
pufa.index = range(1, len(pufa)+1)
pufa = pufa.sort_values(by='date')
pufa.index = range(1, len(pufa)+1)
# 2.2
lowest = pufa.sort_values(by='volume')[:1]
highest = pufa.sort_values(by='volume')[-1:]
print(lowest.iloc[0, 5], lowest.iloc[0, 4])
print(highest.iloc[0, 5], highest.iloc[0, 4])
print()
# 2.3
morethan1m = pufa[pufa.volume > 500000]
print(morethan1m)
print()
# 2.4
higher = pufa[pufa.open < pufa.close]
higher_days = len(higher)
print(higher_days)
print()
# 2.5
pufa_open = pufa.loc[:, 'open']
pufa_differ = pufa_open.diff()
print(pufa_differ)
pufa_zhangdie = np.sign(pufa_differ)
print(pufa_zhangdie)
print()
# 2.6
pufa_close = pufa.loc[:, 'close']
pufa_close_1 = pufa_close[pufa_close.index <= 22]
pufa_mean_1 = np.mean(pufa_close_1)
print(pufa_mean_1)
pufa_close_2 = pufa_close[(pufa_close.index <= 37) & (pufa_close.index >= 23)]
pufa_mean_2 = np.mean(pufa_close_2)
print(pufa_mean_2)
pufa_close_3 = pufa_close[pufa_close.index > 37]
pufa_mean_3 = np.mean(pufa_close_3)
print(pufa_mean_3)
# 2.7
pufa_high = pufa.loc[:, 'high']
pufa_high_1 = pufa_high[pufa_high.index <= 22]
pufa_low = pufa.loc[:, 'low']
pufa_low_1 = pufa_low[pufa_low.index <= 22]
fig1 = plt.figure(0)
plt.plot(pufa_high_1)
plt.plot(pufa_low_1)
plt.show()
# 2.8
fig = plt.figure(1)
pufa['cha'] = pufa.close - pufa.open
plt.scatter(pufa.volume, pufa.cha)
plt.show()


