# coding: utf-8

"""Backend class and functions for max-cut solvers."""

from abc import ABCMeta, abstractmethod

import networkx as nx
import numpy as np


class AbstractMaxCut(metaclass=ABCMeta):
    """Abstract class for Max-Cut problem solvers."""

    def __init__(self, graph):
        """Instantiate the solver."""
        self.graph = graph
        self._results = None

    def get_results(self, item='cut', verbose=False):
        """Return the lazy-evaluated max-cut results reached.

        item : whether to return the 'cut' itself, its 'value'
               or the initial 'matrix' solving the SDP program
        """
        if self._results is None:
            self.solve(verbose)
        if item not in self._results:
            valid = ', '.join(["'%s'" % key for key in self._results.keys()])
            raise KeyError(
                "In valid 'item' keyword: should be one of {{%s}}." % valid
            )
        return self._results.get(item)

    @abstractmethod
    def solve(self, verbose=True):
        """Solve the BM-formulated max-cut problem using RTR.

        Resulting cut, value of the cut and solved matrix
        may be accessed through the `get_solution` method.
        """
        return NotImplemented


def get_partition(vectors,graph):
    """Cut a graph based on a matricial solution using randomized rounding.

    vectors   : matrix of vectors of unit norm (as rows),
                defining the cut probabilities to round up

    Use the Goemans-Williamson rounding technique, deciding which
    set to assign each node depending on the sign of the dot product
    between said node's vector and a random unit-norm one.

    Return a list of {{-1, +1}} values indicating to which part
    each node belongs.
    """
    # Pick a random vector on the unit sphere.
    #random = np.random.normal(size=vectors.shape[1])
    #random /= np.linalg.norm(random, 2)
    # Compute partition probabilities and round the cut.
    L = 1.0 / 4.0 * nx.laplacian_matrix(graph).todense()
    #print(np.sum(L))
    obj=0.0
    count=0
    while count<100:
        random_value = np.random.normal(size=vectors.shape[1])
        x=np.mat(np.sign(np.dot(vectors, random_value)))
        o=(x*L*x.T)[0,0]
        if o>obj:
            obj=o
            x_cut=x
        count+=1
    return x_cut


def get_cut_value(graph, partition):
    """Compute the share of edges' weights in a given cut.

    graph     : graph being cut off
    partition : list of {{-1, +1}} values indicating
                to which part each node belongs
    """
    '''
    in_cut = sum(
        attr['weight'] for u, v, attr in graph.edges(data=True)
        if partition[0,u] != partition[0,v]
    )
    '''
    L = 1.0 / 4.0 * nx.laplacian_matrix(graph).todense()
    o = (partition * L * partition.T)[0, 0]

    #total = .5 * nx.adjacency_matrix(graph).sum()
    #print(in_cut,total)
    return o
