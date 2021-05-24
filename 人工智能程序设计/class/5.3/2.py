# coding:utf-8
from numpy import *
import matplotlib
import matplotlib.pyplot as plt

"""
pca降维
"""


# 加载数据集
def loadDataSet(fileName, delim):
    fr = open(fileName)
    stringArr = [line.strip().split(delim) for line in fr.readlines()]
    datArr = [list(map(float, line)) for line in stringArr]
    return mat(datArr)


# 加载包含NaN的数据集
# 用平均值代替缺失值
def replaceNanWithMean(fileName, delim):
    datMat = loadDataSet(fileName, delim)
    numFeat = shape(datMat)[1]
    for i in range(numFeat):
        meanVal = mean(datMat[nonzero(~isnan(datMat[:, i].A))[0], i])
        datMat[nonzero(isnan(datMat[:, i].A))[0], i] = meanVal
    return datMat


# PCA算法
def pca(dataMat, topNfeat=9999999):
    # 均值归一化
    meanVals = dataMat.mean(axis=0)
    maxVals = dataMat.max(axis=0)
    minVals = dataMat.min(axis=0)
    meanRemoved = (dataMat - meanVals) / (maxVals - minVals)
    # 协方差矩阵
    covMat = cov(meanRemoved, rowvar=0)
    # 特征值，特征向量
    eigVals, eigVects = linalg.eig(mat(covMat))
    # 按照特征值从小到大排序，返回排序后索引
    eigValInd = argsort(eigVals)
    # 逆序取topNfeat个最大的特征的索引
    eigValInd = eigValInd[:-(topNfeat + 1):-1]
    # 获取特征向量
    redEigVects = eigVects[:, eigValInd]
    # 矩阵相乘，降低维度
    lowDDataMat = meanRemoved * redEigVects
    # 将原始数据重新映射会高维，用于调试
    reconMat = multiply((lowDDataMat * redEigVects.T), (maxVals - minVals)) + meanVals
    return lowDDataMat, reconMat


if __name__ == '__main__':
    dataMat = loadDataSet('testSet.txt', '\t')
    lowDMat, reconMat = pca(dataMat, 1)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(dataMat[:, 0].flatten().A[0], dataMat[:, 1].flatten().A[0],
               marker='^', s=90)
    ax.scatter(reconMat[:, 0].flatten().A[0], reconMat[:, 1].flatten().A[0],
               marker='o', s=50, c='red')
    plt.show()

    dataMat = replaceNanWithMean('secom.data', ' ')
    meanRemoved = dataMat - dataMat.mean(axis=0)
    covMat = cov(meanRemoved, rowvar=0)
    eigVals, eigVects = linalg.eig(mat(covMat))
    eigValInd = argsort(eigVals)
    eigValInd = eigValInd[::-1]
    sortedEigVals = eigVals[eigValInd]
    total = sum(sortedEigVals)
    varPercentage = sortedEigVals / total * 100

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(range(1, 21), varPercentage[:20], marker='^')
    plt.xlabel('Principal Component Number')
    plt.ylabel('Percentage of Variance')
    plt.show()