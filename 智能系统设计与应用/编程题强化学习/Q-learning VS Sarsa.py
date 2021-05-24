import numpy as np
from cliff_environment import *
from matplotlib import pyplot as plt


epsilon = 0.1
alpha = 0.1
gamma = 1
num_episode=500


def Q_learning():
    Q = initialize_Q()
    r_list = []
    r_ten_list = []
    for episode in range(num_episode):
        # Initialize S
        S = [0,0]
        r_sum = 0
        while 1:
            # Choose A
            A = select_A(S,Q,epsilon)
            R,S_next = RS_next(S,A)
            r_sum+=R
            if S_next[0]<0:
                if len(r_ten_list)==10:
                    r_ten_list.pop()
                    r_ten_list.insert(0,r_sum)
                    r_list.append(np.mean(r_ten_list))
                else:
                    r_ten_list.insert(0,r_sum)
                r_sum=0
                break
            else:
                Q[S[0]][S[1]][A] += alpha * (R + gamma*np.max(Q[S_next[0]][S_next[1]])-Q[S[0]][S[1]][A])
                S=S_next
    return r_list
def Sarsa():
    Q=initialize_Q()
    r_list = []
    r_ten_list = []
    for episode in range(num_episode):
        S = [0,0]
        r_sum = 0
        # Choose A
        A = select_A(S,Q,epsilon)
        
        while 1:
            R,S_next = RS_next(S,A)
            r_sum+=R
            
            if S_next[0]>=0:
                A_next = select_A(S_next,Q,epsilon)          
                Q[S[0]][S[1]][A] +=  alpha * (R + gamma*Q[S_next[0]][S_next[1]][A_next]-Q[S[0]][S[1]][A])
                S = S_next
                A = A_next
            else:
                if len(r_ten_list)==10:
                    r_ten_list.pop()
                    r_ten_list.insert(0,r_sum)
                    r_list.append(np.mean(r_ten_list))
                else:
                    r_ten_list.insert(0,r_sum)
                r_sum=0
                break
        
    return r_list


if __name__ == "__main__":
    qr = Q_learning()
    sr = Sarsa()
    
    plt.plot([i for i in range(len(qr))],qr,color="red",label="Q-learning")
    plt.plot([i for i in range(len(sr))],sr,color="skyblue",label="Sarsa")
    plt.legend()
    plt.show()