import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def truth(x):
    return np.sin(x[0]) - np.cos(x[1])
# 生成一组训练数据
def gen_pair():
    x1 = np.random.uniform(-5,5)
    x2 = np.random.uniform(-5,5)
    y = truth([x1,x2])
    return [x1,x2],y
# 生成训练集，共num组训练数据
def gen_data(num):
    all_x = list()
    all_y = list()
    for i in range(num):
        x,y = gen_pair()
        all_x.append(x)
        all_y.append(y)
    return all_x,all_y

# activate函数
def activate(x):
    # sigmoid
    return 1.0/(1+np.exp(-x))

    # relu
    # if x > 0:
    #     return x
    # return 0

# activate函数的导数
def deriv_activate(x):
    # sigmoid
    return activate(x)*(1-activate(x))
    
    # relu
    # if x > 0:
        # return 1
    # return 0

# 均方误差
def mse_loss(y_true, y_pred):
    return np.square(y_true-y_pred).mean() / 2.0


class MLP():
    def __init__(self, n_hidden):
        self.hidden = n_hidden
        self.w = np.random.normal(size = 2*self.hidden + 1*self.hidden )
        self.b = np.random.normal(size = self.hidden + 1)
        print("created MLP of size: 2 x %d x 1" % self.hidden)

    def predict(self,x):
        in_h = np.zeros(self.hidden)
        h = np.zeros(self.hidden)
        for i in range(self.hidden):
            in_h[i] = self.w[2*i] * x[0] + self.w[2*i+1] * x[1] + self.b[i]
            h[i] = activate(in_h[i])
        
        in_o1 = self.b[-1]
        for i in range(self.hidden):
            in_o1 += self.w[2*self.hidden + i] * h[i]
        
        o1 = in_o1
        return o1

    def train(self, X_train, y_train, X_valid, y_valid):
        learn_rate = 0.1 # 初始学习率
        decay = 0.8 # 使用衰减系数来控制learn_rate
        batch_size = 10000 # 每一轮学习的样本数

        iteration = 0
        for x, y_true in zip(X_train, y_train):
            # 1.前向传播过程
            in_h = np.zeros(self.hidden)
            h = np.zeros(self.hidden)
            for i in range(self.hidden):
                in_h[i] = self.w[2*i]*x[0] + self.w[2*i+1]*x[1] + self.b[i]
                h[i] = activate(in_h[i])
            
            in_o1 = self.b[-1]
            for i in range(self.hidden):
                in_o1 += self.w[2*self.hidden + i] * h[i]

            y_pred = in_o1          

            # 2.计算梯度
            # 2.1平方误差的梯度
            d_E_d_ypred =  y_pred - y_true

            # 2.2输出层梯度
            d_ypred_d_b = 1
            d_ypred_d_w = np.zeros(self.hidden)
            d_ypred_d_h = np.zeros(self.hidden)
            for i in range(self.hidden):
                d_ypred_d_w[i] = h[i]
                d_ypred_d_h[i] = self.w[2*self.hidden + i]

            # 2.3隐层梯度
            d_h_d_w = np.zeros((self.hidden,2))
            d_h_d_b = np.zeros(self.hidden)
            for i in range(self.hidden):
                d_h_d_w[i][0] = deriv_activate(in_h[i]) * x[0]
                d_h_d_w[i][1] = deriv_activate(in_h[i]) * x[1]
                d_h_d_b[i] = deriv_activate(in_h[i]) * 1
            
            # 3.参数更新
            # 3.1 输出层
            self.b[-1] -= learn_rate * d_E_d_ypred * d_ypred_d_b
            for i in range(self.hidden):
                self.w[2*self.hidden + i] -= learn_rate * d_E_d_ypred * d_ypred_d_w[i]

            # 3.2 隐层
            for i in range(self.hidden):
                # print(self.w[2*i],self.w[2*i+1])
                self.b[i] -= learn_rate * d_E_d_ypred * d_ypred_d_h[i] * d_h_d_b[i]
                self.w[2*i] -= learn_rate * d_E_d_ypred * d_ypred_d_h[i] * d_h_d_w[i][0]
                self.w[2*i+1] -= learn_rate * d_E_d_ypred * d_ypred_d_h[i] * d_h_d_w[i][1]
        
            iteration += 1
            if (iteration % batch_size == 0):
                # 计算validation上的loss
                y_pred = np.apply_along_axis(self.predict, 1, X_valid)
                loss = mse_loss(y_pred, y_valid)
                print("Epoch %d --------------------------------->"%(iteration/batch_size))
                print("learning_rate: %f    mse: %f"%(learn_rate,loss))
                
                # 使用衰减系数来控制learn_rate
                learn_rate *= decay 

        print("train down! ")


if __name__=='__main__':
    # 准备训练数据
    X_train,y_train = gen_data(100000)
    X_train = np.array(X_train)
    y_train = np.array(y_train)
    cut_point = len(y_train) // 10
    X_train, X_valid = X_train[:-cut_point], X_train[-cut_point:]
    y_train, y_valid = y_train[:-cut_point], y_train[-cut_point:]
    print("Training set sample done")


    # 网络创建，训练过程
    network = MLP(n_hidden = 5)
    network.train(X_train, y_train, X_valid, y_valid)


    # 验证结果
    X_test,y_test = gen_data(10000)
    X_test = np.array(X_test)
    y_test = np.array(y_test)
    y_pred = np.apply_along_axis(network.predict,1,X_test)
    print("final mse:%f" % mse_loss(y_pred,y_test))


    # 绘图分析
    figure = plt.figure()
    ax = Axes3D(figure)
    X = np.arange(-5,5,0.1)
    Y = np.arange(-5,5,0.1)
    X,Y = np.meshgrid(X,Y)
    Z = np.zeros((len(X),len(Y)))
    for i in range(len(X)):
        for j in range(len(Y)):
            Z[j][i] = network.predict([X[j][i],Y[j][i]])
    ax.plot_surface(X,Y,Z,rstride=1,cstride=1,cmap='rainbow')
    plt.show()

    figure = plt.figure()
    ax = Axes3D(figure)
    X = np.arange(-5,5,0.1)
    Y = np.arange(-5,5,0.1)
    X,Y = np.meshgrid(X,Y)
    R = np.sin(X) - np.cos(Y)
    ax.plot_surface(X,Y,R,rstride=1,cstride=1,cmap='rainbow')
    plt.show()