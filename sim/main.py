import functools
from multiprocessing import Process, Queue, Manager
import numpy as np
import networkx as nx
import argparse
import os
import re
import time

from cloud_funcs import *
from graph_funcs import *
from utils import *

"""
Graphs are classified with a major_id or minor_id.
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


def simulate(
    jobname,
    minpts,
    maxpts,
    interval,
    numrunsper,
    batch,
    cloudtype,
    which_comps,
    anomalies={},
):
    """
    Main simulation function.
        jobname:
            name of the current simulation job
        minpts, maxpts, interval:
            integers delimiting sizes of point clouds to simulate
        numrunsper:
            number of point clouds to simulate for each point cloud size
        batch:
            number of point clouds to work on concurrently
        cloudtype:
            string indicating point cloud type (defined in cloud_funcs.py)
        which_comps:
            dictionary specifying the exact set of comparisons to be made
        anomalies:
            dictionary of the form {comparison:fraction} of comparisons for which
            point clouds should be recorded if intersection is less than a user-
            specified fraction
    """
    start_time = time.time()

    # create directory to output results
    cloudfuncs = {
        "uniform-sqr": "pts_uni",
        "annulus": "pts_annulus",
        "annulus-rand": "pts_annulus_random",
        "uniform-ball": "pts_ball",
        "normal-clust": "pts_clusnorm",
        "uniform-diam": "pts_cubediam",
        "corners": "pts_corners",
        "uniform-grid": "pts_grid",
        "normal-bivar": "pts_normal",
        "spokes": "pts_spokes",
        "concen-circ": "pts_concentric_circular_points",
    }
    cloudfuncname = cloudfuncs[cloudtype]
    dirname = cloudtype + "-results"
    cwd = os.getcwd()
    clouddir = os.path.join(cwd, "results", jobname, dirname)
    if not os.path.isdir(clouddir):
        os.makedirs(clouddir)

    # gather comparison specifications from user
    comparisons = [
        "_".join([major_id, minor_id])
        for major_id in which_comps
        for minor_id in which_comps[major_id]
    ]
    graphs_to_compute = set(which_comps.keys()) | set(
        graphid for v in which_comps.values() for graphid in v
    )
    kdelafuncs = {
        g: functools.partial(get_kdelaunay_graph, order=int(g[:-3]))
        for g in graphs_to_compute
        if re.match("[0-9]+del", g)
    }
    knngsfuncs = {
        g: functools.partial(get_nng_graph, k=int(g[:-3]), metric=2)
        for g in graphs_to_compute
        if re.match("[0-9]+nng", g)
    }
    graphfuncs = {
        "20pt": functools.partial(get_nng_graph, pct=0.20, metric=2),
        "mst": get_mst_graph,
        "gab": get_gabriel_graph,
        "urq": get_urquhart_graph,
        "dmg": functools.partial(
            minus_func,
            d1=dict(func=get_delaunay_tri_graph),
            d2=dict(func=get_gabriel_graph),
        ),
        "del": get_delaunay_tri_graph,
        "bito": get_bitonic_tour,
        "path": functools.partial(
            get_tsp_graph, mode="path", dirname=jobname + "/" + cloudtype, metric="2"
        ),
        "tour": functools.partial(
            get_tsp_graph, mode="tour", dirname=jobname + "/" + cloudtype, metric="2"
        ),
    }
    allgraphfuncs = {**kdelafuncs, **knngsfuncs, **graphfuncs}

    # determine the batch sizes that will be computed
    numruns, rem = divmod(numrunsper, batch)
    batchnums = numruns * [batch] + [rem] if rem != 0 else numruns * [batch]

    div, rem = divmod(maxpts - minpts, interval)
    all_numpts = [minpts + k * interval for k in range(int(div) + 1)]
    for numpts in all_numpts:
        s = time.time()
        for idx, num_in_batch in enumerate(batchnums):

            # update meta.txt to reflect new batch
            with open(clouddir + "/meta.txt", "w") as f:
                runcount = sum(batchnums[:idx])
                metadata = {
                    "minpts-latest-run": minpts,
                    "maxpts-latest-run": maxpts,
                    "interval-latest-run": interval,
                    "batch-latest-run": batch,
                    "numrunsper-latest-run": numrunsper,
                    "numpts-latest": numpts,
                    "runcnt-latest": runcount,
                }
                f.write(str(metadata))

            # generate num_in_batch point clouds of type cloudtype
            # note it is crucial that the points in each point cloud be sorted
            # lexicographically
            pts = [
                sorted(globals()[cloudfuncname](numpts), key=lambda k: [k[0], k[1]])
                for _ in range(num_in_batch)
            ]
            graphfuncs = {
                graphid: func
                for graphid, func in allgraphfuncs.items()
                if graphid in graphs_to_compute
            }
            graphs = {}
            for name, func in graphfuncs.items():
                rets = []  # will contain dictionaries of the form {iteration:graph}
                queue = Queue()  # will schedule computation of graphs
                procs = []
                for iteration in range(num_in_batch):
                    task = functools.partial(
                        func, points=pts[iteration], q=queue, iteration=iteration
                    )
                    proc = Process(target=task)
                    procs.append(proc)
                    proc.start()
                for proc in procs:
                    ret = queue.get()
                    rets.append(ret)
                for proc in procs:
                    proc.join()
                # unpack results and store graphs in graphs dict
                samples = {
                    iteration: graph for d in rets for iteration, graph in d.items()
                }
                graphs[name] = samples
            print(
                "Done computing graphs for NUMPTS "
                + str(numpts)
                + ", BATCH NO. "
                + str(idx)
            )

            # organize specifications for graph comparisons
            comp_details = {}
            for major_id in which_comps:
                for minor_id in which_comps[major_id]:
                    spec = [graphs[major_id], graphs[minor_id]]
                    comp_details["_".join([major_id, minor_id])] = spec
            manager = Manager()
            new_fracs = manager.dict()
            procs = []
            # make all graph comparisons in parallel
            for comp in comp_details:
                task = functools.partial(
                    compare,
                    d=new_fracs,
                    comp=comp,
                    g1=comp_details[comp][0],
                    g2=comp_details[comp][1],
                    anomalies=anomalies,
                    dirname=clouddir,
                )
                proc = Process(target=task)
                procs.append(proc)
                proc.start()
            for proc in procs:
                proc.join()

            # update data.txt with new comparison data
            if os.path.exists(clouddir + "/data.txt"):
                with open(clouddir + "/data.txt", "r+") as f:
                    data = eval(f.read())
                    for comp in comparisons:
                        if numpts not in data[comp]:
                            data[comp][numpts] = []
                        data[comp][numpts] += new_fracs[comp]
                    f.seek(0)
                    f.write(str(data))
                    f.truncate()
            else:
                with open(clouddir + "/data.txt", "w") as f:
                    f.write(
                        str({comp: {numpts: new_fracs[comp]} for comp in comparisons})
                    )
            print(
                "Done updating data file for NUMPTS "
                + str(numpts)
                + ", BATCH NO. "
                + str(idx)
            )

        # update compute-times.txt
        time_for_numpts = time.time() - s
        with open(clouddir + "/compute-times.txt", "a+") as f:
            f.write(
                "Numpts: "
                + str(numpts)
                + ",\tCompute time: "
                + str(round(time_for_numpts, 3))
                + " secs\t\t= "
                + str(round(time_for_numpts / 60, 3))
                + " mins\t\t= "
                + str(round(time_for_numpts / 3600, 3))
                + " hours\n"
            )

    # remove tour-wds and path-wds directories, which were created by get_tsp_graph
    tourwd = "tour-wds/" + "tour-wds-" + cloudtype + "/"
    pathwd = "path-wds/" + "path-wds-" + cloudtype + "/"
    cwd = os.getcwd()
    if os.path.isdir(os.path.join(cwd, tourwd)):
        for item in os.listdir(os.path.join(cwd, tourwd)):
            try:
                os.rmdir(os.path.join(cwd, tourwd + item))
            except:
                pass
        try:
            os.rmdir(os.path.join(cwd, tourwd))
        except:
            pass
    if os.path.isdir(os.path.join(cwd, pathwd)):
        for item in os.listdir(os.path.join(cwd, pathwd)):
            try:
                os.rmdir(os.path.join(cwd, pathwd + item))
            except:
                pass
        try:
            os.rmdir(os.path.join(cwd, pathwd))
        except:
            pass

    print("Total time in seconds: " + str(time.time() - start_time))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobname", type=str, required=True)
    parser.add_argument("--minpts", type=int, required=True)
    parser.add_argument("--maxpts", type=int, required=True)
    parser.add_argument("--interval", type=int, required=True)
    parser.add_argument("--numrunsper", type=int, required=True)
    parser.add_argument("--batch", type=int, required=True)
    parser.add_argument("--cloudtype", type=str, required=True)
    parser.add_argument("--comps", type=str, required=True)
    parser.add_argument("--anoms", type=str, required=True)
    args = parser.parse_args()
    jobname = args.jobname
    minpts = args.minpts
    maxpts = args.maxpts
    interval = args.interval
    batch = args.batch
    numrunsper = args.numrunsper
    cloudtype = args.cloudtype
    comps = eval(args.comps)
    anoms = eval(args.anoms)

    simulate(
        jobname=jobname,
        minpts=minpts,
        maxpts=maxpts,
        interval=interval,
        numrunsper=numrunsper,
        batch=batch,
        cloudtype=cloudtype,
        which_comps=comps,
        anomalies=anoms,
    )
