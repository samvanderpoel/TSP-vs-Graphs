import functools
from multiprocessing import Process, Queue, Manager
import numpy as np
import networkx as nx

import argparse
import os # for get_tsp_path
import time

from graphfuncs import *
from utilfuncs import *
from point_distributions import *

def compare(d, comp, g1, g2, div, num_in_batch):
    print('Working on comparison: ' + comp)
    d[comp] = [num_common_edges(g1[i], g2[i])/div for i in range(num_in_batch)]
    print('Finished comparison: ' + comp)

def simulate_all(minpts, maxpts, interval, batch, numrunsper, randtype, which_comps):

    start_time = time.time()
    
    comparisons = ['_'.join([major_id, minor_id]) for major_id in which_comps for minor_id in which_comps[major_id]]
    allgraphfuncs = {'1nng':functools.partial(get_knng_graph, k=1, metric=2),
                     '2nng':functools.partial(get_knng_graph, k=2, metric=2),
                     '20pt':functools.partial(get_pctnng_graph, pct=0.20, metric=2),
                     'mst':get_mst_graph,
                     'gab':get_gabriel_graph,
                     'urq':get_urquhart_graph,
                     'del':get_delaunay_tri_graph,
                     'bito':get_bitonic_tour,
                     'path':functools.partial(get_tsp_graph, mode='path', metric='2'),
                     'tour':functools.partial(get_tsp_graph, mode='tour', metric='2')}
    graphs_to_compute = set(which_comps.keys()) | set(graphid for v in which_comps.values() for graphid in v)

    cwd = os.getcwd()
    randdir = os.path.join(cwd, randtype + '-results')
    if not os.path.isdir(randdir):
        os.makedirs(randdir)

    numruns, rem = divmod(numrunsper, batch)
    batchnums = numruns*[batch] + [rem] if rem != 0 else numruns*[batch]
    
    for numpts in range(minpts,maxpts,interval):
        s = time.time()
        for idx, num_in_batch in enumerate(batchnums):
            with open(randtype + '-results/' + 'meta.txt', 'w') as f:
                runcount = sum(batchnums[:idx])
                metadata = {'minpts-latest-run':minpts, 'maxpts-latest-run':maxpts,
                            'interval-latest-run':interval, 'batch-latest-run':batch,
                            'numrunsper-latest-run':numrunsper,
                            'numpts-latest':numpts, 'runcnt-latest':runcount}
                f.write(str(metadata))
            
            # SUPPLY RANDTYPE AS STRING THAT MATCHES SAMPLING FUNCTION NAMES 
            pts = [sorted(globals()[randtype](numpts), key=lambda k: [k[0], k[1]]) for _ in range(num_in_batch)]
            graphfuncs = {graphid:func for graphid, func in allgraphfuncs.items() if graphid in graphs_to_compute}
            graphs = {}
            for name, func in graphfuncs.items():
                rets = []
                queue = Queue()
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
                samples = {iteration:graph for d in rets for iteration, graph in d.items()}
                graphs[name] = samples
            print("done computing graphs")

            comp_details = {}
            for major_id in which_comps:
                for minor_id in which_comps[major_id]:
                    div = numpts if major_id in ['tour', 'bito'] else numpts-1
                    comp_details['_'.join([major_id, minor_id])] = [graphs[minor_id], graphs[major_id], div]
            manager = Manager()
            new_fracs = manager.dict()
            procs = []
            for comp in comp_details:
                proc = Process(target=functools.partial(compare, d=new_fracs, comp=comp, g1=comp_details[comp][0],
                                                        g2=comp_details[comp][1], div=comp_details[comp][2],
                                                        num_in_batch=num_in_batch))
                procs.append(proc)
                proc.start()
            for proc in procs:
                proc.join()
            
            if os.path.exists(randtype + '-results/data.txt'):
                with open(randtype + '-results/data.txt', "r+") as f:
                    data = eval(f.read())
                    for comp in comparisons:
                        if numpts not in data[comp]:
                            data[comp][numpts] = []
                        data[comp][numpts] += new_fracs[comp]
                    f.seek(0)
                    f.write(str(data))
                    f.truncate()
            else:
                with open(randtype + '-results/data.txt', 'w') as f:
                    f.write(str({comp:{numpts:new_fracs[comp]} for comp in comparisons}))
            print("done updating data file")

            # delete all items in cwd that are not .py, .sh, .slurm, .txt, or directory
            cwd = os.getcwd()
            contents = os.listdir(cwd)
            for item in contents:
                if not item.endswith(".py") and not item.endswith(".sh") and \
                   not item.endswith(".slurm") and not item.endswith(".txt") and \
                   not os.path.isdir(os.path.join(cwd, item)):
                    os.remove(os.path.join(cwd, item))
        time_for_numpts = time.time()-s
        with open(randtype + '-results/compute-times.txt', 'a+') as f:
            f.write('Numpts: ' + str(numpts) + ',\tCompute time: ' + str(round(time_for_numpts, 3)) + ' secs\t\t= ' + \
                    str(round(time_for_numpts/60, 3)) + ' mins\t\t= ' + str(round(time_for_numpts/3600, 3)) + ' hours\n')

    cwd = os.getcwd()
    if os.path.isdir(os.path.join(cwd, "tour-wds/")):
        for item in os.listdir(os.path.join(cwd, "tour-wds/")):
            os.rmdir(os.path.join(cwd, "tour-wds/" + item))
        os.rmdir(os.path.join(cwd, "tour-wds/"))
    if os.path.isdir(os.path.join(cwd, "path-wds/")):
        for item in os.listdir(os.path.join(cwd, "path-wds/")):
            os.rmdir(os.path.join(cwd, "path-wds/" + item))
        os.rmdir(os.path.join(cwd, "path-wds/"))

    print("Total time in seconds: " + str(time.time() - start_time))

parser = argparse.ArgumentParser()
parser.add_argument('--minpts', type=int, required=True)
parser.add_argument('--maxpts', type=int, required=True)
parser.add_argument('--interval', type=int, required=True)
parser.add_argument('--batch', type=int, required=True)
parser.add_argument('--numrunsper', type=int, required=True)
parser.add_argument('--randtype', type=str, required=True)
minpts     = parser.parse_args().minpts
maxpts     = parser.parse_args().maxpts
interval   = parser.parse_args().interval
batch      = parser.parse_args().batch
numrunsper = parser.parse_args().numrunsper
randtype   = parser.parse_args().randtype

all_comps = {'tour':['1nng', '2nng', '20pt', 'mst', 'gab', 'urq', 'del', 'bito', 'path'],
             'path':['1nng', '2nng', '20pt', 'mst', 'gab', 'urq', 'del'],
             'bito':['1nng', '2nng', '20pt', 'mst', 'gab', 'urq', 'del']}
which_comps = {'tour':['1nng', '2nng', '20pt', 'mst', 'gab', 'urq', 'del', 'path'],
               'path':['1nng', '2nng', '20pt', 'mst', 'gab', 'urq', 'del']}
simulate_all(minpts=minpts, maxpts=maxpts, interval=interval, batch=batch,
             numrunsper=numrunsper, randtype=randtype, which_comps=all_comps)
