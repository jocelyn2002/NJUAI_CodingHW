import pandas as pd
import os

# 数据初始化
train_data = pd.read_csv("./Naive Bayesian Classifier/train_data.csv")
test_data = pd.read_csv("./Naive Bayesian Classifier/test_data.csv")
train_x=train_data.iloc[:,:-1]
train_y=train_data.iloc[:,-1]
test_x=test_data
total = len(train_data.index)
print(train_y[1])
# print(train_x.iloc[139,:].values)
# print ((train_x.iloc[1,:].values==train_x.iloc[1,:].values).all())


# 因为y只有两个值，所以实际上只需比较x=x0时，y哪一个值出现的更多，就可以判断为这一个类
def get_predict(data):
    # num_xi=0
    num_xi_yi=[0,0]
    
    for i in train_data.index:
        if (train_x.iloc[i,:].values==data).all():
            # num_xi+=1
            num_xi_yi[train_y[i]]+=1
    
    if num_xi_yi[0]>=num_xi_yi[1]:
        return 0
    else:
        return 1


predict = list();
for i in test_x.index:
    predict.append(get_predict(test_x.iloc[i,:].values))
print(predict)



# 检测一下正确率
right=0
for i in train_data.index:
    if train_y[i]==get_predict(train_x.iloc[i,:].values):
        right+=1
print(right)
# 结果为135，正确率还可以
