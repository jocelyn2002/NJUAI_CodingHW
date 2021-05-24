import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA,TruncatedSVD
import plotly.graph_objs as go
import plotly.offline as of

music_list = ['钢琴', '吉他', '小提琴', '电音', '萨克斯', 'vocal', 'rap', '长笛']
p = list()
for i in range(0, len(music_list)):
    p.append(pd.read_csv(r'D:\OneDrive - smail.nju.edu.cn\desktop\music_classification\全分类表\\'
                         + music_list[i] + '.csv'))
    p[i]['曲风'] = music_list[i]
data = p[0]
for i in range(1, 8):
    data = data.append(p[i], ignore_index=True)
data = p[0]
for i in range(1, 7):
    data = data.append(p[i], ignore_index=True)
colors = {'钢琴': 'red',
          '吉他': 'orange',
          '小提琴': 'yellow',
          '电音': 'green',
          '萨克斯': 'indigo',
          'vocal': 'blue',
          'rap': 'purple',
          '长笛': 'black'}
color = []
for i in data.index:
    color.append(colors[data.loc[i, '曲风']])
svd1 = TruncatedSVD(n_components=3)
data1 = svd1.fit_transform(data.iloc[:, :-1])
scatter0 = go.Scatter3d(
    x=data1[:, 0],
    y=data1[:, 1],
    z=data1[:, 2],
    mode='markers',
    marker=dict(
        size=2,
        color=color,
        opacity=0.5
    )
)
svd2 = TruncatedSVD(n_components=2)
data2 = svd2.fit_transform(data.iloc[:, :-1])
scatter1 = go.Scatter(
    x=data1[:, 0],
    y=data1[:, 1],
    mode='markers',
    marker=dict(
        size=5,
        color=color,
        opacity=0.5
    )
)
of.plot([scatter0], filename=r'D:\OneDrive - smail.nju.edu.cn\desktop\music_classification\图库\7分类3d')
of.plot([scatter1], filename=r'D:\OneDrive - smail.nju.edu.cn\desktop\music_classification\图库\7分类2d')
print('ok')
