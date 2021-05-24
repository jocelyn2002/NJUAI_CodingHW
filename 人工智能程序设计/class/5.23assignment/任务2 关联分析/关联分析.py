import pandas as pd
import numpy as np
import copy


car = pd.read_csv('car.data.csv')



# 寻找频繁项集
def find_first(a, support):
    # 生成后选单项集
    co = []
    for i in range(0, len(a.index)):
        for j in range(0, len(a.columns)):
            p = [a.columns[j], a.iloc[i, j]]
            if p not in co:
                co.append(p)
    # 生成频繁单项集
    n = len(a.index)
    first_segment = []
    for sp in co:
        count = 0
        for i in range(0, len(a.index)):
            for j in range(0, len(a.columns)):
                if [a.columns[j], a.iloc[i, j]] == sp:
                    count += 1
                    break
        fre = count / n
        if fre >= support:
            first_segment.append([[sp],fre])
    return first_segment
def find_all(a, support):
    n = len(a.index)
    this_list = find_first(a, support)
    final_list = copy.deepcopy(this_list)
    while this_list:
        attempt_list = []
        for this1 in range(0, len(this_list)-1):
            for this2 in range(this1+1, len(this_list)):
                attempt = copy.deepcopy(this_list[this1][0])   # attempt 为 多个原子组成的 列表
                attempt_name = []
                for i in attempt:
                    attempt_name.append(i[0])
                pl = 0
                for a2 in this_list[this2][0]:  # a2 为 原子 列表
                    if a2[0] not in attempt_name:
                        attempt.append(a2)
                        attempt_name.append(a2[0])
                        pl += 1
                if pl == 1:  # 判断长度是否n+1
                    # 判断所有子集是否频繁
                    is_se = 1
                    for i in range(0, len(attempt)):
                        attempt_ = attempt[:i]+attempt[i+1:]
                        is_seg = 0
                        for j in range(0, len(this_list)):
                            if attempt_ == this_list[j][0]:
                                is_seg = 1
                                break
                        if is_seg == 0:
                            is_se = 0
                    if is_se == 1:
                        # 判断此 n+1-项 是否是频繁项，若是则添加到频繁项集
                        con = 0
                        for i in a.index:
                            wea = 1   # weather 是否相等
                            for j in range(0, len(attempt)):
                                if a.loc[i, attempt[j][0]] != attempt[j][1]:
                                    wea = 0
                                    break
                            if wea == 1:
                                con += 1
                        fre = con/n
                        if fre >= support:  # 频率高于support
                            attempt_list.append([attempt, fre])
                            # print(attempt,fre)
        this_list = copy.deepcopy(attempt_list)
        final_list.extend(attempt_list)
    return final_list
# 关联
def connect(l, confidence):
    connection = []
    for i in range(len(l)-1, -1, -1):
        for j in range(i-1, -1, -1):
            if len(l[i][0]) == len(l[j][0])+1:
                not_in = 0
                mark = 0
                for k in range(0, len(l[i][0])):
                    if l[i][0][k] not in l[j][0]:
                        not_in += 1
                        mark = k
                if not_in == 1:
                    fre = l[i][1]/l[j][1]
                    if fre >= confidence:
                        connection.append([str(l[j][0])+'->'+str(l[i][0][mark]), fre])
    return connection


# # 对所有
# p = find_all(car, support=0.2)
# connection = connect(p, confidence=0.8)
# for i in connection:
#     print(i)
# print()
# # 对非unacc的车
# car1 = car[car.iloc[:, 6] != 'unacc']
# p = find_all(car1, support=0.2)
# connection = connect(p, confidence=0.8)
# for i in connection:
#     print(i)
# print()
# # 对最少的两种车
# car2 = car1[car1.iloc[:,6]!='acc']
# p = find_all(car2, support=0.2)
# connection = connect(p, confidence=0.8)
# for i in connection:
#     print(i)
# print()



# 聚类
car.replace(('vhigh', 'high','med','low'),(11,12,13,14), inplace=True)
car.replace(('5more', 'more'), (5, 6), inplace=True)
car.replace(('big', 'small'), (12, 14), inplace=True)
car.replace(('unacc','acc','good','vgood'),(1,2,3,4),inplace=True)
car.replace(('2','3','4'),(2,3,4),inplace=True)
# print(car)
car[7] = -1  # 7列用于表示聚类
k = 4
p = np.random.randint(low=0, high=len(car.index), size=k)
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
    for j in range(0, len(a.columns)):
        data.append(a.iloc[:,j].mean())
    return data
# 生成初始中心
center = []
for cla_num in range(0, k):
    center.append(list(car.iloc[p[cla_num], :6]))
print(center)
# 循环直至聚类结果不变
counter = 1  # 统计聚类次数
while True:
    # 归类
    print(counter)
    for i in range(0, len(car.index)):
        d = []
        for cla_num in range(0, k):
            d.append(distance2(list(car.iloc[i, :6]), center[cla_num]))
        min = 0
        for cla_num in range(1, k):
            if d[cla_num] < d[min]:
                min = cla_num
        car.iloc[i, 7] = min
    # 产生新中心
    newcenter = []
    for cla_num in range(0, k):
        thisclass = car[car[7] == cla_num].iloc[:, :6]
        newcenter.append(find_center(thisclass))
    # 退出条件 聚类不变
    if newcenter == center:
        break
    else:
        counter += 1
        center = newcenter
print(car)
print(counter)

