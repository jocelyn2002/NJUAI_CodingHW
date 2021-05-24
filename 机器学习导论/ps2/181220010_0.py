import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

# 训练
x_train=pd.read_csv('train_feature.csv')
x_train['add_column'] = 1
y_train=pd.read_csv('train_target.csv')
x_train = x_train.values
y_train = y_train.values
beta = np.matmul(np.matmul(np.linalg.pinv(np.matmul(x_train.T,x_train)),x_train.T),y_train)


# 验证
x_val=pd.read_csv('val_feature.csv')
x_val['add_column'] = 1
y_val=pd.read_csv('val_target.csv')
x_val = x_val.values
y_val = y_val.values

theta = 0.5

y_predict = list()
for xi in x_val:
    z=np.dot(beta.T,xi)
    f = 1 / (1+np.e ** (-z[0]))
    y_predict.append(1 if f>theta else 0)

TP=TN=FP=FN=0
for i in range(len(y_predict)):
    if y_predict[i]==1 and y_val[i]==1:
        TP+=1
    elif y_predict[i]==1 and y_val[i]==0:
        FP+=1
    elif y_predict[i]==0 and y_val[i]==1:
        FN+=1
    else:
        TN+=1

print("theta = 0.5时")
print("准确率acc:",(TP+TN)/(TP+TN+FP+FN))
print("查准率P:",(TP)/(TP+FP))
print("查全率R:",TP/(TP+FN))

# 寻找最优theta
c = list()
acc = list()
p = list()
r = list()
max = [0,0]
for i in range(1,500):
    theta = i/500
    c.append(theta)

    y_predict = list()
    for xi in x_val:
        z=np.dot(beta.T,xi)
        f = 1 / (1+np.e ** (-z[0]))
        y_predict.append(1 if f>theta else 0)

    TP=TN=FP=FN=1
    for i in range(len(y_predict)):
        if y_predict[i]==1 and y_val[i]==1:
            TP+=1
        elif y_predict[i]==1 and y_val[i]==0:
            FP+=1
        elif y_predict[i]==0 and y_val[i]==1:
            FN+=1
        else:
            TN+=1
    if ((TP+TN)/(TP+TN+FP+FN)+(TP)/(TP+FP)+TP/(TP+FN)>max[0]):
        max[0]=(TP+TN)/(TP+TN+FP+FN)+(TP)/(TP+FP)+TP/(TP+FN)
        max[1]=theta
    acc.append((TP+TN)/(TP+TN+FP+FN))
    p.append((TP)/(TP+FP))
    r.append(TP/(TP+FN))

plt.plot(c,acc,label='acc')
plt.plot(c,p,label='p')
plt.plot(c,r,label='r')
plt.legend()
plt.show()
print("最佳theta: ",max[1])

# 预测
theta = max[1]
x_test=pd.read_csv('test_feature.csv')
x_test['add_column'] = 1
x_test = x_test.values

y_predict = list()
for xi in x_test:
    z=np.dot(beta.T,xi)
    f = 1 / (1+np.e ** (-z[0]))
    y_predict.append(1 if f>theta else 0)
y_predict = pd.DataFrame(y_predict)
y_predict.to_csv('181220010_0.csv',header=0,index=0)