import pandas as pd
import plotly
import plotly.graph_objs as go
import sklearn.model_selection
import sklearn.decomposition
from sklearn import metrics
from sklearn.linear_model import LinearRegression
import numpy as np
# 数据预处理
gupiao = pd.read_csv('data_akbilgic.csv')
co = gupiao[0:1].values[0]
co = co[1:]
co[0] += '_TL_BASED'
co[1] += '_USD_BASED'
gupiao = pd.DataFrame(gupiao.iloc[1:, 1:].values, columns=co).astype(float)


# 数据降维
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
x = gupiao.iloc[:, 1:]
x = pca(x, 2)
x = pd.DataFrame(x)
y = gupiao.iloc[:, 0:1]
print(y)
print(x[0])
print(x[1])

# 画出第一项关于降维后其他项的图
scatter=[]
y_1 = list(float(u) for u in y.values)
for i in range(0,2):
    x_1 = list(float(u) for u in x[i].values)
    scatter.append(go.Scatter(
        x=y_1,
        y=x_1,
        name=str(i),
        mode='markers',
        marker=dict(
            size=3,
        )
    ))
plotly.offline.plot(scatter, filename='原始数据2.html')


# 线性回归训练

x_train, x_test, y_train, y_test = \
    sklearn.model_selection.train_test_split(x, y, test_size=0.2, random_state=888)
# print(x_train.shape)
# print(y_train.shape)
# print(x_test.shape)
# print(y_test.shape)
linreg = LinearRegression()  # 建立线性模型类实例linreg
linreg.fit(x_train, y_train)
# print(linreg.intercept_)
# print(linreg.coef_)


# 画出测试集预测值与真值的对应图
# 重写一下.predict()方法的实现
# def get_y(data):
#     y = linreg.intercept_[0]
#     for i2 in range(0, len(linreg.coef_[0])):
#         y += float(data.values[0][i2])*float(linreg.coef_[0][i2])
#     return y
# y_test_prime = []
# for i in x_test.index:
#     y_test_prime.append(get_y(x[i:i+1]))
# print(y_test_prime)
y_test = [float(i) for i in y_test.values]
y_test_prime = linreg.predict(x_test)
y_test_prime = [y_test_prime[i][0] for i in range(0,len(y_test_prime))]
plot1 = go.Scatter(
    x=np.linspace(0, 1, num=len(y_test)),
    y=y_test,
    mode='markers+lines',
    name='test'
)
plot2 = go.Scatter(
    x=np.linspace(0, 1, num=len(y_test)),
    y=y_test_prime,
    mode='markers+lines',
    name='test_prime'
)
plotly.offline.plot([plot1, plot2], filename='降维.html')

# 检查误差
p = (metrics.mean_squared_error(y_test, y_test_prime))**0.5
print(p)

# 交叉验证
from sklearn.model_selection import cross_val_predict
linreg = LinearRegression()
predicted = cross_val_predict(linreg, x, y, cv=10)
p = (metrics.mean_squared_error(y, predicted))**0.5
print(p)
