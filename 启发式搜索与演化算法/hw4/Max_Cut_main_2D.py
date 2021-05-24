import sys

import Max_Cut_RRMS_2D
import numpy as np
import random
from datetime import datetime
def GetFacebookData(filePath):
    dataFile=open(filePath)
    maxIndex=-1
    minIndex=100000000
    for line in dataFile.readlines():
        items=line.split()
        if int(items[0])>maxIndex:
            maxIndex=int(items[0])
        if int(items[0])<minIndex:
            minIndex=int(items[0])
        if int(items[1]) > maxIndex:
            maxIndex = int(items[1])
        if int(items[1]) < minIndex:
            minIndex = int(items[1])
    nodeNum=maxIndex-minIndex+1
    print("maxIndex, minIndex, nodeNum is %d,%d,%d respectively."%(maxIndex,minIndex,nodeNum))
    dataFile.close()

    dataFile = open(filePath)
    data=np.mat(np.zeros((nodeNum,nodeNum)))
    for line in dataFile.readlines():
        items = line.split()
        if int(items[0])!=int(items[1]):#eliminate the self-circle
            data[int(items[0])-minIndex,int(items[1])-minIndex]=1.0
            data[int(items[1])-minIndex,int(items[0])-minIndex]=1.0
    dataFile.close()
    return data

class ObjectiveFunction:
    def __init__(self,data,w=None):#w is the weight of objective functions
        #initialize the random seed to make sure the reproduce of the result.
        #data is the adjacent matrix
        np.random.seed(0)
        random.seed(0)
        n = np.shape(data)[0]
        self.n=n
        self.data=data
        self.weightOfGraph1=1.0*np.mat(np.random.rand(n,n))
        self.weightOfGraph2=1.0*np.mat(np.random.rand(n,n))
        self.weightList = [self.weightOfGraph1, self.weightOfGraph2]
        self.ReformalizeWeightMatrix(n, data, *self.weightList)
        #self.wightOfEachMovie=np.mat([10.0*self.dataMean[i,0]/np.sum(self.dataMean) for i in range(self.numOfMovies)])
        self.f1=0.0
        self.f2=0.0
        self.w=w
    def ReformalizeWeightMatrix(self,n,data,*args):
        for i in range(n):
            for j in range(i,n):
                if data[i,j]<0.5:#means data[i,j]==0
                    for item in args:
                        item[i,j]=0.0
                        item[j,i]=0.0
                else:
                    for item in args:
                        item[j,i]=item[i,j]

    def GetWeightList(self,k):
        return self.weightList[k]
    def F1(self,S):# S is the index of selected items
        S_hat = [item for item in range(self.n) if item not in S]
        self.f1=np.sum((self.weightOfGraph1[S,:])[:,S_hat])
        return self.f1

    def F2(self,S):# S is the index of selected
        S_hat = [item for item in range(self.n) if item not in S]
        self.f2 = np.sum((self.weightOfGraph2[S,:])[:,S_hat])
        return self.f2

    def FS(self,matrix,S):
        S_hat = [item for item in range(self.n) if item not in S]
        return np.sum((matrix[S,:])[:,S_hat])

    def ObjectiveSpacePoint(self,S):
        self.f1 = self.F1(S)
        self.f2 = self.F2(S)
        return [self.f1,self.f2]


if __name__=="__main__":
    
    data=GetFacebookData('./football.gml')
    objectiveFunc = ObjectiveFunction(data)


    ###population is the list of solutions
    ##############################################################
    #for example population=[[0,3,5],[5,3,2],[1,2,5,8,9]] means that population contains three solutions
    #the fisrt solution solution [0,3,5] means all the nodes are divided into two partitions , nodes 0,3,5 are in one partition, and all the other nodes are in another partition
    #the second solution solution [5,3,2] means all the nodes are divided into two partitions , nodes 5,3,2 are in one partition, and all the other nodes are in another partition
    #the second solution solution [1,2,5,8,9] means all the nodes are divided into two partitions , nodes 1,2,5,8,9 are in one partition, and all the other nodes are in another partition
    # whe  you need to compute your regret ratio, please replace the population with your population
    ##############################################################
    # population=[[1]] 
    
    from my_NSGA_II import *
    population = NSGA(dimension=2,epochs=20)

    ratio = Max_Cut_RRMS_2D.Do(population, data, objectiveFunc)
    print(datetime.now().strftime('20%y-%m-%d %H:%M:%S'),'the regret ratio is %f'%(ratio))