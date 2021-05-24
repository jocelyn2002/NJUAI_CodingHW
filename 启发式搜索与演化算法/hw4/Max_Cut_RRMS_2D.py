import sys
import numpy as np
import random
import math
import sdp_do
from scipy.spatial import ConvexHull
def PS(pointList):# a list of 3-d points
    #return the nonNegative normal vectors, do not contain the vector of each coordinate
    newPoints=[]
    for point in pointList:
        newPoints.append([0, point[1]])
        newPoints.append([point[0], 0])
    newPoints.append([0,0])
    newPointsList=pointList+newPoints
    points=np.mat(newPointsList)
    hull=ConvexHull(points)
    b=10000000*np.ones((2,1))
    nonNegativeNormVectors=[]
    for simplex in hull.simplices:
        tempMatrix=points[simplex,:]
        if math.fabs(np.linalg.det(tempMatrix))>0.000001:
            vector=np.linalg.solve(tempMatrix,b)
            if np.sum(vector<=0)==2:
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
    nonNegativesNormVectors.append(np.mat([[0.0], [1.0]]))
    nonNegativesNormVectors.append(np.mat([[1.0], [0.0]]))
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


def GetWeightsForTwoDimension(k):
    gap=math.pi/(2.0*(k+1))
    theta=gap
    weights=[]
    for i in range(k):
        weights.append([math.cos(theta),math.sin(theta)])
        theta+=gap
    return weights

def RRMS(algorithm,k,n,objectiveFunc):
    #objectiveFunc is the class of ObjectiveFunction
    weights=GetWeightsForTwoDimension(k)
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
    #coorPopulation = CoordinateWise(sdp_do.MaxCut, n, *objectivesAndWeight)
    populationOfObjective=[]
    #population, populationOfObjective = RRMS(sdp_do.MaxCut, k , n, objectiveFunc)
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
    coorPopulation = CoordinateWise(sdp_do.MaxCut, n, *objectivesAndWeight)
    #populationOfObjective=[]
    population, populationOfObjective = RRMS(sdp_do.MaxCut, k-2 , n, objectiveFunc)
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
    coorPopulation = CoordinateWise(sdp_do.MaxCut, n, *objectivesAndWeight)
    populationOfObjective=[]
    #population, populationOfObjective = RRMS(sdp_do.MaxCut, k , n, objectiveFunc)
    for item in coorPopulation:
        #population.append(item)
        populationOfObjective.append(objectiveFunc.ObjectiveSpacePoint(item))
    #print('old regret is %f:'%(RegretRatio(population, populationOfObjective, objectiveFunc, sdp_do.MaxCut, n)))
    return(RegretRatio(coorPopulation, populationOfObjective, objectiveFunc, sdp_do.MaxCut, n))