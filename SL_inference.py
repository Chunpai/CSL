__author__ = 'Chunpai W.'
 
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pdb
import copy
from readAPDM import readAPDM
import random
#from SLOperators import transitivity
#from SLOperators import fusion
from random import randint
from DataWrapper import *





global paths
paths = [] 
global path
path = []

def findPaths(G, source, target, threshold=10):
    arcs = []
    for nei in nx.neighbors(G,source):
        arc = (source,nei)
        length = len(path)
        #path_copy = copy.copy(path)
        count = 0
        for (i,j) in path:
            if nei != i and nei != j:
                count += 1
        if count == length:    
            arcs.append(arc)
    for arc in arcs:
        if arc[1] == target and len(path) + 1 <= threshold:
            path_copy = copy.copy(path)
            path_copy.append(arc)
            paths.append(path_copy)
        elif arc[1] != target and len(path) + 1 <= threshold:
            path.append(arc)
            findPaths(G,arc[1],target,threshold)
            path.remove(arc)


'''
V = [0, 1, ...] is a list of vertex ids
E: a list of pairs of vertex ids
Obs: a dictionary with key edge and its value a list of congestion observations of this edge from t = 1 to t = T
Omega: a dictionary with key edge and its value a pair of alpha and beta
E_X: a list of pairs of vertex ids whose opinions will be predicted.
'''
def SL_prediction(V,E,Obs,Omega,E_X,flag = 0):
    '''
    flag == 0:  if no path between (i,j), fuse opinions of neighbors' edges of i and j 
         == 1:  not consider fusing neighbor edges
    '''
    if flag == 0:
        G = nx.Graph()   #used for traffic dataset
    elif flag == 1:
        G = nx.DiGraph()  # used for trustness dataset
    else:
        raise Exception('Wrong flag argument')

    E_known = [e for e in E if e not in E_X]
    G.add_nodes_from(V)
    Omega_X = {}
    #print 'number of known edges',len(E_known)

    for e in E_known:
        source, target = e
        alpha, beta = Omega[e]
        op = beta_to_opinion(alpha,beta)
        G.add_edge(source,target,opinion=op)
    #print 'number of training edges:',len(G.edges())

    Omega_X = {}
    if flag == 0:
        #print 'flag == 0' 
        while(len(E_X)!=0):
            for e in E_X:
                source, target = e
                #case 1
                if source not in G.nodes() and target not in G.nodes():
                    #print 'not in G',source,target
                    #print len(E_X)
                    continue
                #case 2
                elif source not in G.nodes():# or target not in G.nodes():
                    G.add_node(source)
                    neis = G.neighbors(target)
                    multi_paths = []
                    neighbor_path = []
                    for nei in neis:
                        if (target,nei) in G.edges():
                            neighbor_path.append((target,nei))
                        if (nei, target)in G.edges():
                            neighbor_path.append((nei,target))
                    if neighbor_path == []:
                        raise Exception('errrror 1')
                    else:
                        multi_paths.append(neighbor_path)
                    op = computeOpinion(G,e,multi_paths)
                    G.add_edge(source,target,opinion = op)
                    Omega_X[e] = opinion_to_beta(op)
                    E_X.remove(e)
                #case 3
                elif target not in G.nodes(): 
                    G.add_node(target)
                    neis = G.neighbors(source)
                    multi_paths = []
                    neighbor_path = []
                    for nei in neis:
                        if (source,nei) in G.edges():
                            neighbor_path.append((source,nei))
                        if (nei, source)in G.edges():
                            neighbor_path.append((nei,source))
                    if neighbor_path == []:
                        raise Exception('errrror 1')
                    else:
                        multi_paths.append(neighbor_path)
                    op = computeOpinion(G,e,multi_paths)
                    G.add_edge(source,target,opinion = op)
                    Omega_X[e] = opinion_to_beta(op)
                    E_X.remove(e)
                #case 4
                else:
                    findPaths(G,source, target)
                    global paths
                    #print e, paths
                    if paths != []:
                        total_opinion = computeOpinion(G,e,paths)
                        G.add_edge(source, target, opinion = total_opinion)
                        Omega_X[e] = opinion_to_beta(total_opinion)
                        paths = []
                        E_X.remove(e) 
                    else:
                        neis = G.neighbors(source) + G.neighbors(target)
                        multi_paths = []
                        neighbor_path = []
                        for nei in neis:
                            if (source,nei) in G.edges():
                                neighbor_path.append((source,nei))
                            if (nei, source)in G.edges():
                                neighbor_path.append((nei,source))
                            if (target,nei) in G.edges():
                                neighbor_path.append((target,nei))
                            if (nei,target) in G.edges():
                                neighbor_path.append((nei,target))
                        if neighbor_path != []:
                            multi_paths.append(neighbor_path)
                            total_opinion = computeOpinion(G,e,multi_paths)
                            G.add_edge(source, target, opinion = total_opinion)
                            Omega_X[e] = opinion_to_beta(total_opinion)
                            E_X.remove(e) 
    elif flag == 1:
        while(len(E_X)!=0):
            for e in E_X:
                #print 'testing edge',e
                source, target = e
                findPaths(G,source, target)
                global paths
                #print e, paths
                if paths != []:
                    total_opinion = computeOpinion(G,e,paths)
                    G.add_edge(source, target, opinion = total_opinion)
                    Omega_X[e] = opinion_to_beta(total_opinion)
                    paths = []  #set global variable paths to [] to ensure next function call of findPaths()
                    E_X.remove(e)                
                else:
                    raise Exception('no path found on edge:',e)
    else:
        raise Exception('wrong flag parameter')
    #print G.number_of_nodes()
    #print G.number_of_edges()
    return Omega_X




def beta_to_opinion(alpha,beta,W=2.0,a=0.5):
    '''
    compute opinion based on hyperparameters of beta distribution
    '''
    if alpha == 0:
        alpha += 0.01
    if beta == 0:
        beta += 0.01
    b = (alpha - W*a)/float(alpha+beta)
    d = (beta - W*(1-a))/float(alpha+beta)
    u = (W)/float(alpha+beta)
    return [b,d,u,a]
  


def opinion_to_beta(op,W=2.0):
    '''
    convert opinion to hyperparameters of beta distribution
    op is opinion : list
    '''
    b,d,u,a = op
    #alpha = W*a + (b*W/u) 
    #beta = (W-u*W*a-b*W)/u 
    r = b * W / u
    s = d * W / u
    alpha = r + a * W
    beta = s + (1-a) * W
    return (alpha,beta)



def obs_to_omega(obs):
    '''
    get Omega based on observation dict
    input:
        obs: (dict) key is edge, value is a list of obs of the edge
    output:
        Omega: (dict) key is the edge (tuple), value is (alpha,beta)
    '''
    Omega = {}
    for e in obs:
        obs_list = obs[e]
        alpha = np.count_nonzero(obs_list) 
        beta = len(obs_list) - alpha
        if e not in Omega:
            Omega[e] = (alpha,beta)
        else:
            raise Exception("HAHA ERROR: Duplicate Edges")
    return Omega
    

 
def computeOpinion(G,e,multi_paths): 
    '''
    input:
        G: a graph, networkx graph object
        e: is (source, target), whose opinion you want to predict
        multi_paths: [[],[]] 2D list, each sublist is a edge path from source to target
    output:
        total_opinion: [b,d,u,a]      
    '''
    if multi_paths == []:
        raise error('Empty Path')
        return  
    else:
        #print 'multi_paths',multi_paths
        paths_opinion_list = []
        for p in multi_paths:
            opinion_path = []
            for arc in p:
                o = G[arc[0]][arc[1]]['opinion'] 
                opinion_path.append(o)   
            path_opinion = opinion_path[0]
            for i in range(1,len(opinion_path)):
                path_opinion = transitivity(path_opinion,opinion_path[i])
            paths_opinion_list.append(path_opinion)
        total_opinion = paths_opinion_list[0] 
        for i in range(1,len(paths_opinion_list)):
            total_opinion = fusion(total_opinion, paths_opinion_list[i]) 
        return total_opinion 


"""
INPUT: o1, o2 have the format (-belief, disbelief, uncertainty, base)
"""
def transitivity(o1, o2):
    o = [0, 0, 0, 0]
    o[0] = o1[0] * o2[0]
    o[1] = o1[0] * o2[1]
    o[2] = o1[1] + o1[2] + o1[0] * o2[2]
    o[3] = o2[3]
    return o

def fusion(o1, o2):
    o = [0, 0, 0, 0]
    o[0] = (o1[0] * o2[2] + o2[0] * o1[2]) / (o1[2] + o2[2] - o1[2] * o2[2])
    o[1] = (o1[1] * o2[2] + o2[1] * o1[2]) / (o1[2] + o2[2] - o1[2] * o2[2])
    o[2] = (o1[2] * o2[2]) / (o1[2] + o2[2] - o1[2] * o2[2])
    o[3] = o1[3]
    return o


def test():    
    V, E, Obs, Omega = readAPDM('APDM-IRIX-DC-2014-03-01.txt')
    sizeE = len(E)
    print sizeE
    
    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_edges_from(E)
    print sorted(nx.connected_components(G), key = len, reverse=True)
    '''
    E_X = random.sample(E,int(sizeE*0.05))
    print len(E_X)
    print 'unknown edges: ',E_X
    Omega_X = SL_prediction(V,E,Obs,Omega,E_X)
    '''  



def test1():
    G = nx.DiGraph()
    V = [1,2,3,4,5,6,7,8,9,10,11]
    E = [(1,2),(1,3),(2,4),(3,5),(2,6),(3,6),(6,7),(7,8),(4,9),(5,10),(7,9),(8,10),(7,11),(8,11)]
    G.add_nodes_from(V)
    G.add_edges_from(E)    
    Omega = {}
    for e in G.edges():
        alpha = randint(2,7)
        beta = 10 - alpha
        Omega[e] = [alpha,beta]
    E_X = [(4,9),(3,6),(7,9),(8,10)]
    #print Omega
    #nx.draw_networkx(G)
    Omega_X = SL_prediction(V,E,Omega,E_X)    
    for e in Omega_X:
        print '\nedge',e
        print 'predicted opinion',beta_to_opinion(Omega_X[e][0],Omega_X[e][1])
        alpha, beta = Omega[e]
        print 'true opinion',beta_to_opinion(alpha,beta)
    #print Omega_X

     


def pipeline(percent=0.05):

    dw = DataWrapper()
    V, E, Obs, G = dw.data_wrapper()
    print('number of nodes: {}'.format(len(V)))
    print('number of edges: {}'.format(len(E)))
    print('number of cc: {}'.format(nx.number_connected_components(G)))
    
    Omega = obs_to_omega(Obs)
    sizeE = len(E)
    E_X = random.sample(E,int(round(sizeE*percent)))
    X_copy = [e for e in E_X]
    Omega_X = SL_prediction(V,E,Omega,X)
       
    

if __name__ == '__main__':
    #test()
    #test1()
    pipeline(V,E,Obs)
