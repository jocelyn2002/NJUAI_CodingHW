# coding:utf-8
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

"""
pca降维
"""
# #加载数据集
# path = "e:/python_test"
# name = "winequality-red.csv"
wine = pd.read_csv(r'D:\desktop\python资源\winequality-red.csv')
wine = wine.values
print("请输入降维后数据维度")
topNfeat = int(input())
while topNfeat >= len(wine[0]):
    print("输入维数大于等于原始维数，请重新输入")
    topNfeat = int(input())


def pca(dataMat, topNfeat):
    # 均值归一化
    meanVals = dataMat.mean(axis=0)  # 按列计算均值，每一列都是一个属性,下同
    maxVals = dataMat.max(axis=0)
    minVals = dataMat.min(axis=0)
    meanRemoved = (dataMat - meanVals) / (maxVals - minVals)
    # 协方差矩阵
    covMat = np.cov(meanRemoved, rowvar=0)  # rowvar : bool,optional如果rowvar为True(默认值),则每行代表一个变量
    # rowvar = 0 即代表每列为一个向量

    eigVals, eigVects = np.linalg.eig(covMat)  # 特征值,特征向量
    eigVallnd = np.argsort(eigVals)
    eigVallnd = eigVallnd[:-(topNfeat + 1):-1]  # 按照特征值从小到大排序，返回排序后索引，逆序后取topNfeat个最大的特征值的索引
    # 因为切片取不到端点，所以要加一  #:-1是步长
    redEigVects = eigVects[:, eigVallnd]  # 获取特征向量
    lowDDataMat = np.dot(meanRemoved, redEigVects)
    return lowDDataMat


print(pca(wine, topNfeat))

