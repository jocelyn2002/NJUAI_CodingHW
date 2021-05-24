import numpy as np

def f(x):
    r = x**2+20*np.sin(x)+1
    # r = x**2+1
    return r

def dr_f(x):
    r = 2*x+20*np.cos(x)
    #r = 2*x
    return r

def GD(eps, max_iters):
    alpha = 0.02     # 学习率
    x = 3    # 初始值
    iters = 0
    y1 = f(x)
    y2 = y1+0.1
    while abs(y1 - y2) > eps and iters < max_iters:
        y1 = y2
        x = x - alpha * dr_f(x)
        print(x)
        y2 = f(x)
        iters += 1
    return x, y2

if __name__ == '__main__':
    x_min, f_xmin = GD(1e-8, 1000)
    print(x_min)







