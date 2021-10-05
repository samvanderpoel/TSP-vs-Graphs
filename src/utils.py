import numpy as np
import networkx as nx

def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def num_common_edges(g1, g2):
    num_common = 0
    for e in g2.edges():
        if g1.has_edge(*e):
            num_common += 1
    return num_common

def graph_to_yaml(graph, comp, dirname):
    """
    Writes the coordinates of a nx graph to a yaml file.
        graph:
            nx graph
        comp:
            comparison id, of the form 'majorid_minorid'
        dirname:
            dir in which to create anomalies folder and write yaml files
    """
    points = [graph.nodes[node]["pos"] for node in list(graph.nodes)]
    n = len(points)
    anom_dir = os.path.join(dirname, 'anomalies/' + comp)
    if not os.path.isdir(anom_dir):
        os.makedirs(anom_dir)
    timenow = str(datetime.datetime.now()).replace('-','').replace(' ','').replace(':','').replace('.','')
    filepath = os.path.join(anom_dir, str(n) + '_' + timenow + '.yaml')
    with open(filepath, 'w+') as file:
        file.write('points:\n')
        for point in points:
            file.write('  - [{a},{b}]\n'.format(a=point[0], b=point[1]))

def compare(d, comp, g1, g2, div, anomalies, dirname):
    """
    Compares two dictionaries g1, g2 of graphs indexed by iteration
        d:
            dictionary that stores graph intersection data by comparison type
        comp:
            string of the form 'majorid_minorid'
        g1, g2:
            dictionaries of graphs indexed by iteration
        div:
            n or n-1, depending whether g1 contains paths or cycles
    """
    #print('Working on comparison: ' + comp)
    n = len(g1)
    new_data = []
    for i in range(n):
        common = num_common_edges(g1[i], g2[i]) / div
        new_data += [common]
        if comp in anomalies and common < anomalies[comp]:
            graph_to_yaml(g1[i], comp, dirname)
    d[comp] = new_data
    #print('Finished comparison: ' + comp)
