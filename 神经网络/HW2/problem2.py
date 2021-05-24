import numpy as np
from random import randint
from math import exp


f = 0.1
N_iterations = 1000000
w = [1,1,1,1,1,1,1]
b = 0
learn_rate = 1
decay = 0.99


def LED(Num):
    if Num==-1:
        return [1,1,1,-1,1,1,1]
    elif Num==1:
        return [-1,-1,1,-1,-1,1,-1]
    elif Num==2:
        return [1,-1,1,1,1,-1,1]
    elif Num==3:
        return [1,-1,1,1,-1,1,1]
    elif Num==4:
        return [-1,1,1,1,-1,1,-1]
    elif Num==5:
        return [1,1,-1,1,-1,1,1]
    elif Num==6:
        return [1,1,-1,1,1,1,1]
    elif Num==7:
        return [1,-1,1,-1,-1,1,-1]
    elif Num==8:
        return [1,1,1,1,1,1,1]
    elif Num==9:
        return [1,1,1,1,-1,1,1]
def RealLED(Num):
    light_list = LED(Num)
    for i in range(len(light_list)):
        if (randint(1,10) <= f*10):
            light_list[i] *= -1
    return light_list

def sigmoid(x):
    return 1.0/(1+exp(-x))
def deriv_sigmoid(x):
    return sigmoid(x)*(1-sigmoid(x)) #即exp(-x)/((1+exp(-x))**2)
def CrossEntrophy(y_true,y_pred):
    return (1-y_true)/(1-y_pred) - y_true/y_pred
def predict(x):
    return sigmoid(np.dot(np.array(w),np.array(x)) + b)
for i in range(1,N_iterations+1):
    Num = randint(2,3)
    x = RealLED(Num)

    w_1 = np.array(w)
    x_1 = np.array(x)

    sum_1 = np.dot(w_1,x_1) + b
    d_w = deriv_sigmoid(sum_1) * x_1
    d_b = deriv_sigmoid(sum_1)

    y_pred = predict(x)
    d_L_d_y = CrossEntrophy(3-Num,y_pred)

    w -= d_w * learn_rate * d_L_d_y
    b -= learn_rate * d_b * d_L_d_y

    if i%1000 == 0:
        learn_rate *= decay
        print(i, learn_rate)


print()
print("p(s=2|2)=",predict(LED(2)))
print("p(s=3|2)=",predict(LED(3)))
print()
print("w:",w,"b:",b)
