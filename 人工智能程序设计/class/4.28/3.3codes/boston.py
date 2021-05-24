import matplotlib.pyplot as plt
from sklearn import datasets, preprocessing
import pandas as pd
import numpy as np

# boston = datasets.load_boston()
# boston_df = pd.DataFrame(boston.data[:, 4:7])
# boston_df.columns = boston.feature_names[4:7]
#
# # boston_df = (boston_df - boston_df.mean())/(boston_df.std())
# scaler = preprocessing.scale(boston_df)
# print(scaler)
#
iris = datasets.load_iris()
iris_df = pd.DataFrame(iris.data)
iris_df.columns = iris.feature_names
iris_df['target'] = iris.target
# print(iris_df.sample(10,replace=True))
# print(iris_df[iris_df.target == 1].sample(10))
# d = {0: 0.1, 1: 0.2, 2: 0.3}
# print(iris_df.groupby('target').apply(lambda x: x.sample(frac=d[x.name])))


# h = np.random.randint(1,10,100000)
# # plt.hist(h)
# # bins = np.linspace(h.min(),h.max(),3,endpoint=True)
# bins = np.array([1,3,6,9])
# plt.hist(h,bins, rwidth=0.95)
# print(bins)


# a=np.array([[2,-3,1],[3,2,0],[1,1,1]])
# b=np.array([1,13,16]).reshape(-1,1)
# x = np.linalg.solve(a,b)
# print(x)

#最小二乘法, y = a0+a1*x
def zxecf(a):
    return (len(a))
