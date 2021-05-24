from math import log
import numpy as np
from keras.models import load_model
from keras.datasets import mnist
import matplotlib.pyplot as plt
model = load_model('model.h5')  # 当前攻击的神经网络
(x_train, y_train), (x_test, y_test) = mnist.load_data()

def get_adv(img, target=None, max_steps=1000):
    if target is None:
        right_class = np.argmax(model.predict(img.reshape([1,1,28,28]))[0])
    # 损失公式中的f函数
    k = 0  # f内的损失项常数
    c = 0.003  # f前系数
    def distance2(a):
        b = a.reshape([-1])
        euclidean2 = np.linalg.norm(b) ** 2
        return euclidean2
    def f(x):
        prob = model.predict(x.reshape([1, 1, 28, 28]))[0]
        if target is None:
            p1 = prob[right_class]
            prob[right_class] = -1
            return max(log(p1) - log(max(prob)), -k)
        else:
            p1 = prob[target]
            prob[target] = -1
            return max(log(max(prob)) - log(p1), -k)
    def cost(x):
        return distance2(x.reshape([1,1,28,28]) - img) + c * f(x.reshape([1,1,28,28]))


    # 一阶微分,输入为4维图片[1,1,28,28]，输出同样
    h = 0.0001  # g与h公式中小h的值
    def gi(x, i):
        x_plus = x.copy().reshape([-1])
        x_minus = x.copy().reshape([-1])
        x_plus[i] += h
        x_minus[i] -= h
        x_plus.reshape([1,1,28, 28])
        x_minus.reshape([1,1,28, 28])
        return (cost(x_plus)-cost(x_minus))/(2*h)
    def hi(x, i):
        x_plus = x.copy().reshape([-1])
        x_minus = x.copy().reshape([-1])
        x_plus[i] += h
        x_minus[i] -= h
        x_plus.reshape([1, 1, 28, 28])
        x_minus.reshape([1, 1, 28, 28])
        return (cost(x_plus) + cost(x_minus) - 2*cost(x)) / (h**2)

    # 优化函数
    step_size = 1000  # ZOO_Newton 中的 step_size 系数
    def ZOO_Newton(x, i):
        g = gi(x, i)
        h = hi(x, i)
        x = x.reshape([-1])
        # print(i, g, h, end=' ')
        # print(x[i],end=' ')
        if h <= 0:
            x[i] -= step_size * g
        else:
            x[i] -= step_size * g / h
        # print(x[i])
        x[i] = np.clip(x[i], 0, 1)
        x = x.reshape([1,1,28,28])
        return x

    # 正式开工
    x = img.copy()
    rand_list = np.random.randint(0, 28*28, max_steps)
    for i in range(max_steps):
        x = ZOO_Newton(x, rand_list[i])
        if target is None and np.argmax(model.predict(x)) != right_class:
            print(i)
            break
        elif np.argmax(model.predict(x)) == target:
            print(i)
            break

    return x

# 单图演示
# x0 = x_test[7]/255
# x = get_adv(x0)
# plt.imshow(x0.reshape([28,28]))
# plt.show()
# plt.imshow(x.reshape([28,28]))
# plt.show()


# l2 norm评价
su = 0
for i in range(100):
    print(i, end='   ')
    x0 = x_test[i]/255
    x = get_adv(x0)
    su += np.linalg.norm(x.reshape([28,28])-x0)
print('average l2 norm:', su/100)
