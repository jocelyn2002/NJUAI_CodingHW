import seaborn
import pandas as pd
import matplotlib.pyplot as plt
data = pd.read_excel(r'D:\desktop\nan.xlsx')
# p = pd.DataFrame()
# p['sex'] = [1 if item == 'male' else 0 for item in data.sex]
# p['alive'] = [1 if item == 'yes' else 0 for item in data.alive]
# print(p.corr())
# data.age.fillna(method='bfill', inplace=True)
print(data.boxplot())
plt.show()
