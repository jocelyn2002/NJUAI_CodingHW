import numpy as np
# 定义常亮
qf=3.007 # 5算法5数据，0.05
qa=2.728 # 5算法，0.05
N=5
k=5

# 载入数据
Algs = np.array([3.2,3.8,1.2,4,2.8])
name = {3.2:"A",3.8:"B",1.2:"C",4:"D",2.8:"E"}

# Friedman检验
Tx2 = 12*N/(k*(k+1)) * (np.sum(Algs**2)-k*((k+1)**2)/4)
TF = ((N-1)*Tx2) / (N*(k-1)-Tx2)
print("TF:",TF)
if (TF>qf):
    print("所有算法性能相同假设 被Friedman检验所拒绝")

    # 进行Nemenyi后续检验
    CD = qa*(k*(k+1)/(6*N))**0.5
    print("CD:", CD)
    max_alg = np.max(Algs)
    for alg in Algs:
        if max_alg-alg > CD:
            print("算法",name[max_alg],"比算法",name[alg],"显著要好")
