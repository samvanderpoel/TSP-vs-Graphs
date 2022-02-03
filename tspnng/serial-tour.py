import sys, os, random, time, colorama, yaml
from colorama import Fore, Style
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import networkx as nx
import itertools
from sympy.utilities.iterables import multiset_permutations
import copy
import graphviz


# For Enabling Latex inside plots
plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Palatino"],
    }
)


def tgen(n):
    """Generate the set T(n) = {-1,0,1}^n"""
    Ls = [[-1, 0, 1] for _ in range(n)]
    for val in itertools.product(*Ls):
        # if zero tuple then continue....
        if all([e == 0 for e in val]):
            continue
        yield val


def snng(n):
    """Generate the set SNNG(n) as given in Sam's pseudocode.
    This is a generator function that yields the values
    of the (\sigma_0, \sigma_1, \ldots, \sigma_n-1)
    """
    Ls = []
    for i in range(n):
        L = list(range(n))
        L.remove((i - 1) % n)
        L.remove(i)
        L.remove((i + 1) % n)
        Ls.append(L)

    for mapval in itertools.product(*Ls):
        yield mapval


def all_vertices_deg2_p(F):
    """Predicate to check is all vertices of the supplied graph have degree 2"""
    nodes = list(F.nodes())
    deg_sequence = [F.degree(node) for node in nodes]

    temp = True
    for d in deg_sequence:
        if d != 2:
            temp = False
            break
    return temp


def cycle_p(F):
    """Predicate to check if the supplied graph is a cycle"""
    return nx.is_connected(F) and all_vertices_deg2_p(F)


def tournng_p(n):

    for sig in snng(n):
        print(sig)
        temp = False
        for t in tgen(n):
            F = nx.Graph()
            for i in range(n):
                F.add_edge(i, (i + 1) % n)
            for i, ti in enumerate(t):
                if ti in [-1, 1]:
                    try:
                        F.remove_edge(i, (i + ti) % n)
                    except:
                        pass
                    F.add_edge(i, sig[i])
            if cycle_p(F):
                print("Edge swap: " + str(t))
                print("New edges: " + str(list(F.edges())))
                temp = True
                break
        if temp == False:
            return False
    return True


if __name__ == "__main__":
    n = 8
    print("\nTournng for n=", n, " is ")
    print(tournng_p(n))
