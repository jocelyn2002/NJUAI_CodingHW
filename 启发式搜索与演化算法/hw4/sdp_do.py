import sys
import networkx as nx
import numpy as np
import _sdp
def CreateGraph(n,w):
    nodeList = range(n)  # node id ranges from zero to n
    # Make G undirected.
    G = nx.Graph()
    G.add_nodes_from(nodeList)
    # Allocate weights to the edges.
    for i in range(n-1):
        for j in range(i+1, n):
            if w[i, j] > 0:
                G.add_edge(i, j, weight=w[i, j])
    return G
def MaxCut(n,weightMaxtirx):
    graph=CreateGraph(n,weightMaxtirx)
    mysdp = _sdp.MaxCutSDP(graph, solver='cvxopt')
    mysdp.solve()
    cut = mysdp.get_results('cut')
    return [i for i in range(n) if cut[0,i]>=0]


def ReformalizeWeightMatrix(n,data,*args):
    for i in range(n-1):
        for j in range(i,n):
            if data[i,j]<0.5:#means data[i,j]==0
                for item in args:
                    item[i,j]=0.0
                    item[j,i]=0.0
            else:
                for item in args:
                    item[j,i]=item[i,j]
if __name__=="__main__":
    print('start')
    n = 7
    w = np.mat(np.random.rand(n, n))
    w[4,3]=0
    w[3,4]=0
    w[2,5]=0
    w[5,2]=0
    w[6,0]=0
    w[0,6]=0
    w[1,5]=0
    w[5,1]=0
    w[0,6]=0
    w[6,0]=0
    w[4,2]=0
    w[2,4]=0
    w[3,1]=0
    w[1,3]=0
    w[6,5]=0
    w[5,6]=0
    w[0,4]=0
    w[4,0]=0
    w[3,0]=0
    w[0,3]=0
    for i in range(n):
        for j in range(i,n):
            if i==j:
                w[i,j]=0
            w[j,i]=w[i,j]
    print(w)
    graph=CreateGraph(n,w)
    #print(nx.laplacian_matrix(graph).todense())

    cut=MaxCut(n, w)
    print(cut)


