# 输出函数
def out_U(U):
    for i in range(10):
        for j in range(10):
            print("%.2f"%U[i][j],end=' ')
        print()
    print()
def out_policy(policy):
    for i in range(10):
        for j in range(10):
            if policy[i][j]==0:
                print("←",end=' ')
            elif policy[i][j]==1:
                print("→",end=' ')
            elif policy[i][j]==2:
                print("↑",end =' ')
            else:
                print("↓",end=' ')
        print()
    print()

# 规定方向 left:0 right:1 up:2 down:3
def R(x,y,a):
    assert(0<=x<=9)
    assert(0<=y<=9)
    if x==2 and y==7:
        return 3
    elif x==7 and y==8:
        return 10
    elif x==4 and y==3:
        return -5
    elif x==7 and y==3:
        return -10
    else:
        if y==0 and a == 0:
            return -1
        elif y==9 and a == 1:
            return -1
        elif x==0 and a == 2:
            return -1
        elif x==9 and a==3:
            return -1
        else:
            return 0
def S_next(x,y,a):
    # 使用-1,-1表示游戏结束，将在下面进行判断
    if x==2 and y==7:
        return -1,-1
    elif x==7 and y==8:
        return -1,-1
    elif x==4 and y==3:
        return -1,-1
    elif x==7 and y==3:
        return -1,-1
    elif y==0 and a == 0:
        return x,y
    elif y==9 and a == 1:
        return x,y
    elif x==0 and a == 2:
        return x,y
    elif x==9 and a==3:
        return x,y
    elif a==0:
        y-=1
    elif a==1:
        y+=1
    elif a==2:
        x-=1
    elif a==3:
        x+=1
    return x,y

# 策略评价
iter_n = 100 
def U_n(pi):
    U_old = [[0 for j in range(10)] for i in range(10)]
    for time in range(iter_n):
        U_new = [[0 for j in range(10)] for i in range(10)]
        for i in range(10):
            for j in range(10):
                # 随机策略，0.7，3个0.1
                for a in range(4):
                        x_next,y_next = S_next(i,j,a)
                        if a==pi[i][j]:
                            U_new[i][j] += 0.7*R(i,j,a) 
                            if x_next>=0:
                                U_new[i][j] += 0.7*gamma*U_old[x_next][y_next]
                        else:
                            U_new[i][j] += 0.1*R(i,j,a)
                            if x_next>=0:
                                U_new[i][j] += 0.1*gamma*U_old[x_next][y_next]
        U_old = U_new
    return U_old

# 策略迭代
gamma = 0.9 # 衰减系数
pi_0 = [[0 for j in range(10)] for i in range(10)] # 初始策略函数，采取主方向全部向左
def policy_iteration():
    k=0
    pi_old = pi_0
    while 1:
        k+=1
        pi_new = [[0 for j in range(10)] for i in range(10)]
        U = U_n(pi_old)
        # out_U(U)

        for i in range(10):
            for j in range(10):
                max_value = -1000
                for a in range(4):
                    new_value = 0
                    for aa in range(4):
                        x_next,y_next = S_next(i,j,aa)
                        if aa==a:
                            new_value += 0.7*R(i,j,aa)
                            if x_next>=0:
                                new_value += 0.7*gamma*U[x_next][y_next]
                        else:
                            new_value += 0.1*R(i,j,aa)
                            if x_next>=0:
                                new_value += 0.1*gamma*U[x_next][y_next]
                    
                    if new_value > max_value:
                        max_value = new_value
                        pi_new[i][j]=a
        
        # 验证是否不变
        dif = 0
        for i in range(10):
            for j in range(10):
                dif += abs( pi_new[i][j] - pi_old[i][j])
        if dif != 0 and k<=100:
            # out_policy(pi_new)
            # print()
            pi_old = pi_new
        else:
            out_U(U)
            out_policy(pi_new)
            print("policy iteration finishes!\niterated",k,"times")
            print()
            return pi_old

policy_iteration()


# 值迭代
epsilon = 1e-6
gamma = 0.9
U_0 = [[0 for j in range(10)] for i in range(10)] # 初始值函数
def get_pi_from_U(U):
    pi = [[0 for j in range(10)] for i in range(10)]
    for i in range(10):
        for j in range(10):
            max_value = -1000
            for a in range(4):
                new_value = 0
                for aa in range(4):
                    x_next,y_next = S_next(i,j,aa)
                    if aa==a:
                        new_value += 0.7*R(i,j,aa)
                        if x_next>=0:
                            new_value += 0.7*gamma*U[x_next][y_next]
                    else:
                        new_value += 0.1*R(i,j,aa)
                        if x_next>=0:
                            new_value += 0.1*gamma*U[x_next][y_next]
                
                if new_value>max_value:
                    max_value=new_value
                    pi[i][j] = a
    
    return pi
def value_iteration():
    k = 0
    U_old = U_0
    while 1:
        k+=1
        U_new = [[0 for j in range(10)] for i in range(10)]
        for i in range(10):
            for j in range(10):
                max_value = -1000
                for a in range(4):
                    new_value = 0
                    for aa in range(4):
                        x_next,y_next = S_next(i,j,aa)
                        if aa==a:
                            new_value += 0.7*R(i,j,aa)
                            if x_next>=0:
                                new_value += 0.7*gamma*U_old[x_next][y_next]
                        else:
                            new_value += 0.1*R(i,j,aa)
                            if x_next>=0:
                                new_value += 0.1*gamma*U_old[x_next][y_next]
                    
                    if new_value>max_value:
                        max_value=new_value
                
                U_new[i][j] = max_value
        
        dif = 0
        for i in range(10):
            for j in range(10):
                if abs(U_new[i][j]-U_old[i][j])>dif:
                    dif = abs(U_new[i][j]-U_old[i][j])
        
        if dif < epsilon*(1-gamma)/gamma:
            out_U(U_new)
            pi = get_pi_from_U(U_new)
            out_policy(pi)
            print("value iteration finishes!\niterated",k,"times")
            print()
            return
        else:
            U_old = U_new

value_iteration()


# 高斯-赛德尔值迭代
gamma = 0.9
U_0 = [[0 for j in range(10)] for i in range(10)] # 初始值函数
def gauss_seidel():
    k = 0
    U = U_0
    pi_old = [[0 for j in range(10)] for i in range(10)]
    while 1:
        k+=1
        for i in range(10):
            for j in range(10):
                max_value = -1000
                for a in range(4):
                    new_value = 0
                    for aa in range(4):
                        x_next,y_next = S_next(i,j,aa)
                        if aa==a:
                            new_value += 0.7*R(i,j,aa)
                            if x_next>=0:
                                new_value += 0.7*gamma*U[x_next][y_next]
                        else:
                            new_value += 0.1*R(i,j,aa)
                            if x_next>=0:
                                new_value += 0.1*gamma*U[x_next][y_next]
                    
                    if new_value>max_value:
                        max_value=new_value
                
                U[i][j] = max_value
        
        
        pi = get_pi_from_U(U)
        dif = 0
        for i in range(10):
            for j in range(10):
                dif += abs(pi[i][j]-pi_old[i][j])
        
        if dif == 0:
            out_U(U)
            out_policy(pi)
            print("Gauss-Seidel finishes!\niterated",k,"times")
            print()
            return
        else:
            pi_old = pi

gauss_seidel()

