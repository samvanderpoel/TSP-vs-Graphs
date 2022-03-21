import argparse
import networkx as nx
import itertools


def tgen(n):
    """
    Yield elements of the set T(n) = {-1,0,1}^n - {(0,...,0)}
    """
    Ls = [[-1, 0, 1] for _ in range(n)]
    for val in itertools.product(*Ls):
        # if zero tuple then continue....
        if all([e == 0 for e in val]):
            continue
        yield val


def snng(n):
    """
    Yield elements of the set S_NNG(n).
    """
    Ls = [
        list(set(range(n)) - set([(i - 1) % n, i, (i + 1) % n]))
        for i in range(n)
    ]

    for mapval in itertools.product(*Ls):
        yield mapval


def all_vertices_deg2(F):
    """
    Check if all vertices have degree 2
    """
    nodes = list(F.nodes())
    deg_sequence = [F.degree(node) for node in nodes]

    temp = True
    for d in deg_sequence:
        if d != 2:
            temp = False
            break
    return temp


def cycle(F):
    """
    Check if F is a cycle
    """
    return nx.is_connected(F) and all_vertices_deg2(F)


def tour_nng(n):

    F = nx.Graph()
    edgelist = [(i, (i+1)%n) for i in range(n)]
    F.add_edges_from(edgelist)

    for sig in snng(n):
        temp = False
        for t in tgen(n):
            for i in range(n):
                if F.has_edge(i, (i+t[i])%n):
                    F.remove_edge(i, (i+t[i])%n)
                    F.add_edge(i, sig[i])
            
            iscycle = cycle(F)
            F.remove_edges_from(list(F.edges()))
            F.add_edges_from(edgelist)

            if cycle(F):
                temp = True
                break

        if temp == False:
            return False
    
    return True


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    n = parser.parse_args().n
    print(f"Result for n={n}: {tour_nng(n)}")
