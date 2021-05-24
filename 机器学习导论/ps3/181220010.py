import pandas as pd
import numpy as np
from cvxopt import matrix, solvers
solvers.options['show_progress'] = False
import numpy as np
x_train = pd.read_csv("ML20_PS3_programming/X_train.csv",header=None).values
y_train = pd.read_csv("ML20_PS3_programming/y_train.csv",header=None).values
for i in range(len(y_train)):
    if y_train[i] == 0:
        y_train[i] = -1
x_valid = x_train[-100:,:]
y_valid = y_train[-100:,:]
x_train = x_train[:-100,:]
y_train = y_train[:-100,:]
m = len(y_train)
# print("m=",m)


# 第一题
P = np.zeros([m,m]).tolist()
for i in range(m):
    for j in range(m):
        P[j][i] = y_train[i][0]*y_train[j][0]*np.dot(np.array(x_train[i]),np.array(x_train[j]))
P = matrix(P)
# print("p:",P.size)

q = -np.ones(m)
q = matrix(q)
# print("q:",q.size)

G = -np.identity(m)
G = matrix(G)
# print("g:",G.size)

h = np.zeros(m)
h = matrix(h)
# print("h:",h.size)

A = np.ones(m).tolist()
for i in range(m):
    A[i]=y_train[i][0] / 1.0
A=matrix(A,(1,m))
# print("a:",A.size)

b = matrix([0.0])
# print("b:",b.size)


result_1 = solvers.qp(P,q,G,h,A,b)
alpha_1 = list(result_1['x'])
print("QP包运算完成")
x_train = np.array(x_train)
w_1 = 0
for i in range(m):
    w_1 += alpha_1[i]*y_train[i]*x_train[i]
S = list()
for i in range(m):
    if alpha_1[i]>0:
        S.append(i)
b_1 = 0
for s in S:
    b_1 += y_train[s] / 1.0
    for i in S:
        b_1 -= alpha_1[i]*y_train[i]*np.dot(x_train[i],x_train[s])
b_1 /= len(S)
print(w_1,b_1)


# 第二题
# 计算样本最大间隔组合
dic = dict()
for i in range(len(x_train)):
    most_gap = 0
    for j in range(len(x_train)):
        gap = np.linalg.norm(x_train[i,:]-x_train[j,:])
        if gap>most_gap:
            most_gap = gap
            dic.update({i:j})


# 最大迭代次数
times = 100
alpha = np.zeros(m)
w = np.zeros(len(x_train[0]))
b = 1
def f(x):
    return np.dot(w,x) + b
def nI(x):
    if (x==True):
        return 1
    else:
        return 0
def E(i):
    return f(x_train[i]) - y_train[i]
def K(i,j):
    return np.dot(x_train[i],x_train[j])
def miu(i,j):
    return K(i,i)+K(j,j)-2*K(i,j)
def clipp(raw,i1,i2):
    L = 0
    if y_train[i1] != y_train[i2]:
        L = max(0,alpha[i2]-alpha[i1])
    else:
        L = 0

    if raw < L:
        return L
    else:
        return raw
for time in range(times):
    # 选取违背KKT条件最多的alpha_i
    mkkt = 0
    mi = 0
    for i in range(m):
        kkt = nI(alpha[i]>=0) - (y_train[i]*f(x_train[i])-1) + abs(alpha[i]*(y_train[i]*f(x_train[i])-1)==0)
        if kkt > mkkt:
            mkkt = kkt
            mi = i
    
    i1 = mi
    i2 = dic[mi]

    alpha_i2_old = alpha[i2]
    alpha_i2_new = alpha[i2] + y_train[i2]*(E(i1)-E(i2)) / miu(i1,i2)

    alpha[i2] = clipp(alpha_i2_new,i1,i2)
    alpha[i1] = alpha[i1] + y_train[i1]*y_train[i2]*(alpha[i2]-alpha_i2_old)

    w = np.zeros(len(x_train[0]))
    for i in range(m):
        w += alpha[i]*y_train[i]*x_train[i]

    b = y_train[i1] - alpha[i1]*y_train[i1]*K(i1,i1) - alpha[i2]*y_train[i2]*K(i2,i1)
    for i in range(m):
        if i==i1 or i== i2:
            continue
        b -= alpha[i]*y_train[i]*K(i,i1)

print("SMO方法优化完成")

w_2 = 0
for i in range(m):
    w_2 += alpha[i]*y_train[i]*x_train[i]
S = list()
for i in range(m):
    if alpha[i]>0:
        S.append(i)
b_2 = 0
for s in S:
    b_2 += y_train[s] / 1.0
    for i in S:
        b_2 -= alpha[i]*y_train[i]*np.dot(x_train[i],x_train[s])
b_2 /= len(S)
print(w_2,b_2)



# 第三题
acc_1 = 0
for i in range(len(x_valid)):
    yp = 1 if np.dot(w_1,x_valid[i])+b_1 >= 1 else -1
    if yp == y_valid[i]:
        acc_1 += 1
acc_1 /= len(x_valid)
print(acc_1)

acc_2 = 0
for i in range(len(x_valid)):
    yp = 1 if np.dot(w_2,x_valid[i])+b_2 >= 1 else -1
    if yp == y_valid[i]:
        acc_2 += 1
acc_2 /= len(x_valid)
print(acc_2)


x_test = pd.read_csv("ML20_PS3_programming/X_test.csv",header=None).values
y_test = list(0 for i in range(len(x_test)))
for i in range(len(x_test)):
    y_test[i] = 1 if np.dot(w_2,x_test[i])+b_2 >= 1 else 0


y_test = pd.DataFrame(y_test)
y_test.to_csv("181220010_丁豪.csv",index=False,header=False)