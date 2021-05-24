import pandas as pd
a = pd.DataFrame({'color': ['c', 'c', 'f', 'e', 'd'], 'year': [1, 2, 3, 4, 5], 'day': [1, 2, 3, 4, 5]})
b = pd.DataFrame({'color': ['c', 'c', 'f', 'd'], 'years': [6, 7, 8, 10], 'min': [1, 2, 3, 5]})
c = pd.merge(a, b, on='color', how='left')
print(c[['year', 'day']].apply(pd.DataFrame.mean))