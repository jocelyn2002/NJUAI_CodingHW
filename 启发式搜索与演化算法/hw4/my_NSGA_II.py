from my_utils import *
import numpy as np
from datetime import datetime

def NSGA(dimension):
    c,w = gen_model(dimension)

    # 从中群中选择一个父节点出来(选目标函数大的)
    def BinaryTournament(P):
        size = P.shape[0]
        t1 = P[np.random.randint(size)]
        t2 = P[np.random.randint(size)]
        minus = target_function(c,w,t1) - target_function(c,w,t2)
        return t1 if np.sum(minus) > 0 else t2

    # 返回排好序的解集列表（大的在前小的在后）
    def fastNonDominatedSorting(P):
        rank = np.zeros(P.shape[0])

        S = [[] for i in range(P.shape[0])]
        n = np.zeros(P.shape[0])
        F = []
        for x in range(P.shape[0]):
            for y in range(P.shape[0]):
                if dominatedBy(c,w,P[y],P[x]):
                    S[x].append(y)
                elif dominatedBy(c,w,P[x],P[y]):
                    n[x] += 1
            if n[x] == 0:
                rank[x] = 1
                F.append(x)
        
        i = 0
        while len(F)>0:
            Q = []
            for x in F:
                for y in S[x]:
                    n[y] -= 1
                    if n[y] == 0:
                        rank[y] = i+1
                        Q.append(y)
            i += 1
            F = Q
        
        ret = []
        for i in range(1,P.shape[0]+1):
            tmp = []
            for j in range(len(rank)):
                if rank[j] == i:
                    tmp.append(P[j])
            if len(tmp)>0:
                ret.append(tmp)
            else:
                break
        
        # 反转，使大的排在前面
        return ret[::-1]
                
    # 计算crosding分数，返回 ndarray
    def crowdingDistance(P):
        target = [target_function(c,w,p) for p in P]
        target = np.array(target).T # 转置之后大小为： target维度 x individual
        # 设置初始distance为0
        distance = np.zeros([len(P)])
        for dim in range(target.shape[0]):
            Q = target[dim,:]
            Q = np.sort(Q)
            scale = Q.max() - Q.min()
            for i in range(len(P)):
                index = int(np.where(Q == target[dim][i])[0][0])
                if index==0 or index==target.shape[1]-1:
                    distance[i] = 100000 # 设为无穷大
                else:
                    distance[i] += (Q[index+1] - Q[index-1]) / scale
        return distance


    # 要开始咯
    p = init_population()
    for epoch in range(Epoch):
        print(datetime.now().strftime('20%y-%m-%d %H:%M:%S')," NSGA-II on",str(dimension)+'d'," Epoch:",epoch)
        # 父代挑选、生成子代
        offspring = []
        while len(offspring) < PopulationSize:
            p1 = BinaryTournament(p)
            p2 = BinaryTournament(p)
            
            p1 = mutation(p1)
            p2 = mutation(p2)

            child = crossover(p1,p2)
            offspring.append(child)
            
        new_pop = np.array(list(p)[:] + offspring[:])

        # N+N selection
        pops = fastNonDominatedSorting(new_pop)
        p = [] # 重置种群
        for tmp in pops: # tmp是个List
            if len(p) == PopulationSize:
                break
            elif len(p) + len(tmp) <= PopulationSize:
                p += tmp
            else:
                dis = crowdingDistance(tmp)
                k = PopulationSize-len(p)
                ids = np.argpartition(dis,-k)
                for index in ids[-k:]:
                    p.append(tmp[index])
        
        p = np.array(p)

    print('NSGA-II Success!')
    ret = [gen_result(individual) for individual in p]

    print("Final Population Size:",end=' ')
    for i in range(len(ret)):
        print(len(ret[i]),end=' ')
    print()

    return ret