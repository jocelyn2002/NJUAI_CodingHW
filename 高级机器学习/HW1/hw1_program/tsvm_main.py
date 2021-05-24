import os

from sklearn.utils import class_weight
if ('hw1_program' in os.listdir(os.getcwd())):
    os.chdir('hw1_program')

import numpy as np
from sklearn import svm,preprocessing
from sklearn.metrics import auc,roc_curve,accuracy_score
import matplotlib.pyplot as plt


class TSVM:
    def __init__(self):
        # 参数
        self.C_l = 1
        self.C_u = 0.000001
        # sklearn中的SVM分类器，指定软间隔惩罚系数，SMO算法使用的核函数，使用概率
        self.clf = svm.SVC(C=1, kernel='linear',probability=True)
     
    def fit(self, X_l, y_l, X_u):
        """
        训练函数
        :param X_l: 有标记数据的特征
        :param y: 有标记数据的标记
        :param X_u: 无标记数据的特征
        """
        
        # 第一次，根据有标记进行训练，判断无标记数据，
        # TODO:设置分别的C_u+ C_u-
        self.clf.fit(X_l, y_l)
        y_u = self.clf.predict(X_u)
        
        y = np.concatenate((y_l,y_u))
        x = np.concatenate((X_l,X_u))

        weight = np.zeros(len(x))
        weight[:len(X_l)] = self.C_l
        weight[len(X_l):] = self.C_u
        

        # 后续，迭代
        iter_times = 0
        while (self.C_u < self.C_l):
            while True:
                iter_times += 1

                self.clf.fit(x,y,weight)
                y_u = self.clf.predict(X_u)

                dist_u = self.clf.decision_function(X_u) # dist = (w^Tx+b) / ||w||
                w_norm = np.linalg.norm(self.clf.coef_) # ||w||
                xi = 1-y_u*(dist_u*w_norm)

                index = np.arange(xi.size)
                pos,pos_id,neg,neg_id = xi[y_u>0],index[y_u>0],xi[y_u<0],index[y_u<0]
                
                if pos.size == 0 or neg.size==0:
                    break
                
                # 选择最大，因为如果最大的 xi_1 + xi_2 <= 2, 则其余也应当<=2，因此可以退出循环
                max_pos_id,max_neg_id = pos_id[np.argmax(pos)],neg_id[np.argmax(neg)]
                xi_pos,xi_neg = xi[max_pos_id],xi[max_neg_id]
                
                if xi_pos>0 and xi_neg>0 and xi_pos+xi_neg>2:
                    y_u[max_pos_id] *= -1
                    y_u[max_neg_id] *= -1
                    y = np.concatenate(y_l,y_u)
                else:
                    break

            self.C_u = min(2 * self.C_u, self.C_l)
            weight[len(X_l):] = self.C_u
        print("Training finished in [%d] iterations" % iter_times)

    def predict(self, X):
        """
        预测函数
        :param X: 预测数据的特征
        :return: 数据对应的预测值
        """
        return self.clf.predict(X)

    def pred_prob(self, X):
        return self.clf.predict_proba(X)


def load_data():
    label_X = np.loadtxt('label_X.csv', delimiter=',')
    label_y = np.loadtxt('label_y.csv', delimiter=',').astype(np.int)
    unlabel_X = np.loadtxt('unlabel_X.csv', delimiter=',')
    unlabel_y = np.loadtxt('unlabel_y.csv', delimiter=',').astype(np.int)
    test_X = np.loadtxt('test_X.csv', delimiter=',')
    test_y = np.loadtxt('test_y.csv', delimiter=',').astype(np.int)

    label_y[label_y == 0] = -1
    unlabel_y[unlabel_y == 0] = -1
    test_y[test_y == 0] = -1

    return label_X, label_y, unlabel_X, unlabel_y, test_X, test_y

def rna(y_prob,y_true,pltname):
    fpr,tpr,thresholds = roc_curve(y_true,y_prob,)
    auc1 = auc(fpr,tpr)

    plt.figure()
    plt.plot(fpr,tpr,color='darkorange',label='ROC curve (auc=%f)' % auc1)
    plt.plot([0,1],[0,1],color='navy',linestyle='--')
    plt.xlim=([0.0,1.0])
    plt.ylim=([0.0,1.05])
    plt.xlabel('FPR')
    plt.ylabel('TPR')
    plt.title(pltname)
    plt.legend(loc="lower right")
    plt.show()

    return auc1


if __name__ == '__main__':
    label_X, label_y, unlabel_X, unlabel_y, test_X, test_y \
        = load_data()
    label_X = preprocessing.scale(label_X)
    unlabel_X = preprocessing.scale(unlabel_X)
    test_X = preprocessing.scale(test_X)

    
    tsvm = TSVM()
    tsvm.fit(label_X, label_y, unlabel_X)


    y_unlable_pred = tsvm.predict(unlabel_X)
    y_unlabel_prob = tsvm.pred_prob(unlabel_X)[:,1]
    auc_unlabel = rna(y_unlabel_prob,unlabel_y,"unlabel ROC")
    print("unlabel acc:",accuracy_score(y_unlable_pred,unlabel_y),"auc",auc_unlabel)


    y_test_pred = tsvm.predict(test_X)
    y_test_prob = tsvm.pred_prob(test_X)[:,1]
    auc_test = rna(y_test_prob,test_y,"test ROC")
    print("test acc:", accuracy_score(y_test_pred,test_y),"auc:",auc_test)