import numpy as np
import scipy.special

def node_potentials(features, state_params):
    """
    Returns a w x k numpy array of node potentials,
    where w is the word length and k is the size of the alphabet.

    Parameters:
    - features, a w x n numpy array of feature vectors,
      where n is the length of the feature vector; and
    - state_params, a k x n numpy array of state parameters.
    """

    return np.dot(features, np.transpose(state_params))

def clique_potentials(node_factor1, node_factor2, trans_params):
    """
    Computes the clique potentials of a single clique.
    Returns a k x k numpy array, where k is the size of the alphabet.

    Parameters:
    - node_factor1, a k-dimensional numpy array of node potentials;
    - node_factor2, a k-dimensional numpy array of node potentials or a None object; and
    - trans_params, a k x k numpy array of transition parameters.
    """

    psi = trans_params + node_factor1[:, np.newaxis]
    if node_factor2 is not None:
        psi += node_factor2

    return psi

def clique_tree_potentials(theta, features):
    """
    Computes the clique potentials of the entire chain.
    Returns a (w-1) x k x k numpy array,
    where w is the word length and k is the size of the alphabet.

    Parameters:
    - theta, a [state_params, trans_params] list; and
    - features, a w x n numpy array, where n is the length of the feature vector.
    """

    state_params, trans_params = theta
    phi = node_potentials(features, state_params)

    # Include the potentials of the last two nodes in the same clique
    cliques = [(node, None) for node in phi[:-2]] + [(phi[-2], phi[-1])]

    psi = [clique_potentials(n1, n2, trans_params) for n1, n2 in cliques]

    return np.array(psi)

def sum_product_messages(psi):
    """
    Returns the (backward messages, forward messages) tuple.
    Each messages is a (w-2) x k numpy array,
    where w is the word length and k is the size of the alphabet.

    Parameter:
    - psi, a (w-1) x k x k numpy array of clique tree potentials.
    """
    
    # Backward messages
    bwd = []
    prev_msgs = np.zeros(psi.shape[1])
    for clique in psi[:0:-1]:
        msg = scipy.special.logsumexp(clique + prev_msgs, axis=1)
        bwd.append(msg)
        prev_msgs += msg

    # Forward messages
    fwd = []
    prev_msgs = np.zeros(psi.shape[1])
    for clique in psi[:-1]:
        msg = scipy.special.logsumexp(clique + prev_msgs[:, np.newaxis], axis=0)
        fwd.append(msg)
        prev_msgs += msg

    return (np.array(bwd), np.array(fwd))

def beliefs(theta, features):
    """
    Returns a numpy array of size (w-1) x k x k,
    where w is the word length and k is the size of the alphabet.

    Parameters:
    - theta, a [state_params, trans_params] list; and
    - features, a w x n numpy array of feature vectors,
      where n is the length of the feature vector.
    """

    psi = clique_tree_potentials(theta, features)
    delta_bwd, delta_fwd = sum_product_messages(psi)

    k = delta_fwd.shape[1]
    delta_fwd = np.concatenate(([np.zeros(k)], delta_fwd))
    delta_bwd = np.concatenate((delta_bwd[::-1], [np.zeros(k)]))
    beta = psi + delta_fwd[:, :, np.newaxis] + delta_bwd[:, np.newaxis]

    return np.array(beta)

def pairwise_prob(beta):
    """
    Computes the pairwise marginal probabilities.
    Returns a numpy array of size (w-1) x k x k,
    where w is the word length and k is the size of the alphabet.
    
    Parameter:
    - beta, a (w-1) x k x k numpy array of log belief tables.
    """

    return np.exp(beta - scipy.special.logsumexp(beta, axis=(1,2))[:, np.newaxis, np.newaxis])

def single_prob(pairwise_p):
    """
    Computes the singleton marginal probabilities.
    Returns a w x k numpy array, where n is the word length and k is the size of the alphabet.
    
    Parameter:
    - pairwise_p, a numpy array of size (w-1) x k x k of pairwise marginal probabilities.
    """

    p = np.sum(pairwise_p, axis=2)
    q = np.sum(pairwise_p[-1], axis=0) # Last character in the word

    return np.concatenate((p, q[np.newaxis, :]))

def joint_prob(single_p, label, alphabet):
    """
    Computes the joint probability of the label given singleton marginal probabilities.
    Returns a scalar.

    Parameters:
    - single_p, a w x k numpy array of singleton marginal probabilities,
      where n is the word length and k is the size of the alphabet;
    - label, a list of character labels; and
    - alphabet, a list of all possible character labels.
    """

    p = [np.log(marginal[alphabet.index(c)]) for (c, marginal) in zip(label, single_p)]

    return np.sum(p)

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

    return -np.sum(p)/len(data)

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

    return np.ndarray.flatten(np.negative(gradient))

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

    return np.ndarray.flatten(np.negative(gradient))

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

def predict_word(single_p, alphabet):
    """
    Returns a list of predicted characters of a word.

    Parameters:
    - single_p, a w x k numpy array of singleton marginal probabilities,
      where w is the word length and k is the size of the alphabet; and
    - alphabet, a list of all possible character labels.
    """

    indices = np.argmax(single_p, axis=1)

    return [alphabet[i] for i in indices]

def predict(theta, data, alphabet):
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