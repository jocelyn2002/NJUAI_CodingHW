import numpy as np
import tensorflow as tf
from math import tanh, log
from keras.datasets import mnist
from keras.models import load_model
model = load_model('model.h5')
(x_train, y_train), (x_test, y_test) = mnist.load_data()

C = tf.constant(0.001)
k = tf.constant(0, dtype=tf.float32)  # f内的损失项常数
m = tf.constant(1e6, dtype=tf.float32)  # 一个比较大的数，用于设定无上界
LEARNING_RATE = 0.0001


# a为任意维的tf张量，返回欧氏距离平方
def distance2(a):
    b = tf.reshape(a, [1, -1])
    euclidean2 = np.linalg.norm(b)**2
    return euclidean2
def generate_sigma(img, target=None, right_class=None):

    def f(x, target=None, right_class=None):
        prob = model.predict(x.reshape([-1, 1, 28, 28]))[0]
        if target is None:
            p1 = prob[right_class]
            prob[right_class] = -1
            return max(log(p1) - log(max(prob)), -k)
        else:
            p1 = prob[target]
            prob[target] = -1
            return max(log(max(prob)) - log(p1), -k)

    w = np.zeros([1, 1, 28, 28])
    cost_function = distance2(0.5 * (tf.tanh(w) + 1) - img) + C * f(0.5 * (tf.tanh(w) + 1))
    train_step = tf.train.AdamOptimizer(LEARNING_RATE).minimize(cost_function)
    for i in range(100):
        sess.run(train_step)
    return 0.5 * (tf.tanh(w) + 1)

sess = tf.Session()
image = (x_train[0].reshape([28, 28])/255)
sigma = generate_sigma(sess, image)
hack = image+sigma
import matplotlib.pyplot as plt
plt.imshow(image)
plt.show()
plt.imshow(hack)
plt.show()