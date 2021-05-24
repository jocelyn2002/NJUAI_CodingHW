import sys
import numpy as np
import random
import math
import sdp_do
from scipy.spatial import ConvexHull
#from Max_Cut_OPT import OPT

def PS(pointList):# a list of 3-d points
    #return the nonNegative normal vectors, do not contain the vector of each coordinate
    newPoints=[]
    for point in pointList:
        newPoints.append([point[0],point[1],point[2],0.0])
        newPoints.append([point[0],point[1],0.0,point[3]])
        newPoints.append([point[0],0.0,point[2],point[3]])
        newPoints.append([0.0, point[1],point[2],point[3]])
        newPoints.append([point[0], 0.0, 0.0,0.0])
        newPoints.append([0.0,point[1], 0.0, 0.0])
        newPoints.append([0.0, 0.0,point[2], 0.0])
        newPoints.append([0.0, 0.0, 0.0,point[3]])
    newPoints.append([0,0,0,0])
    newPointsList=pointList+newPoints
    points=np.mat(newPointsList)
    hull=ConvexHull(points)
    b=10000000*np.ones((4,1))
    nonNegativeNormVectors=[]
    for simplex in hull.simplices:#simplex is the indices of points to form a hyperplane
        tempMatrix=points[simplex,:]
        if math.fabs(np.linalg.det(tempMatrix))>0.000001:
            vector=np.linalg.solve(tempMatrix,b)
            if np.sum(vector<=0)==4:
                vector=0.0-vector
            if np.sum(vector < 0) == 0:
                normValue=np.linalg.norm(vector)
                fvector=vector/normValue
                isSame=False
                for item in nonNegativeNormVectors:#eliminate the same vector
                    if np.sum(abs(item-fvector))<0.000001:
                        isSame=True
                        break
                if abs(1.0-np.sum(abs(fvector)))<0.000001:#eliminate the vectors of coordinate
                    isSame=True
                if not isSame:
                    nonNegativeNormVectors.append(fvector)
    return nonNegativeNormVectors

def RegretRatio(population,pointList,objectiveFunc,algorithm,n):
    #pointList consist of points in the objective corresponding to popultiaon
    nonNegativesNormVectors=PS(pointList)
    nonNegativesNormVectors.append(np.mat([[0.0], [1.0], [0.0], [0.0]]))
    nonNegativesNormVectors.append(np.mat([[0.0], [0.0], [1.0], [0.0]]))
    nonNegativesNormVectors.append(np.mat([[1.0], [0.0], [0.0], [0.0]]))
    nonNegativesNormVectors.append(np.mat([[0.0], [0.0], [0.0], [1.0]]))
    #print(nonNegativesNormVectors)
    ratio=-float('inf')
    for normVector in nonNegativesNormVectors:

        ################calculate the solution based on current weight########
        tempMatrix = np.mat(np.zeros((n, n)))
        for i in range(np.shape(normVector)[0]):
            tempMatrix += normVector[i,0] * objectiveFunc.GetWeightList(i)
        #result=algorithm(n,tempMatrix)
        ################calculate the solution based on current weight########
        maxValueAll=(1.0/0.87856)*objectiveFunc.FS(tempMatrix,algorithm(n,tempMatrix))
        #maxValueAll=np.dot(np.mat(objectiveFunc.ObjectiveSpacePoint(result)),normVector)
        maxValuePart=-float('inf')
        for item in population:
            tempValue=np.dot(np.mat(objectiveFunc.ObjectiveSpacePoint(item)),normVector)
            if maxValuePart<tempValue:
                maxValuePart=tempValue
        tempRatio=1.0-1.0*maxValuePart/maxValueAll
        if ratio<tempRatio:
            ratio=tempRatio
    return ratio



def CoordinateWise(algorithm,n,*args):#,**kwargs):#args is objective function,kwargs is parameters of objective function
    #n is the number of items in ground
    dimension=len(args)
    population=[]
    for i in range(dimension):
        population.append(algorithm(n,args[i][1]))
    return population

########get weights of four dimension space##############
def GetWeightsForFourDimension(k):
    d = 4
    m = int(math.pow((1.0*k) / (d*1.0),1.0/(d-1.0)))
    gap = 1.0 / m
    tempCeterPoints = []
    axis1 = gap / 2.0
    for i in range(m):
        axis2 = gap / 2.0
        for j in range(m):
            axis3 = gap/2.0
            for t in range(m):
                tempCeterPoints.append([axis1, axis2, axis3])
                axis3 += gap
            axis2+=gap
        axis1 += gap
    weights = []
    for item in tempCeterPoints:
        tempNum = math.sqrt(item[0] * item[0] + item[1] * item[1] + item[2]*item[2]+1.0)
        weights.append([item[0] / tempNum, item[1] / tempNum, item[2] / tempNum, 1.0 / tempNum])
        weights.append([item[0] / tempNum, item[1] / tempNum, 1.0 / tempNum,item[2] / tempNum])
        weights.append([item[0] / tempNum, 1.0 / tempNum,item[1] / tempNum, item[2] / tempNum])
        weights.append([1.0 / tempNum, item[0] / tempNum, item[1] / tempNum, item[2]/ tempNum])
    residueNum = k - int(d * math.pow(m, d - 1))
    tempMatrix = np.random.rand(residueNum, d)
    for i in range(residueNum):
        tempNum = np.linalg.norm(tempMatrix[i, :])
        weights.append([tempMatrix[i, 0] / tempNum, tempMatrix[i, 1] / tempNum, tempMatrix[i, 2] / tempNum, tempMatrix[i,3] / tempNum])
    return weights

def RRMS(algorithm,k,n,objectiveFunc):
    #objectiveFunc is the class of ObjectiveFunction
    weights=GetWeightsForFourDimension(k)
    population=[]
    populationOfObjective=[]
    for weight in weights:
        ################calculate the solution based on current weight########
        tempMatrix = np.mat(np.zeros((n, n)))
        for i in range(len(weight)):
            tempMatrix += weight[i] * objectiveFunc.GetWeightList(i)
        population.append(algorithm(n, tempMatrix))
        ################calculate the solution based on current weight########
        populationOfObjective.append(objectiveFunc.ObjectiveSpacePoint(population[-1]))
    return population,populationOfObjective

def Do(population,data,objectiveFunc):
    #k = 20
    #data=GetFacebookData('./../../data/dolphins.gml')
    n = np.shape(data)[0]
    #objectiveFunc = ObjectiveFunction(data)
    objectivesAndWeight = []
    objectivesAndWeight.append([objectiveFunc.F1, objectiveFunc.GetWeightList(0)])
    objectivesAndWeight.append([objectiveFunc.F2, objectiveFunc.GetWeightList(1)])
    objectivesAndWeight.append([objectiveFunc.F3, objectiveFunc.GetWeightList(2)])
    objectivesAndWeight.append([objectiveFunc.F4, objectiveFunc.GetWeightList(3)])
    #coorPopulation = CoordinateWise(sdp_do.MaxCut, n, *objectivesAndWeight)
    #population, populationOfObjective = RRMS(sdp_do.MaxCut, k , n, objectiveFunc)
    populationOfObjective = []
    for item in population:
        #population.append(item)
        populationOfObjective.append(objectiveFunc.ObjectiveSpacePoint(item))
    #print('old regret is %f:'%(RegretRatio(population, populationOfObjective, objectiveFunc, sdp_do.MaxCut, n)))
    return(RegretRatio(population, populationOfObjective, objectiveFunc, sdp_do.MaxCut, n))


def RRMS_Origin(k,data,objectiveFunc):
    #k = 20
    #data=GetFacebookData('./../../data/dolphins.gml')
    n = np.shape(data)[0]
    #objectiveFunc = ObjectiveFunction(data)
    objectivesAndWeight = []
    objectivesAndWeight.append([objectiveFunc.F1, objectiveFunc.GetWeightList(0)])
    objectivesAndWeight.append([objectiveFunc.F2, objectiveFunc.GetWeightList(1)])
    objectivesAndWeight.append([objectiveFunc.F3, objectiveFunc.GetWeightList(2)])
    objectivesAndWeight.append([objectiveFunc.F4, objectiveFunc.GetWeightList(3)])
    coorPopulation = CoordinateWise(sdp_do.MaxCut, n, *objectivesAndWeight)
    #populationOfObjective=[]
    population, populationOfObjective = RRMS(sdp_do.MaxCut, k-4 , n, objectiveFunc)
    for item in coorPopulation:
        population.append(item)
        populationOfObjective.append(objectiveFunc.ObjectiveSpacePoint(item))
    #print('old regret is %f:'%(RegretRatio(population, populationOfObjective, objectiveFunc, sdp_do.MaxCut, n)))
    return(RegretRatio(population, populationOfObjective, objectiveFunc, sdp_do.MaxCut, n))

def RRMS_Star(k,data,objectiveFunc):
    #k = 20
    #data=GetFacebookData('./../../data/dolphins.gml')
    n = np.shape(data)[0]
    #objectiveFunc = ObjectiveFunction(data)
    objectivesAndWeight = []
    objectivesAndWeight.append([objectiveFunc.F1, objectiveFunc.GetWeightList(0)])
    objectivesAndWeight.append([objectiveFunc.F2, objectiveFunc.GetWeightList(1)])
    objectivesAndWeight.append([objectiveFunc.F3, objectiveFunc.GetWeightList(2)])
    objectivesAndWeight.append([objectiveFunc.F4, objectiveFunc.GetWeightList(3)])
    #coorPopulation = CoordinateWise(sdp_do.MaxCut, n, *objectivesAndWeight)
    #populationOfObjective=[]
    population, populationOfObjective = RRMS(sdp_do.MaxCut, k , n, objectiveFunc)
    #for item in coorPopulation:
        #population.append(item)
        #populationOfObjective.append(objectiveFunc.ObjectiveSpacePoint(item))
    #print('old regret is %f:'%(RegretRatio(population, populationOfObjective, objectiveFunc, sdp_do.MaxCut, n)))
    return(RegretRatio(population, populationOfObjective, objectiveFunc, sdp_do.MaxCut, n))

def SingleObj(k,data,objectiveFunc):
    #k = 20
    #data=GetFacebookData('./../../data/dolphins.gml')
    n = np.shape(data)[0]
    #objectiveFunc = ObjectiveFunction(data)
    objectivesAndWeight = []
    objectivesAndWeight.append([objectiveFunc.F1, objectiveFunc.GetWeightList(0)])
    objectivesAndWeight.append([objectiveFunc.F2, objectiveFunc.GetWeightList(1)])
    objectivesAndWeight.append([objectiveFunc.F3, objectiveFunc.GetWeightList(2)])
    objectivesAndWeight.append([objectiveFunc.F4, objectiveFunc.GetWeightList(3)])
    coorPopulation = CoordinateWise(sdp_do.MaxCut, n, *objectivesAndWeight)
    populationOfObjective=[]
    #population, populationOfObjective = RRMS(sdp_do.MaxCut, k , n, objectiveFunc)
    for item in coorPopulation:
        #population.append(item)
        populationOfObjective.append(objectiveFunc.ObjectiveSpacePoint(item))
    #print('old regret is %f:'%(RegretRatio(population, populationOfObjective, objectiveFunc, sdp_do.MaxCut, n)))
    return(RegretRatio(coorPopulation, populationOfObjective, objectiveFunc, sdp_do.MaxCut, n))

