import numpy as np
import warnings
from keras import backend as K
from keras.models import load_model
from keras.datasets import mnist
import matplotlib.pyplot as plt
import tensorflow as tf
config=tf.ConfigProto(gpu_options=tf.GPUOptions(allow_growth=True))
sess = tf.InteractiveSession(config=config)
K.set_session(sess)

warnings.filterwarnings('ignore')
model = load_model('./model.h5')
(x_train, y_train), (x_test, y_test) = mnist.load_data()
# 设置常数
E = 0.007
S = 0.2
Rounds = 30


def i_FGSM(img, target=None):
    hacked_image = np.copy(img)
    model_input_layer = model.layers[0].input
    model_output_layer = model.layers[-1].output
    max_below = img-S
    max_above = img+S
    list1 = model.predict(img)[0]
    right_class = np.argmax(list1)
    # print('right class:', right_class)
    if target is None:
        list1[right_class] = -1.0
        target = np.argmax(list1)
    # print('target class:', target)
    # print()
    cost_function = model_output_layer[0, target]
    gradient_function = K.gradients(cost_function, model_input_layer)[0]
    grab_cost_and_gradients_from_model = K.function([model_input_layer, K.learning_phase()],
                                                        [cost_function, gradient_function])
    for i in range(Rounds):
        cost, gradients = grab_cost_and_gradients_from_model([hacked_image, 0])
        n = np.sign(gradients)
        hacked_image += n*E
        hacked_image = np.clip(hacked_image, max_below, max_above)
        hacked_image = np.clip(hacked_image, -1.0, 1.0)
        # print('target predict:', cost)
        if cost >= 0.5:
            print(i)
            break
    else:
        print(Rounds)
    return hacked_image
def predict(img):
    return np.argmax(model.predict(img)[0])


# #单张图片检测
# hack = i_FGSM(x_test[0].reshape([-1, 1, 28, 28])/255)
# plt.imshow(x_test[0].reshape([28, 28])/255)
# plt.show()
# plt.imshow(hack.reshape([28, 28]))
# plt.show()


# # 非目标攻击评价
# n_of_attack = 0
# for image in x_test[0:100]:
#     image = image.reshape([-1, 1, 28, 28])/255
#     hack = i_FGSM(image)
#     if predict(image) != predict(hack):
#         n_of_attack += 1
# u_attack_rate = n_of_attack/1000
#
#
# # 目标攻击评价 全部攻击到 5
# # n_of_attack = 0
# # for image in x_test:
# #     image = image.reshape([-1, 1, 28, 28])/255
# #     hack = i_FGSM(image, target=5)
# #     if predict(image) != predict(hack):
# #         n_of_attack += 1
# # attack_rate = n_of_attack/len(x_test[0])
#
#
# print('untargeted attack rate:', u_attack_rate)
# # print('targeted attack rate:', attack_rate)


# l2 norm测试
su = 0
for image in x_test[0:100]:
    image = image.reshape([-1, 1, 28, 28])/255
    hack = i_FGSM(image)
    su += np.linalg.norm(hack-image)
print('average l2 norm:', su/100)
