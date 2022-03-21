import argparse
import functools
import itertools as it
from multiprocessing import Pool
import os, sys
import networkx as nx
import rust

# graph_tool can't be installed via pip. If you're using pip as your
# package manager, then you likely cannot use find_edge_swap_gt below
# as it uses graph_tool. Note that this is somewhat irrelevant, as the
# high performance version of this code uses a Rust implementation of
# the find_edge_swap method, circumventing any use of graph_tool.
try:
    import graph_tool.all as gt
    import graph_tool.topology as tg
except:
    pass


def all_vertices_deg2(F):
    """
    Checks if all vertices of F have degree 2
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


def tgen(n):
    """
    Generate T(n) = {-1,0,1}^n - (0,...,0)
    """
    Ls = [[-1, 0, 1] for _ in range(n)]
    for val in it.product(*Ls):
        # if zero tuple then continue....
        if all([e == 0 for e in val]):
            continue
        yield val


def snng_parallel(n, k):
    """
    Generate Snng(n) up to index k
    """
    Ls = [
        list(set(range(n)) - set([(i-1)%n, i, (i+1)%n]))
        for i in range(k)
    ]
    for mapval in it.product(*Ls):
        yield list(mapval)


def quit(arg, pool):
    if arg is None:
        pass
    else:
        global counterexample
        counterexample = arg
        pool.terminate() # kill all pool workers


def find_edge_swap_gt(n, k, suffix, proc):
    with open(
        os.path.join(gnuprocdir, f"out{proc}.txt"), "w"
    ) as f:
        f.write("started\n")

    F = gt.Graph(directed=False)
    F.set_fast_edge_removal(fast=True)
    edgelist = [(i, (i + 1) % n) for i in range(n)]
    F.add_edge_list(edgelist)
    # G = F.copy()
    
    for prefix in snng_parallel(n, k):
        sig = prefix + suffix
        foundswap = False
        for t in tgen(n):
            for i in range(n):
                e = F.edge(i, (i+t[i])%n)
                if e in F.edges():
                    F.remove_edge(e)
                    F.add_edge(i, sig[i])

            iscycle = (
                list(tg.label_components(F)[0]) == n*[0] and
                all(F.get_total_degrees(F.get_vertices()) == 2)
            )
            # iscycle = tg.isomorphism(F, G)

            F.clear_edges()
            F.add_edge_list(edgelist)
            if iscycle:
                foundswap = True
                break

        if not foundswap:
            return [sig, t]

    with open(
        os.path.join(gnuprocdir, f"out{proc}.txt"), "a"
    ) as f:
        f.write("finished\n")


def find_edge_swap_nx(n, k, suffix, proc):
    with open(
        os.path.join(gnuprocdir, f"out{proc}.txt"), "w"
    ) as f:
        f.write("started\n")

    F = nx.Graph()
    edgelist = [(i, (i+1)%n) for i in range(n)]
    F.add_edges_from(edgelist)

    for prefix in snng_parallel(n, k):
        sig = prefix + suffix
        foundswap = False
        for t in tgen(n):
            for i in range(n):
                if F.has_edge(i, (i+t[i])%n):
                    F.remove_edge(i, (i+t[i])%n)
                    F.add_edge(i, sig[i])

            iscycle = cycle(F)
            F.remove_edges_from(list(F.edges()))
            F.add_edges_from(edgelist)

            if iscycle:
                foundswap = True
                break

        if not foundswap:
            return [sig, t]

    with open(
        os.path.join(gnuprocdir, f"out{proc}.txt"), "a"
    ) as f:
        f.write("finished\n")


def find_edge_swap_rust(n, k, suffix, proc):
    with open(
        os.path.join(gnuprocdir, f"out{proc}.txt"), "w"
    ) as f:
        f.write("started\n")

    # call rust-implemented binary for warp-speed implementation
    result = rust.find_edge_swap(n, k, suffix)

    if result is not None:
        return list(result)

    with open(
        os.path.join(gnuprocdir, f"out{proc}.txt"), "a"
    ) as f:
        f.write("finished\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--mid", type=str, required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--q", type=int, required=True)
    parser.add_argument("--gnuproc", type=int, required=True)
    mid = eval(parser.parse_args().mid)
    n = parser.parse_args().n
    p = parser.parse_args().p
    q = parser.parse_args().q
    gnuproc = parser.parse_args().gnuproc

    gnuprocdir = os.path.join(f"tour-reports-{n}", f"gnuproc{gnuproc}")
    if not os.path.exists(gnuprocdir):
        os.mkdir(gnuprocdir)

    suffixes = [
        list(set(range(n)) - set([(i-1)%n, i, (i+1)%n]))
        for i in range(n - q, n)
    ]
    counterexample = None
    pool = Pool()
    method = find_edge_swap_rust

    for i, suffix in enumerate(it.product(*suffixes)):
        func = functools.partial(
            method,
            n=n,
            k=n-(p+q),
            suffix=mid + list(suffix),
            proc=i,
        )
        callback = functools.partial(quit, pool=pool)
        pool.apply_async(func, callback=callback)
    pool.close()
    pool.join()

    if counterexample is not None:
        with open(gnuprocdir + "/failed.txt", "w") as f:
            f.write(
                f"gnuproc {gnuproc}\t\t" +
                f"found counterexample: {counterexample}"
            )
        sys.exit(1)
    else:
        with open(gnuprocdir + "/success.txt", "w") as f:
            f.write(
                f"gnuproc {gnuproc}\t\t" +
                "completed without finding a counterexample"
            )
