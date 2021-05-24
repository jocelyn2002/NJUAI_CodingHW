import numpy as np
import pandas as pd


def pca(df, n):
    data = df.values
    data = data-data.mean(axis=0)
    cov = np.cov(data, rowvar=False)
    values, factors = np.linalg.eig(cov)
    order = np.argsort(values)
    order = order[:-(n+1):-1]
    factors1 = factors[:, order]
    low_data = np.dot(data, factors1)
    return low_data


wine = pd.read_csv(r'D:\OneDrive - smail.nju.edu.cn\desktop\python资源\winequality-red.csv')
print(pca(wine, 2))


