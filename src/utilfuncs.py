import numpy as np
import networkx as nx

def num_common_edges(g1, g2):
    num_common = 0
    for e in g2.edges():
        if g1.has_edge(*e):
            num_common += 1
    return num_common

def graphs_intersect_p(g1,g2):
    flag = False
    if list_common_edges(g1,g2):     
        flag = True 
    return flag
