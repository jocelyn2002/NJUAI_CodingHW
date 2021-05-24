import numpy as np
from keras.datasets import mnist
from keras.utils import np_utils
from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Convolution2D, MaxPooling2D, Flatten
from keras.optimizers import Adam

# 数据加载预处理
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = x_train.reshape(-1, 1, 28, 28)/255  # -1为未知数会自动处理, 思维为 照片个数，channel数，长，宽
x_test = x_test.reshape(-1, 1, 28, 28)/255
y_train = np_utils.to_categorical(y_train, num_classes=10)
y_test = np_utils.to_categorical(y_test, num_classes=10)

# 创建模型
model = Sequential()
# 第一个卷积，激活，池化
model.add(Convolution2D(
    batch_input_shape=(None, 1, 28, 28),
    filters=32,         # 滤波器数量，即下一层层数
    kernel_size=5,
    strides=1,
    padding='same',
    data_format='channels_first'
))
model.add(Activation('relu'))
model.add(MaxPooling2D(
    pool_size=2,
    strides=2,
    padding='same',
    data_format='channels_first'
))
# 第二个卷积，激活，池化
model.add(Convolution2D(
    filters=64,
    kernel_size=5,
    strides=1,
    padding='same',
    data_format='channels_first'
))
model.add(Activation('relu'))
model.add(MaxPooling2D(
    pool_size=2,
    strides=2,
    padding='same',
    data_format='channels_first'
))
# 拉直
model.add(Flatten())
# 全连接层
model.add(Dense(1024))
model.add(Activation('relu'))
model.add(Dense(10))
model.add(Activation('softmax'))

adam = Adam(lr=1e-4)
model.compile(optimizer=adam,
              loss='categorical_crossentropy',
              metrics=['accuracy'])

print('Training-------')
model.fit(x_train, y_train, epochs=5, batch_size=128)  # epochs 训练的轮数，即所有数据被遍历的次数
print('Testing--------')
loss, accuracy = model.evaluate(x_test, y_test)
print('test loss:', loss)
print('test accuracy:', accuracy)

# 保存模型和 softmax前一层输出的模型
model.save('./model.h5')

# layer_model = Model(inputs=model.input, outputs=model.layers[9].output)
# # layer_model.save('./layer_model.h5')