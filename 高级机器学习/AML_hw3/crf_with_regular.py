import numpy as np
import scipy.special
from crf import *

# 正则化系数
L2 = 00.1

# L2正则化
def L2Norm(l, theta):
    return  np.dot(theta, theta) * l

# L2正则化的导数
def gradient_L2Norm(l, theta):
    return l * theta

def likelihood(theta, data, alphabet):
    """
    Objective function to minimize.
    Returns the negative average log likelihood of theta given the data.

    Parameters:
    - theta, a [state_params, trans_params] list;
    - data, a list of (word_label, word_features) tuples; and
    - alphabet, a list of all possible character labels.
    """
    
    # If flattened, reshape theta into a list of state parameter table of size n x k
    # and transition parameter table of size k x k,
    # where n is the length of the feature vector and k is the size of the alphabet
    if len(theta) != 2:
        k = len(alphabet)      # number of possible character labels
        n = len(data[0][1][0]) # length of feature vector
        mid = k * n

        state_params = np.reshape(theta[:mid], (k, n))
        trans_params = np.reshape(theta[mid:], (k, k))
        theta = [state_params, trans_params]

    p = []
    for label, features in data:
        beta = beliefs(theta, features)
        pairwise_p = pairwise_prob(beta)
        single_p = single_prob(pairwise_p)
        p.append(joint_prob(single_p, label, alphabet))

    return -np.sum(p)/len(data) + L2Norm(L2,np.ndarray.flatten(theta[0])) + L2Norm(L2,np.ndarray.flatten(theta[1]))

def state_gradient(theta, data, alphabet):
    """
    Returns a flattened k x n numpy array,
    where k is the size of the alphabet and n is the length of the feature vector.

    Parameters:
    - theta, a [state_params, trans_params] list;
    - data, a list of (word_label, word_features) tuples; and
    - alphabet, a list of all possible character labels.
    """

    # Initialize a state gradient table of size k x n with zeros
    gradient = np.zeros((len(alphabet), len(data[0][1][0])))

    for label, features in data:
        beta = beliefs(theta, features)
        pairwise_p = pairwise_prob(beta)
        single_p = single_prob(pairwise_p)
        for v, c, p in zip(features, label, single_p):
            for i in range(gradient.shape[0]): # possible labels
                for j in range(gradient.shape[1]): # features
                    indicator = 0
                    if c == alphabet[i]:
                        indicator = 1
                    gradient[i][j] += (indicator - p[i]) * v[j]
    
    gradient /= len(data)

    return np.ndarray.flatten(np.negative(gradient+gradient_L2Norm(L2,theta[0])))

def transition_gradient(theta, data, alphabet):
    """
    Returns a flattened k x k numpy array, where k is the size of the alphabet.

    Parameters:
    - theta, a [state_params, trans_params] list;
    - data, a list of (word_label, word_features) tuples; and
    - alphabet, a list of all possible character labels.
    """

    # Initialize a transition gradient table of size k x k with zeros
    gradient = np.zeros((len(alphabet), len(alphabet)))

    for label, features in data:
        beta = beliefs(theta, features)
        pairwise_p = pairwise_prob(beta)
        label_pairs = list(zip([None] + label, label + [None]))[1:-1]

        for (label1, label2), p in zip(label_pairs, pairwise_p):
            for i in range(gradient.shape[0]):
                for j in range(gradient.shape[1]):
                    indicator = 0
                    if label1 == alphabet[i] and label2 == alphabet[j]:
                        indicator = 1
                    gradient[i][j] += indicator - p[i][j]

    gradient /= len(data)

    return np.ndarray.flatten(np.negative(gradient+gradient_L2Norm(L2,theta[1])))

def likelihood_prime(theta, data, alphabet):
    """
    Returns a flattened numpy array of the [feature_gradient, transition_gradient] list.

    Parameters:
    - theta, a [state_params, trans_params] list;
    - data, a list of (word_label, word_features) tuples; and
    - alphabet, a list of all possible character labels.
    """

    # Reshape flattened theta into a list of k x n state parameter table and
    # k x k transition parameter table, where k is the size of the alphabet and
    # n is the length of the feature vector. Both parameter tables are numpy arrays.
    k = len(alphabet)      # number of possible character labels
    n = len(data[0][1][0]) # length of feature vector
    mid = k * n

    state_params = np.reshape(theta[:mid], (k, n))
    trans_params = np.reshape(theta[mid:], (k, k))
    theta = [state_params, trans_params]

    return np.concatenate((state_gradient(theta, data, alphabet),
                           transition_gradient(theta, data, alphabet)))


    """
    Returns a list of predictions, where each prediction is
    a list of predicted character labels of a word.

    Parameters:
    - theta, a [state_params, trans_params] list;
    - data, a list of (word_label, word_features) tuples; and
    - alphabet, a list of all possible character labels.
    """

    predictions = []
    for _, features in data:
        beta = beliefs(theta, features)
        pairwise_p = pairwise_prob(beta)
        single_p = single_prob(pairwise_p)
        predictions.append(predict_word(single_p, alphabet))

    return predictions