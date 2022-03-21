import functools
from multiprocessing import Manager, Process, Queue
import numpy as np
import networkx as nx
import argparse
import os
import re
import time

from cloud_funcs import *
from graph_funcs import *
from utils import *


class Simulation:

    def __init__(
        self,
        jobname,
        minpts,
        maxpts,
        interval,
        numrunsper,
        batch,
        cloudtype,
        which_comps,
        anomalies={}
    ):
        self.jobname = jobname
        self.minpts = minpts
        self.maxpts = maxpts
        self.interval = interval
        self.numrunsper = numrunsper
        self.batch = batch
        self.cloudtype = cloudtype
        self.which_comps = which_comps
        self.anomalies = anomalies

        self.config_cloud_func()
        self.config_graph_funcs()

    def config_cloud_func(self):
        cloudfuncs = {
            'uniform-sqr':'pts_uni',
            'annulus':'pts_annulus',
            'annulus-rand':'pts_annulus_random',
            'uniform-ball':'pts_ball',
            'normal-clust':'pts_clusnorm',
            'uniform-diam':'pts_cubediam',
            'corners':'pts_corners',
            'uniform-grid':'pts_grid',
            'normal-bivar':'pts_normal',
            'spokes':'pts_spokes',
            'concen-circ':'pts_concentric_circular_points'
        }
        self.cloudfuncname = cloudfuncs[self.cloudtype]
        dirname = self.cloudtype + "-results"
        cwd = os.getcwd()
        self.clouddir = os.path.join(
            cwd,
            "results",
            self.jobname,
            dirname
        )
        if not os.path.isdir(self.clouddir):
            os.makedirs(self.clouddir)

    def config_graph_funcs(self):
        self.comparisons = [
            '_'.join([major_id, minor_id])
            for major_id in self.which_comps
            for minor_id in self.which_comps[major_id]
        ]
        self.graphs_to_compute = (
            set(self.which_comps.keys()) |
            set(
                graphid
                for v in self.which_comps.values()
                for graphid in v
            )
        )
        kdelaunay_funcs = {
            g:functools.partial(
                get_kdelaunay_graph,
                order=int(g[:-3])
            )
            for g in self.graphs_to_compute
            if re.match("[0-9]+del", g)
        }
        knng_funcs = {
            g:functools.partial(get_nng_graph, k=int(g[:-3]), metric=2)
            for g in self.graphs_to_compute
            if re.match("[0-9]+nng", g)
        }
        standard_funcs = {
            '20pt':functools.partial(get_nng_graph, pct=0.20, metric=2),
            'mst':get_mst_graph,
            'gab':get_gabriel_graph,
            'urq':get_urquhart_graph,
            'dmg':functools.partial(
                minus_func,
                d1=dict(func=get_delaunay_tri_graph),
                d2=dict(func=get_gabriel_graph)
            ),
            'del':get_delaunay_tri_graph,
            'bito':get_bitonic_tour,
            'path':functools.partial(
                get_tsp_graph,
                mode='path',
                dirname=os.path.join(self.jobname, self.cloudtype),
                metric='2'
            ),
            'tour':functools.partial(
                get_tsp_graph,
                mode='tour',
                dirname=os.path.join(self.jobname, self.cloudtype),
                metric='2'
            )
        }
        self.graph_funcs = {
            **kdelaunay_funcs,
            **knng_funcs, 
            **standard_funcs
        }

    def simulate_batch(
        self,
        numpts,
        num_in_batch,
        batch_nums,
        idx
    ):
        # update meta.txt to reflect new batch
        with open(self.clouddir + '/meta.txt', 'w') as f:
            runcount = sum(batch_nums[:idx])
            metadata = [
                f'minpts-latest-run: {self.minpts}\n',
                f'maxpts-latest-run: {self.maxpts}\n',
                f'interval-latest-run: {self.interval}\n',
                f'batch-latest-run: {self.batch}\n',
                f'numrunsper-latest-run: {self.numrunsper}\n',
                f'numpts-latest: {numpts}\n',
                f'runcnt-latest: {runcount}'
            ]
            f.writelines(metadata)
        
        # generate num_in_batch point clouds, lex-sorted
        pts = [
            sorted(
                globals()[self.cloudfuncname](numpts),
                key=lambda k: [k[0], k[1]]
            )
            for _ in range(num_in_batch)
        ]
        funcs = {
            graphid:func
            for graphid, func in self.graph_funcs.items()
            if graphid in self.graphs_to_compute
        }
        graphs = {}
        for name, func in funcs.items():
            rets = [] # will contain dicts of form {iteration:graph}
            queue = Queue() # will schedule computation of graphs
            procs = []
            for iteration in range(num_in_batch):
                task = functools.partial(
                    func,
                    points=pts[iteration],
                    q=queue,
                    iteration=iteration
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
                iteration:graph
                for d in rets
                for iteration, graph in d.items()
            }
            graphs[name] = samples
        print(
            f"Done computing graphs for NUMPTS {numpts}, " +
            f"BATCH NO. {idx}"
        )

        # organize specifications for graph comparisons
        comp_details = {}
        for major_id in self.which_comps:
            for minor_id in self.which_comps[major_id]:
                spec = [graphs[major_id], graphs[minor_id]]
                comp_details['_'.join([major_id, minor_id])] = spec
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
                anomalies=self.anomalies,
                dirname=self.clouddir
            )
            proc = Process(target=task)
            procs.append(proc)
            proc.start()
            proc.join()
        
        # update data.txt with new comparison data
        data_dir = os.path.join(self.clouddir, "data.txt")
        if os.path.exists(data_dir):
            with open(data_dir, "r+") as f:
                data = eval(f.read())
                for comp in self.comparisons:
                    if numpts not in data[comp]:
                        data[comp][numpts] = []
                    data[comp][numpts] += new_fracs[comp]
                f.seek(0)
                f.write(str(data))
                f.truncate()
        else:
            with open(data_dir, "w") as f:
                f.write(
                    str({
                            comp:{numpts:new_fracs[comp]}
                            for comp in self.comparisons
                    })
                )
        print(
            f"Done updating data file for NUMPTS {numpts}, " +
            f"BATCH NO. {idx}"
        )

    def simulate(self):
        start_time = time.time()

        # batch sizes to be computed
        numruns, rem = divmod(self.numrunsper, self.batch)
        batch_nums = numruns*[self.batch] + [rem] \
            if rem != 0 else numruns*[self.batch]
        
        div, rem = divmod(self.maxpts - self.minpts, self.interval)
        all_numpts = [
            self.minpts + k*self.interval for k in range(int(div)+1)
        ]
        for numpts in all_numpts:
            s = time.time()

            for idx, num_in_batch in enumerate(batch_nums):
                self.simulate_batch(numpts, num_in_batch, batch_nums, idx)

            # update compute-times.txt
            time_for_numpts = time.time() - s
            with open(
                os.path.join(self.clouddir, "compute-times.txt"), 'a+'
            ) as f:
                f.write(
                    f"Numpts: {numpts},\tCompute time: "
                    + f"{round(time_for_numpts, 3)} secs\t\t= "
                    + f"{round(time_for_numpts/60, 3)} mins\t\t= "
                    + f"{round(time_for_numpts/3600, 3)} hours\n"
                )

        self.cleanup_dirs()
        print(f"Total time in seconds: {time.time() - start_time}")

    def cleanup_dirs(self):
        # remove tour-wds and path-wds directories that were
        # created by get_tsp_graph
        tourwd = os.path.join("tour-wds", f"tour-wds-{self.cloudtype}")
        pathwd = os.path.join("path-wds", f"path-wds-{self.cloudtype}")
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
