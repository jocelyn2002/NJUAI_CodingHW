import pandas as pd
a = pd.read_csv('181220010_0.csv').values
b = pd.read_csv('181220010_1.csv').values
c = 0
for i in range(len(a)):
    if a[i] != b[i]:
        c+=1
print(c)