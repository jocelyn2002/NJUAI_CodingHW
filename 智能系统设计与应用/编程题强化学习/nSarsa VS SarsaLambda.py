import numpy as np
from cliff_environment import *
from matplotlib import pyplot as plt


epsilon = 0.1
alpha = 0.1
gamma = 1
num_episode = 500


def n_Sarsa(n):
    Q=initialize_Q()
    r_list = []
    r_ten_list = []
    for episode in range(num_episode):
        # print(episode)
        S = [[0,0]]
        A = [select_A(S[0],Q,epsilon)]
        R = []
        T = 1e20
        r_sum = 0
        t=-1
        while 1:
            t+=1
            if t<T:
                R_next,S_next = RS_next(S[t],A[t])
                R.append(R_next)
                r_sum+=R_next
                S.append(S_next)
                if S_next[0]<0:
                    T = t+1
                else:
                    A.append(select_A(S_next,Q,epsilon))
            top = t-n+1
            if top>=0:
                G=0
                for i in range(top+1,min(top+n,T)+1):
                    G += gamma**(i-top-1) * R[i-1]
                if top+n < T:
                    G += gamma**n * Q[S[top+n][0]][S[top+n][1]][A[top+n]]
                Q[S[top][0]][S[top][1]][A[top]]+=alpha*(G-Q[S[top][0]][S[top][1]][A[top]])
            if top==T-1:
                if len(r_ten_list)==10:
                    r_ten_list.pop()
                    r_ten_list.insert(0,r_sum)
                    r_list.append(np.mean(r_ten_list))
                else:
                    r_ten_list.insert(0,r_sum)
                    # r_list.append(np.mean(r_ten_list)) 
                r_sum=0
                break
    
    return r_list
# 使用累计迹的Sarsa_lambda
def Sarsa_lambda(lam):
    Q=initialize_Q()
    r_list = []
    r_ten_list = []
    for episode in range(num_episode):
        # print(episode)
        Z = initialize_Q()
        S = [0,0]
        A = select_A(S,Q,epsilon)
        r_sum = 0
        while 1:
            # print(r_sum)
            R,S_next = RS_next(S,A)
            r_sum += R
            if S_next[0]>=0:
                A_next = select_A(S_next,Q,epsilon)
                delta = R + gamma*Q[S_next[0]][S_next[1]][A_next] - Q[S[0]][S[1]][A]
                Z[S[0]][S[1]][A] += 1
                
                for x in range(12):
                    for y in range(4):
                        for a in range(4):
                            Q[x][y][a] += alpha*delta*Z[x][y][a]
                            Z[x][y][a] *= gamma*lam
                
                S,A=S_next,A_next
            else:
                if len(r_ten_list)==10:
                    r_ten_list.pop()
                    r_ten_list.insert(0,r_sum)
                    r_list.append(np.mean(r_ten_list))
                else:
                    r_ten_list.insert(0,r_sum)
                    # r_list.append(np.mean(r_ten_list))
                r_sum=0
                break
    
    return r_list


# n步Sarsa
# ns1 = n_Sarsa(1)
# plt.plot([i for i in range(len(ns1))],ns1,label="1-Sarsa")
# ns3 = n_Sarsa(3)
# plt.plot([i for i in range(len(ns3))],ns3,label="3-Sarsa")
# ns5 = n_Sarsa(5)
# plt.plot([i for i in range(len(ns5))],ns5,label="5-Sarsa")

# Sarsa(lambda)
sl0 = Sarsa_lambda(0)
plt.plot([i for i in range(len(sl0))],sl0,label="Sarsa(0)")
sl05 = Sarsa_lambda(0.5)
plt.plot([i for i in range(len(sl05))],sl05,label="Sarsa(0.5)")
sl09 = Sarsa_lambda(0.9)
plt.plot([i for i in range(len(sl09))],sl09,label="Sarsa(0.9)")

plt.legend()
plt.show()