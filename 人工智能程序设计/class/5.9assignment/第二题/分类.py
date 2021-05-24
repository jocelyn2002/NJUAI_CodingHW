from sklearn.decomposition import PCA
import pandas as pd
import plotly.graph_objs as go
import plotly.offline
from sklearn.linear_model import LinearRegression
import sklearn.model_selection
from sklearn import metrics

# 降维数据观察
data = pd.read_csv('wdbc.csv', names=range(0, 32))
data = data.iloc[:, 1:]
pca = PCA(n_components=2)
pca.fit(data.iloc[:, 1:])
y = pd.DataFrame([1 if item == 'M' else 0 for item in data.iloc[:, 0:1].values])
x = pd.DataFrame(pca.transform(data.iloc[:, 1:])).astype('float')
trace1 = go.Scatter3d(
    x=[float(i) for i in x.iloc[:, 1:2].values],
    y=[float(i) for i in x.iloc[:, 0:1].values],
    z=[float(i) for i in y.values],
    mode='markers',
    marker=dict(
        size=6,
        line=dict(
            color='rgba(217, 217, 217, 0.14)',
            width=0.5
        ),
        opacity=0.8
    )
)
plotly.offline.plot([trace1], filename='降维分析')


# 分类
x_train, x_test, y_train, y_test = \
    sklearn.model_selection.train_test_split(x, y, test_size=0.2, random_state=0)
linreg = LinearRegression()
linreg.fit(x_train, y_train)
y_predict = linreg.predict(x_test)
y_predict = pd.DataFrame(y_predict)
y_test = pd.DataFrame(y_test.values)
p1 = (metrics.mean_squared_error(y_test, y_predict))**0.5 # 预测值（0-1之间）的标准差
C = 0.4 # 为了调整识别率设定的常数
y_predict = [1 if i >= C else 0 for i in linreg.predict(x_test)]
y_test = y_test.values
con = 0
for i in range(0,len(y_predict)):
    if y_predict[i] < y_test[i]:
        con+=1
p3 = con/len(y_predict) # 错误率
y_predict = pd.DataFrame(y_predict)
y_test = pd.DataFrame(y_test)
p2 = (metrics.mean_squared_error(y_test, y_predict))**0.5 # 预测值化成0或1后的标准差
print(p1)
print(p2)
print(p3)
