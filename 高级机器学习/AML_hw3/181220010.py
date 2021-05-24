import os
import time
import numpy as np
from scipy.optimize import fmin_l_bfgs_b
from util import read_data, print_model, read_model, score

def main(regular: bool):
    if regular==True:
        from crf_with_regular import likelihood, likelihood_prime, predict
    else:
        from crf import likelihood, likelihood_prime, predict

    # 载入训练、测试数据
    train_data = read_data('Dataset/train/*')
    test_data = read_data('Dataset/test/*')
    print('Successfully read:', len(train_data), 'train, ',len(test_data),'test')

    # 生成字典
    alphabet = []
    for label,feature in train_data:
        for w in label:
            if w not in alphabet:
                alphabet.append(w)
    for label,feature in test_data:
        for w in label:
            if w not in alphabet:
                alphabet.append(w)
    print("Alphabet:",alphabet)


    # 进行训练
    def train(data, alphabet, maxiter, log):
        """
        Returns the learned [state_params, trans_params] list,
        where each parameter table is a numpy array.
        """

        # Initialize state and transition parameter tables with zeros
        state_params = np.ndarray.flatten(np.zeros((len(alphabet), len(data[0][1][0]))))
        trans_params = np.ndarray.flatten(np.zeros((len(alphabet), len(alphabet))))
        theta = np.concatenate([state_params, trans_params])

        # Learn by minimizing the negative average log likelihood
        t0 = time.time()
        theta, fmin, _ = fmin_l_bfgs_b(likelihood, theta, fprime=likelihood_prime,
                                    args=(data, alphabet), maxiter=maxiter, disp=log)
        t1 = time.time()

        # Write training summary to log
        if log > 0:
            print("Training data size:", len(data))
            print("Value of likelihood function at minimum:", np.exp(-fmin))
            print("Training time:", t1-t0)

        k = len(alphabet)
        n = len(data[0][1][0])
        mid = k * n
        state_params = np.reshape(theta[:mid], (k, n))
        trans_params = np.reshape(theta[mid:], (k, k))

        return [state_params, trans_params]

    model = train(train_data, alphabet, maxiter=50, log=1)



    # 保存模型
    print('Saving model to', 'model')
    if not os.path.exists('model'):
        os.makedirs('model')
    state_file = "model/state-params.txt"
    trans_file = "model/transition-params.txt"
    print_model(model, state_file, trans_file)



    def test(theta, data, alphabet):
        predictions = predict(theta, data, alphabet)
        acc = score(predictions, data)
        print("acc:",acc)
        return acc

    # 从文件中重新读取模型
    theta = read_model('model')

    acc = test(theta, test_data, alphabet)

    return acc


# 无正则化项
acc = main(regular=False)

# 添加正则化项，重新运行
acc_regular = main(regular=True)

print("\nOriginal acc:", acc)
print("Acc with regular:", acc_regular)