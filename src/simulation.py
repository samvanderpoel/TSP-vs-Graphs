import functools
from multiprocessing import Process, Queue, Manager
import numpy as np
import networkx as nx

import argparse
import os
import time

from graphfuncs import *
from utils import *
from point_distributions import *

"""
Graphs are classified with either a major_id or minor_id.
Graphs with major_id include:
    - TSP tour:     'tour'
    - TSP path:     'path'
    - Bitonic TSP:  'bito'
Graphs with minor_id include:
    - 1-NNG:          '1nng'          - Gabriel:        'gab'   
    - 2-NNG:          '2nng'          - Urquhart:       'urq'
    - 20%-NNG:        '20pt'          - Delaunay:       'del'
    - MST:            'mst'           - Bitonic TSP:    'bito'
    - Order-1 Del.:   '1del'          - Order-2 Del.:   '2del'
A graph having major_id means that other graphs are being
compared against it.
"""

def compare(d, comp, g1, g2, div):
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
    print('Working on comparison: ' + comp)
    n = len(g1)
    d[comp] = [num_common_edges(g1[i], g2[i])/div for i in range(n)]
    print('Finished comparison: ' + comp)

def simulate(minpts, maxpts, interval, numrunsper, batch, randtype, which_comps):
    """
    Main simulation function.
        minpts, maxpts, interval:
            integers delimiting sizes of point clouds to simulate
        numrunsper:
            number of point clouds to simulate for each point cloud size
        batch:
            number of point clouds to work on concurrently
        randtype:
            string indicating point cloud type (defined in point_distributions.py)
        which_comps:
            dictionary specifying the exact set of comparisons to be made
    """
    start_time = time.time()
    
    # gather comparison specifications from user
    comparisons = ['_'.join([major_id, minor_id]) for major_id in which_comps for minor_id in which_comps[major_id]]
    allgraphfuncs = {'1nng':functools.partial(get_knng_graph, k=1, metric=2),
                     '2nng':functools.partial(get_knng_graph, k=2, metric=2),
                     '20pt':functools.partial(get_pctnng_graph, pct=0.20, metric=2),
                     'mst':get_mst_graph,
                     'gab':get_gabriel_graph,
                     'urq':get_urquhart_graph,
                     'del':get_delaunay_tri_graph,
                     '1del':functools.partial(get_kdelaunay_graph, order=1),
                     '2del':functools.partial(get_kdelaunay_graph, order=2),
                     'bito':get_bitonic_tour,
                     'path':functools.partial(get_tsp_graph, mode='path', metric='2'),
                     'tour':functools.partial(get_tsp_graph, mode='tour', metric='2')}
    graphs_to_compute = set(which_comps.keys()) | set(graphid for v in which_comps.values() for graphid in v)

    # create directory to output results
    dirnames = {'pts_uni':'uniform-sqr',
                'pts_annulus':'annulus',
                'pts_annulus_random':'annulus-rand',
                'pts_ball':'uniform-ball',
                'pts_clusnorm':'normal-clust',
                'pts_cubediam':'uniform-diam',
                'pts_corners':'corners',
                'pts_grid':'uniform-grid',
                'pts_normal':'normal-bivar',
                'pts_spokes':'spokes',
                'pts_concentric_circular_points':'concen-circ'}
    dirname = dirnames[randtype] + "-results"
    cwd = os.getcwd()
    randdir = os.path.join(cwd, "results/" + dirname)
    if not os.path.isdir(randdir):
        os.makedirs(randdir)

    # determine the batch sizes that will be computed
    numruns, rem = divmod(numrunsper, batch)
    batchnums = numruns*[batch] + [rem] if rem != 0 else numruns*[batch]
    
    for numpts in range(minpts,maxpts,interval):
        s = time.time()
        for idx, num_in_batch in enumerate(batchnums):

            # update meta.txt to reflect new batch
            with open(randdir + '/meta.txt', 'w') as f:
                runcount = sum(batchnums[:idx])
                metadata = {'minpts-latest-run':minpts, 'maxpts-latest-run':maxpts,
                            'interval-latest-run':interval, 'batch-latest-run':batch,
                            'numrunsper-latest-run':numrunsper,
                            'numpts-latest':numpts, 'runcnt-latest':runcount}
                f.write(str(metadata))
            
            # generate num_in_batch point clouds of type randtype
            # note it is crucial that the point clouds are sorted lexicographically
            pts = [sorted(globals()[randtype](numpts), key=lambda k: [k[0], k[1]]) for _ in range(num_in_batch)]
            graphfuncs = {graphid:func for graphid, func in allgraphfuncs.items() if graphid in graphs_to_compute}
            graphs = {}
            for name, func in graphfuncs.items():
                rets = [] # will contain dictionaries of the form {iteration:graph} (as in graphfuncs.py)
                queue = Queue() # will schedule computation of graphs
                procs = []
                for iteration in range(num_in_batch):
                    proc = Process(target=functools.partial(func, points=pts[iteration], q=queue, iteration=iteration))
                    procs.append(proc)
                    proc.start()
                for proc in procs:
                    ret = queue.get()
                    rets.append(ret)
                for proc in procs:
                    proc.join()
                # unpack results and store graphs in graphs dict
                samples = {iteration:graph for d in rets for iteration, graph in d.items()}
                graphs[name] = samples
            print("done computing graphs")

            # organize specifications for graph comparisons
            comp_details = {}
            for major_id in which_comps:
                div = numpts if major_id in ['tour', 'bito'] else numpts-1
                for minor_id in which_comps[major_id]:
                    comp_details['_'.join([major_id, minor_id])] = [graphs[minor_id], graphs[major_id], div]
            manager = Manager()
            new_fracs = manager.dict()
            procs = []
            # make all graph comparisons in parallel
            for comp in comp_details:
                proc = Process(target=functools.partial(compare, d=new_fracs, comp=comp, g1=comp_details[comp][0],
                                                        g2=comp_details[comp][1], div=comp_details[comp][2]))
                procs.append(proc)
                proc.start()
            for proc in procs:
                proc.join()
            
            # update data.txt with new comparison data
            if os.path.exists(randdir + "/data.txt"):
                with open(randdir + "/data.txt", "r+") as f:
                    data = eval(f.read())
                    for comp in comparisons:
                        if numpts not in data[comp]:
                            data[comp][numpts] = []
                        data[comp][numpts] += new_fracs[comp]
                    f.seek(0)
                    f.write(str(data))
                    f.truncate()
            else:
                with open(randdir + "/data.txt", 'w') as f:
                    f.write(str({comp:{numpts:new_fracs[comp]} for comp in comparisons}))
            print("done updating data file")

        # update compute-times.txt
        time_for_numpts = time.time()-s
        with open(randdir + '/compute-times.txt', 'a+') as f:
            f.write('Numpts: ' + str(numpts) + ',\tCompute time: ' + str(round(time_for_numpts, 3)) + ' secs\t\t= ' + \
                    str(round(time_for_numpts/60, 3)) + ' mins\t\t= ' + str(round(time_for_numpts/3600, 3)) + ' hours\n')

    # remove tour-wds and path-wds directories, which were created by get_tsp_graph
    cwd = os.getcwd()
    if os.path.isdir(os.path.join(cwd, "tour-wds/")):
        try:
            for item in os.listdir(os.path.join(cwd, "tour-wds/")):
                os.rmdir(os.path.join(cwd, "tour-wds/" + item))
            os.rmdir(os.path.join(cwd, "tour-wds/"))
        except:
            pass
    if os.path.isdir(os.path.join(cwd, "path-wds/")):
        try:
            for item in os.listdir(os.path.join(cwd, "path-wds/")):
                os.rmdir(os.path.join(cwd, "path-wds/" + item))
            os.rmdir(os.path.join(cwd, "path-wds/"))
        except:
            pass

    print("Total time in seconds: " + str(time.time() - start_time))

parser = argparse.ArgumentParser()
parser.add_argument('--minpts', type=int, required=True)
parser.add_argument('--maxpts', type=int, required=True)
parser.add_argument('--interval', type=int, required=True)
parser.add_argument('--numrunsper', type=int, required=True)
parser.add_argument('--batch', type=int, required=True)
parser.add_argument('--randtype', type=str, required=True)
args = parser.parse_args()
minpts     = args.minpts
maxpts     = args.maxpts
interval   = args.interval
batch      = args.batch
numrunsper = args.numrunsper
randtype   = args.randtype

all_comps = {'tour':['1nng', '2nng', '20pt', 'mst', 'gab', 'urq', 'del', '1del', '2del', 'bito', 'path'],
             'path':['1nng', '2nng', '20pt', 'mst', 'gab', 'urq', 'del', '1del', '2del'],
             'bito':['1nng', '2nng', '20pt', 'mst', 'gab', 'urq', 'del', '1del', '2del']}
which_comps = {'tour':['1nng', '2nng', '20pt', 'mst', 'gab', 'urq', 'del', '1del', '2del', 'path'],
               'path':['1nng', '2nng', '20pt', 'mst', 'gab', 'urq', 'del', '1del', '2del']}
simulate(minpts=minpts, maxpts=maxpts, interval=interval, numrunsper=numrunsper,
         batch=batch, randtype=randtype, which_comps=all_comps)
