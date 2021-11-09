import argparse
import functools
import sys, os
import networkx as nx
import itertools
from multiprocessing import Pool

parser = argparse.ArgumentParser()
parser.add_argument('--mid', type=str, required=True)
parser.add_argument('--n', type=int, required=True)
parser.add_argument('--p', type=int, required=True)
parser.add_argument('--q', type=int, required=True)
parser.add_argument('--gnuproc', type=int, required=True)
mid = eval(parser.parse_args().mid)
n = parser.parse_args().n
p = parser.parse_args().p
q = parser.parse_args().q
gnuproc = parser.parse_args().gnuproc

def all_vertices_deg2_p(F):
    """
    Checks if all vertices of F have degree 2
    """
    nodes        = list( F.nodes() )
    deg_sequence = [F.degree(node) for node in nodes]

    temp = True
    for d in deg_sequence:
        if d!=2 :
            temp = False
            break
    return temp

def cycle_p(F):
    """
    Check if F is a cycle
    """
    return nx.is_connected(F) and all_vertices_deg2_p(F)

def tgen(n):
    """
    Generate T(n) = {-1,0,1}^n - (0,...,0)
    """
    Ls = [[-1,0,1] for _ in range(n)]
    for val in itertools.product(*Ls):
        # if zero tuple then continue....
        if all( [e == 0 for e in val] ): 
            continue
        yield val

def snng_parallel(n, k):
    """
    Generate Snng(n) up to index k
    """
    Ls = [list(set(range(n))-set([(i-1)%n, i, (i+1)%n])) for i in range(k)]
    for mapval in itertools.product(*Ls):
        yield list(mapval)

def quit(arg):
    if arg is None:
        pass
    else:
        global counterexample
        counterexample = arg
        pool.terminate()  # kill all pool workers

def find_edge_swap(n, k, suffix, proc):
    with open(gnuprocdir + '/out' + str(proc) + '.txt', 'w') as f:
        f.write('started\n')
    F = nx.Graph()
    edgelist = [(i, (i+1)%n) for i in range(n)]
    F.add_edges_from(edgelist)
    for prefix in snng_parallel(n, k):
        sig = prefix + suffix
        foundswap = False
        for t in tgen(n):
            for i in range(n):
                if t[i] == -1 or t[i] == 1:
                    try:
                        F.remove_edge(i, (i+t[i])%n)
                    except:
                        pass
                    F.add_edge(i, sig[i])
            iscycle = cycle_p(F)
            F.remove_edges_from(list(F.edges()))
            F.add_edges_from(edgelist)
            if iscycle:
                foundswap = True
                break
        if not foundswap:
            return [sig, t]
    with open(gnuprocdir + '/out' + str(proc) + '.txt', 'a') as f:
        f.write('finished\n')

if __name__ == '__main__':
    gnuprocdir = 'tour-reports-' + str(n) + '/gnuproc' + str(gnuproc)
    if not os.path.exists(gnuprocdir):
        os.mkdir(gnuprocdir)
    suffixes = [list( set(range(n))-set([(i-1)%n,i,(i+1)%n]) ) \
                for i in range(n-q, n)]
    counterexample = None
    pool = Pool()
    for i, suffix in enumerate(itertools.product(*suffixes)):
        func = functools.partial(find_edge_swap,
                                 n=n,
                                 k=n-(p+q),
                                 suffix=mid+list(suffix),
                                 proc=i)
        pool.apply_async(func, callback=quit)
    pool.close()
    pool.join()
    if counterexample is not None:
        with open(gnuprocdir + '/failed.txt', 'w') as f:
            f.write('gnuproc ' + str(gnuproc) + '\t\tfound counterexample: ' + \
                    str(counterexample))
        sys.exit(1)
    else:
        with open(gnuprocdir + '/success.txt', 'w') as f:
            f.write('gnuproc ' + str(gnuproc) + \
                    '\t\tcompleted without finding a counterexample')
