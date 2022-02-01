import numpy as np
import networkx as nx
import os
import datetime


def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def num_common_edges(g1, g2):
    num_common = 0
    for e in g2.edges():
        if g1.has_edge(*e):
            num_common += 1
    return num_common


def minus(g1, g2):
    # returns the nx graph g1-g2
    g = nx.Graph()
    for e in g1.edges():
        if not g2.has_edge(*e):
            g.add_edge(*e)
    return g


def graph_to_yaml(graph, dirname):
    """
    Writes the coordinates of a nx graph to a yaml file.
        graph:
            nx graph
        dirname:
            dir in which to create anomalies folder and write yaml files
    """
    points = [graph.nodes[node]["pos"] for node in list(graph.nodes)]
    n = len(points)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    now = str(datetime.datetime.now())
    strnow = now.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")
    filepath = os.path.join(dirname, str(n) + "_" + strnow + ".yaml")
    with open(filepath, "w+") as file:
        file.write("points:\n")
        for point in points:
            file.write("  - [{a},{b}]\n".format(a=point[0], b=point[1]))


def compare(d, comp, g1, g2, anomalies, dirname):
    """
    Compares two dictionaries g1, g2 of graphs indexed by iteration
        d:
            dictionary that stores graph intersection data by comparison type
        comp:
            string of the form 'majorid_minorid'
        g1, g2:
            dictionaries of graphs indexed by iteration
    """
    # print('Working on comparison: ' + comp)
    n = len(g1)
    new_data = []
    for i in range(n):
        common = num_common_edges(g1[i], g2[i]) / len(list(g1[i].edges()))
        new_data += [common]
        if comp in anomalies:
            criterion = eval("common" + anomalies[comp])
            if criterion:
                graph_to_yaml(g1[i], os.path.join(dirname, "anomalies/" + comp))
    d[comp] = new_data
    # print('Finished comparison: ' + comp)
