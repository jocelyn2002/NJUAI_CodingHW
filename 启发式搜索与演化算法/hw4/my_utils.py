import numpy as np

Vertics = 115       # 节点总数
PopulationSize = 20 # 种群大小
MutationRate = 0.1  # 变异率，本次采用 bit-wise
Epoch = 100         # 训练轮数，用于控制总时间

# 建立模型,返回连接矩阵和权重矩阵，其中权重矩阵每一维度为 （目标函数维度，节点1，节点2）
def gen_model(dimension:int):
    connected_matrix = np.zeros([Vertics,Vertics],dtype=int)
    with open('data/graph.txt','r') as f:
        for line in f.readlines():
            a,b = line.split()
            a = int(a)
            b = int(b)
            connected_matrix[a][b] = 1
            connected_matrix[b][a] = 1
    
    weight_matrix = [[line.strip().split(',') for line in open('data/'+str(dimension)+'d/objective'+str(i)+'_weight_matrix.txt').readlines()] for i in range(1,dimension+1)]
    weight_matrix = np.array(weight_matrix,dtype='float')
    
    return connected_matrix,weight_matrix

# 初始化种群，伯努利分布
def init_population():
    return np.random.randint(0,2,[PopulationSize,Vertics])

# 目标函数，返回多维值
def target_function(connected_matrix,weight_matrix,solution):
    dim = weight_matrix.shape[0]
    ret = np.zeros([dim])
    
    # 构建两个连通分量
    connect_part = [[],[]]
    for i in range(Vertics):
        if solution[i] == 0:
            connect_part[0].append(i)
        else:
            connect_part[1].append(i)
    
    # 计算割的值
    for a in range(1,Vertics):
        for b in range(a):
            # ab相邻且a与b属于不同连通分量
            if connected_matrix[a,b]==1 and ((a in connect_part[0] and b in connect_part[1]) or (a in connect_part[1] and b in connect_part[0])):
                # 每个维度分别算
                for d in range(dim):
                    ret[d] += weight_matrix[d][a][b]

    return ret

# 判断s1是否被s2 dominate
def dominatedBy(c,w,s1,s2):
    f1 = target_function(c,w,s1)
    f2 = target_function(c,w,s2)
    for i in range(len(f1)):
        if f1[i]>f2[i]:
            return False
    return True

# 实现了 bit-wise mutation
def mutation(solution):
    for i in range(len(solution)):
        if np.random.rand() < MutationRate:
            solution[i] += 1
            if solution[i] == 2:
                solution[i] = 0
    return solution

# 实现了 one-point crossover
def crossover(s1,s2):
    a = np.random.randint(len(s1))
    ret = np.concatenate((s1[:a],s2[a:]),axis=0)
    return ret

# 从binary生成int表示的结果，用于兼容评估程序
def gen_result(solution):
    ret = []
    for i in range(Vertics):
        if solution[i] == 1:
            ret.append(i)
    return ret
