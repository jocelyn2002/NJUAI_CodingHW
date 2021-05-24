from __future__ import print_function
import numpy as np
import pandas as pd

class KNN():
   
    #k: int,最近邻个数.
    def __init__(self, k=5):
        self.k = k

    # 此处需要填写，建议欧式距离，计算一个样本与训练集中所有样本的距离
    def distance(self, one_sample, X_train):
        dis_list = [np.linalg.norm(one_sample-X_train[i]) for i in range(len(X_train))]
        return dis_list
    
    # 此处需要填写，获取k个近邻的类别标签
    def get_k_neighbor_labels(self, distances, y_train, k):
        neighbor_dist = sorted(distances)[:k]
        neighbor_label = []
        for i in range(len(distances)):
            if distances[i] in neighbor_dist:
                neighbor_label.append(y_train[i])
                if len(neighbor_label) == k:
                    break
        return neighbor_label
    
    # 此处需要填写，标签统计，票数最多的标签即该测试样本的预测标签
    def vote(self, one_sample, X_train, y_train, k):
        dis_list = self.distance(one_sample,X_train)
        neighbor_label = self.get_k_neighbor_labels(dis_list,y_train,k)
        most_value = -1
        most_times = 0
        for i in neighbor_label:
            times = neighbor_label.count(i)
            # print(times)
            if times>most_times:
                # print("fuck")
                most_times=times
                most_value = i
        return most_value
    
    # 此处需要填写，对测试集进行预测
    def predict(self, X_test, X_train, y_train):
        pre_list = []
        for i in range(len(X_train)):
            pre_list.append(self.vote(X_train[i],X_train,y_train,self.k))
        return pre_list
  

def main():
    clf = KNN(k=5)
    train_data = np.genfromtxt('./data/train_data.csv', delimiter=' ')
    train_labels = np.genfromtxt('./data/train_labels.csv', delimiter=' ')
    test_data = np.genfromtxt('./data/test_data.csv', delimiter=' ')
   
    #将预测值存入y_pred(list)内    
    y_pred = clf.predict(test_data, train_data, train_labels)
    np.savetxt("test_ypred.csv", y_pred, delimiter=' ')

    # 正确率测试
    y_train_pred = clf.predict(train_data, train_data, train_labels)
    diff = np.array(y_train_pred) - train_labels
    diff = diff.tolist()
    acc = diff.count(0)*100.0/len(diff)
    print(acc)


if __name__ == "__main__":
    main()