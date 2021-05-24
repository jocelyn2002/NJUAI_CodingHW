import pandas as pd
import numpy as np


# 数据处理 用均值填补 '？'
house = pd.read_csv('house-votes-84.csv', names=range(0, 17))
house.replace(('n', 'y'), (0, 1), inplace=True)

# 手动实现replace方法
# for j in house.columns:
#     nu = len(house.index)
#     su = 0
#     for i in house.index:
#         if house.iloc[i, j] == 'y':
#             house.iloc[i, j] = 1
#         elif house.iloc[i, j] == 'n':
#             house.iloc[i, j] = 0
#         elif house.iloc[i, j] == 'republican':
#             house.iloc[i, j] = 1
#         elif house.iloc[i, j] == 'democrat':
#             house.iloc[i, j] = 0
#         else:
#             nu -= 1
#         if house.iloc[i, j] != '?':
#             su += int(house.iloc[i, j])
#     me = su/nu
#     for i in house.index:
#         if house.iloc[i, j] == '?':
#             house.iloc[i, j] = me

for j in range(1,len(house.columns)):
    nu = len(house.index)
    su = 0
    for i in house.index:
        if house.iloc[i, j] == '?':
            nu -= 1
        else:
            su += int(house.iloc[i, j])
    me = su/nu
    for i in house.index:
        if house.iloc[i, j] == '?':
            house.iloc[i, j] = me
print(house)

# 开始k-means聚类
house[17] = -1  # 17列用于表示聚类
k = 2
p = np.random.randint(low=0, high=len(house.index), size=k)
print(p)
# 以下两个函数都以 坐标 列表作为参数，返回数值
def distance2(a, b):
    su = 0
    for j in range(0,len(a)):
        su += (a[j] - b[j])**2
    return su
# 以下函数以datafram作为参数，返回 坐标 列表
def find_center(a):
    data = []
    for j in a.columns:
        data.append(a[j].mean())
    return data
# 生成初始中心
center = []
for cla_num in range(0, k):
    center.append(list(house.iloc[p[cla_num], 1:]))
print(center)

# 循环直至聚类结果不变
counter = 1  # 统计聚类次数
while True:
    # 归类
    for i in house.index:
        d = []
        for cla_num in range(0, k):
            d.append(distance2(list(house.iloc[i, 1:]), center[cla_num]))
        min = 0
        for cla_num in range(1, k):
            if d[cla_num] < d[min]:
                min = cla_num
        house.iloc[i, 17] = min
    # 产生新中心
    newcenter = []
    for cla_num in range(0, k):
        thisclass = house[house[17] == cla_num].iloc[:, 1:]
        newcenter.append(find_center(thisclass))
    # 退出条件 聚类不变
    if newcenter == center:
        break
    else:
        counter += 1
        center = newcenter
print(house)
print(counter)


# 结果评估，可视化以下
import plotly.graph_objs as go
import plotly.offline
y1 = [1 if i == 'democrat' else 0 for i in house[0]]
y2 =[1 if y1[i] == list(house[17])[i] else 0 for i in range(0,len(house.index))]
co = 0
for i in range(0, len(y2)):
    if y2[i] == 1:
        co += 1
accuracy = co/len(house.index)
if accuracy < 0.5:
    y2 = [1 if y2[i]==0 else 0 for i in range(0, len(y2))]
co = 0
for i in range(0, len(y2)):
    if y2[i] == 1:
        co += 1
accuracy = co/len(house.index)
print('accuracy rate of party:', accuracy)
trace1 = go.Scatter(
    x=np.linspace(0, 100, len(house.index)),
    y=y2,
    mode='markers',
)
plotly.offline.plot([trace1], filename='结果评价')
