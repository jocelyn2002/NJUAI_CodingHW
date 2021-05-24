import numpy as np
# 规定行动0，1，2，3代表左右上下
def RS_next(state,a):
    assert a in [0,1,2,3]

    x,y = state[0],state[1]
    assert x>=0 and x<=11 and y>=0 and y<=3
    
    r = -1
    
    if x==0 and a==0:
        pass
    elif y==3 and a==2:
        pass
    elif x==11 and a==1:
        pass
    elif x==0 and y==0 and a==3:
        pass
    elif x==11 and y==0 and a==3:
        pass
    elif 1<=x and x<=10 and y==1 and a==3:
        x,y = 0,0
        r = -100
    elif y==0 and ((x==0 and a==1) or (x==11 and a==0)):
        x,y = 0,0
        r = -100
    elif x==11 and y==1 and a==3:
        # 返回负值表示情节结束
        x,y=-1,-1
    elif a==0:
        x-=1
    elif a==1:
        x+=1
    elif a==2:
        y+=1
    elif a==3:
        y-=1

    return r,[x,y]


def initialize_Q():
    Q = [[[0,0,0,0] for i in range(4)]for j in range (12)]
    return Q
def epsilon_greedy(epsilon):
    if np.random.rand() <= epsilon:
        return True
    else:
        return False
def select_A(S,Q,epsilon):
    if epsilon_greedy(epsilon)==True:
        return np.random.randint(0,4)
    else:
        return np.argmax(Q[S[0]][S[1]])