import argparse
import functools
import sys, os
import networkx as nx
import itertools
from multiprocessing import Process, Pool

parser = argparse.ArgumentParser()
parser.add_argument('--n', type=int, required=True)
parser.add_argument('--p', type=int, required=True)
n = parser.parse_args().n
p = parser.parse_args().p # (n-3)^p processes will be running

#---------------------------------------------------------------------------
def tgen(n):
    """ Generate the set T(n) = {-1,0,1}^n 
    """
    Ls = [[-1,0,1] for _ in range(n)]
    for val in itertools.product(*Ls):
        # if zero tuple then continue....
        if all( [e == 0 for e in val] ): 
            continue
        yield val

#----------------------------------------------------------------------------------------
def snng(n):
    """ Generate the set SNNG(n) as given in Sam's pseudocode. 
    This is a generator function that yields the values 
    of the (\sigma_0, \sigma_1, \ldots, \sigma_n-1) 
    """
    Ls = []
    for i in range(n):
        L = list(range(n))
        L.remove((i-1)%n)
        L.remove(i)
        L.remove((i+1)%n)
        Ls.append(L)

    for mapval in itertools.product(*Ls):
        yield mapval

#----------------------------------------------------------------------------------------
def all_vertices_deg2_p(F):
    """ Predicate to check is all vertices of the supplied graph have degree 2
    """
    nodes        = list( F.nodes() )
    deg_sequence = [F.degree(node) for node in nodes]

    temp = True
    for d in deg_sequence:
        if d!=2 :
            temp = False
            break
    return temp

#-----------------------------------------------------------------------------------------
def cycle_p(F):
    """ Predicate to check if the supplied graph is a cycle
    """
    return nx.is_connected(F) and all_vertices_deg2_p(F)

#----------------------------------------------------------------------------------------
def tournng_p (n):

    for sig in snng(n):
        print(sig)
        temp = False
        for t in tgen(n):
            F = nx.Graph()
            for i in range(n):
                F.add_edge(i,(i+1)%n)
            for i, ti in enumerate(t):
                if ti in [-1,1]:
                    try:
                        F.remove_edge(i, (i+ti)%n)
                    except:
                        pass
                    F.add_edge(i, sig[i])
            if cycle_p(F):
                print('Edge swap: ' + str(t))
                print('New edges: ' + str(list(F.edges())))
                temp = True
                break
        if temp == False:
            return False
    return True

#----------------------------------------------------------------------------------------

def snng_parallel(n, k):
    Ls = [list(set(range(n))-set([(i-1)%n, i, (i+1)%n])) for i in range(k)]
    for mapval in itertools.product(*Ls):
        yield list(mapval)

def find_edge_swap(n, k, suffix, proc):
    print('started proc ' + str(proc), file = sys.stdout)
    with open('tour-reports/out' + str(proc) + '.txt', 'w') as f:
        f.write('started\n')
    for prefix in snng_parallel(n, k):
        sig = prefix + suffix
        # print(sig)
        temp = False
        for t in tgen(n):
            F = nx.Graph()
            for i in range(n):
                F.add_edge(i,(i+1)%n)
            for i, ti in enumerate(t):
                if ti in [-1,1]:
                    try:
                        F.remove_edge(i, (i+ti)%n)
                    except:
                        pass
                    F.add_edge(i, sig[i])
            if cycle_p(F):
                # print('Edge swap: ' + str(t))
                # print('New edges: ' + str(list(F.edges())))
                temp = True
                break
        if temp == False:
            print('False')
            sys.exit(1)
    print('finished proc ' + str(proc), file = sys.stdout)
    with open('tour-reports/out' + str(proc) + '.txt', 'a') as f:
        f.write('finished\n')

def tournng(n, p):
    suffixes = [list(set(range(n))-set([(i-1)%n, i, (i+1)%n])) for i in range(n-p, n)]
    pool = Pool()
    for i, suffix in enumerate(itertools.product(*suffixes)):
        pool.apply_async(functools.partial(find_edge_swap,
                                           n=n,
                                           k=n-p,
                                           suffix=list(suffix),
                                           proc=i))
    pool.close()
    pool.join()
    print('True')

if __name__ == '__main__':
    if not os.path.exists('tour-reports'):
        os.mkdir('tour-reports')
    tournng(n, p)
