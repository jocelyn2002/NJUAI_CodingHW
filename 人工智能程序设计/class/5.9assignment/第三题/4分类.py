from sklearn.decomposition import PCA
import pandas as pd
import plotly.graph_objs as go
import plotly.offline
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.model_selection import train_test_split
import numpy as np

data = pd.read_csv('dataset.csv', names=range(0,12))
data = data.iloc[:, :-1]
A = ['','','','']
A[0] = pd.DataFrame(data[data[0] == 'A'].iloc[:, 1:].values)
A[1] = pd.DataFrame(data[data[0] == 'B'].iloc[:, 1:].values)
A[2] = pd.DataFrame(data[data[0] == 'C'].iloc[:, 1:].values)
A[3] = pd.DataFrame(data[data[0] == 'D'].iloc[:, 1:].values)
print(A[0])
# 自己的pca
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
trace = [ ]
for j in range(0, 4):
    A[j] = pd.DataFrame(pca(A[j], 2))
    trace.append(go.Scatter3d(
        x=[float(i) for i in A[j].iloc[:, 1].values],
        y=[float(i) for i in A[j].iloc[:, 0].values],
        z=[j for i in A[j].iloc[:, 1:2].values],
        mode='markers',
        marker=dict(
            size=6,
            line=dict(
                width=0.5
            ),
            opacity=0.8
        )
    ))
plotly.offline.plot(trace, filename='降维分析_自己的pca')


# sklearn pca
trace = []
pca = PCA(n_components=2)
for j in range(0, 4):
    pca.fit(A[j])
    A[j] = pd.DataFrame(pca.transform(A[j])).astype('float')
    trace.append(go.Scatter3d(
        x=[float(i) for i in A[j].iloc[:, 1:2].values],
        y=[float(i) for i in A[j].iloc[:, 0:1].values],
        z=[j for i in A[j].iloc[:, 1:2].values],
        mode='markers',
        marker=dict(
            size=1,
            line=dict(
                width=0.5
            ),
            opacity=0.8
        )
    ))
plotly.offline.plot(trace, filename='降维分析_sklearn_pca')


# 逻辑斯蒂分类
x_train,x_test,y_train,y_test=train_test_split(data.iloc[:,1:],data.iloc[:,0:1],test_size=0.2,random_state=0)
lr=LogisticRegression()
lr.fit(x_train,y_train)
y_pred = lr.predict(x_test)
# 结果评价
con = 0
for i in range(0, len(y_pred)):
    if y_pred[i]==y_test.iloc[i,:].values:
        con+=1
print(con/len(y_pred))