import argparse
import functools
import sys, os
import networkx as nx
import itertools
from multiprocessing import Pool

parser = argparse.ArgumentParser()
parser.add_argument('--n', type=int, required=True)
parser.add_argument('--p', type=int, required=True)
n = parser.parse_args().n
p = parser.parse_args().p # (n-3)^p processes will be running

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
        print(5*'\n' + 40*'*')
        print('The culprit is ' + str(arg[0]) + \
              ' with edge exchange ' + str(arg[1]))
        print(40*'*' + 5*'\n')
        global result
        result = 'False'
        pool.terminate()  # kill all pool workers

def find_edge_swap(n, k, suffix, proc):
    print('started proc ' + str(proc), file = sys.stdout)
    with open('tour-reports-' + str(n) + '/out' + \
              str(proc) + '.txt', 'w') as f:
        f.write('started\n')
    for prefix in snng_parallel(n, k):
        sig = prefix + suffix
        foundswap = False
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
                foundswap = True
                break
        if not foundswap:
            return [sig, t]
    print('finished proc ' + str(proc), file = sys.stdout)
    with open('tour-reports-' + str(n) + '/out' + \
              str(proc) + '.txt', 'a') as f:
        f.write('finished\n')

if __name__ == '__main__':
    if not os.path.exists('tour-reports-' + str(n)):
        os.mkdir('tour-reports-' + str(n))
    suffixes = [list( set(range(n))-set([(i-1)%n,i,(i+1)%n]) ) \
                for i in range(n-p, n)]
    result = 'True'
    pool = Pool()
    for i, suffix in enumerate(itertools.product(*suffixes)):
        pool.apply_async(functools.partial(find_edge_swap,
                                           n=n,
                                           k=n-p,
                                           suffix=list(suffix),
                                           proc=i),
                         callback=quit)
    pool.close()
    pool.join()
    print(result)
