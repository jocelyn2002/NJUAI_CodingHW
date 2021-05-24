from my_utils import *
import numpy as np
from datetime import datetime

def MOEA(dimension):
    c,w = gen_model(dimension)
    NeighbourSize = 5

    # 生成子任务权重向量(归一化的)， individual x dimension
    def gen_weight(dim_size,pop_size):
        weight = np.random.rand(pop_size,dim_size)
        div = np.sum(weight,axis=1)
        for i in range(pop_size):
            weight[i] /= div[i]
        return weight

    # 生成子任务的邻居集合
    def gen_neighbours(w_matrix):
        ret = []
        for weight in w_matrix:
            dis = [np.linalg.norm(weight-vector) for vector in w_matrix]
            tmp = []
            ids = np.argpartition(dis,NeighbourSize)
            for index in ids[:NeighbourSize]:
                tmp.append(index)
            ret.append(tmp)
        return np.array(ret)

    # 从自己及邻居中选择一个父亲节点
    def matingSelection(P,weights,neighbours,ID):
        t1 = P[neighbours[ID][np.random.randint(NeighbourSize)]]
        t2 = P[neighbours[ID][np.random.randint(NeighbourSize)]]
        minus = np.dot(weights[ID],target_function(c,w,t1)) - np.dot(weights[ID],target_function(c,w,t2))
        return t1 if minus > 0 else t2
        
    
    # 初始化
    weights = gen_weight(dimension,PopulationSize)
    neighbours = gen_neighbours(weights)
    p = init_population()
    for epoch in range(Epoch):
        print(datetime.now().strftime('20%y-%m-%d %H:%M:%S')," MOEA_D on",str(dimension)+'d'," Epoch:",epoch)
        for ID in range(PopulationSize):
            # MatingSelection and Reproduction
            p1 = matingSelection(p,weights,neighbours,ID)
            p2 = matingSelection(p,weights,neighbours,ID)
            p1 = mutation(p1)
            p2 = mutation(p2)
            child = crossover(p1,p2)

            # Replacement
            for i in neighbours[ID]:
                if np.dot(weights[i],target_function(c,w,child)) > np.dot(weights[i],target_function(c,w,p[i])):
                    p[i] = child
    
    print('MOEA_D Success!')
    ret = [gen_result(individual) for individual in p]

    print("Final Population Size:",end=' ')
    for i in range(len(ret)):
        print(len(ret[i]),end=' ')
    print()

    return ret
