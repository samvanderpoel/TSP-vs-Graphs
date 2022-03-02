import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
import re
import yaml

plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'cm'


def read_simul_data(
    cloudtype,
    clouddir,
    which_comps='all',
    subdir='',
    min_pts=0,
    max_pts=1000000,
    bands=True
):
    data = eval(open(clouddir + '/data.txt', 'r').read())
    # meta = eval(open(cloudtype + '-results/meta.txt', 'r').read())

    if which_comps=='all':
        which_comps = {}
        for comp in data:
            major_id, minor_id = comp.split('_')
            if major_id not in which_comps:
                which_comps[major_id] = []
            which_comps[major_id] += [minor_id]
    else:
        all_comps = [
            '_'.join([major_id, minor_id])
            for major_id in which_comps
            for minor_id in which_comps[major_id]
        ]
        for comp in all_comps:
            if comp not in data:
                raise ValueError(
                    f"Comparison not found in logged data: {comp}"
                )

    graphs_to_compute = (
        set(which_comps.keys()) |
        set(graphid for v in which_comps.values() for graphid in v)
    )
    kdels = sorted(
        g
        for g in graphs_to_compute
        if re.match("[0-9]+del", g)
    )
    knngs = sorted(
        g
        for g in graphs_to_compute
        if re.match("[0-9]+nng", g)
    )
    kdels_cols = [
        (0/255,64/255,255/255),
        (0/255,149/255,255/255),
        (79/255,143/255,35/255),
        (143/255,106/255,35/255)
    ]
    knngs_cols = [
        (170/255,0/255,255/255),
        (255/255,0/255,255/255),
        (143/255,35/255,35/255),
        (107/255,35/255,143/255)
    ]
    kdels_plotcols = {g:kdels_cols[i%4] for i, g in enumerate(kdels)}
    knngs_plotcols = {g:knngs_cols[i%4] for i, g in enumerate(knngs)}

    plotsdir = os.path.join(clouddir, 'plots', subdir)
    if not os.path.isdir(plotsdir):
        os.makedirs(plotsdir)

    tempcols = {
        'tour':(120/255,120/255,100/255),
        'path':(255/255,0/255,0/255),
        'bito':(255/255,127/255,0/255),
        'gab':(255/255,212/255,0/255),
        'urq':(0/255,0/255,0/255),
        'mst':(106/255,255/255,0/255),
        'del':(0/255,234/255,255/255),
        'dmg':(255/255,60/255,60/255),
        '20pt':(35/255,98/255,143/255)
    }
    colors = {**tempcols, **kdels_plotcols, **knngs_plotcols}
    titles = {
        'tour':'TSP Tour',
        'path':'TSP Path',
        'bito':'Bitonic TSP Tour',
        'dmg':'Delaunay \\ Gabriel',
        '1nng':'Nearest Neighbor Graph'
    }
    kdels_labs = {
        g:' '.join(['Order-'+str(g[:-3]), 'Delaunay'])
        for g in graphs_to_compute
        if re.match("[0-9]+del", g)
    }
    knngs_labs = {
        g:''.join([str(g[:-3]), '-NNG'])
        for g in graphs_to_compute
        if re.match("[0-9]+nng", g)
    }
    templabs = {
        'del':'Delaunay',
        '1del':'Order-1 Delaunay',
        '2del':'Order-2 Delaunay',
        'gab':'Gabriel', 'tour':'TSP Tour',
        'path':'TSP Path',
        '1nng':'1-NNG',
        '2nng':'2-NNG',
        '20pt':'20\% NNG',
        'urq':'Urquhart',
        'mst':'MST',
        'dmg':'Delaunay \\ Gabriel',
        'bito':'Bitonic TSP'
    }
    labels = {**templabs, **kdels_labs, **knngs_labs}
    sample = {
        'uniform-sqr':'Uniform on Unit Square',
        'annulus':'Non-Random on Annulus',
        'annulus-rand': 'Uniform on Annulus',
        'uniform-ball':'Uniform on a Disk',
        'normal-clust':'Clusters of Normal Distributions',
        'uniform-diam':'Uniform on Unit Diagonal',
        'corners':'Uniform on Vertices of a Regular Polygon',
        'uniform-grid':'Uniform on Grid',
        'normal-bivar':'Bivariate Normal',
        'spokes':'Random Spokes',
        'concen-circ':'Concentric Circular Points'
    }
    for major_id in which_comps:
        all_comps = [
            '_'.join([major_id, minor_id])
            for minor_id in which_comps[major_id]
        ]
        fig, ax = plt.subplots(dpi=500)
        ax.set_title(
            f"Comparison of edges in {titles[major_id]} and " +
            f"Proximity Graphs\nSampling Type: {sample[cloudtype]}",
            fontdict={'fontsize':12}
        )
        all_numpts = [
            num
            for comp in all_comps
            for num in data[comp].keys()
        ]
        min_pts = max(min_pts, min(all_numpts))
        max_pts = min(max_pts, max(all_numpts))
        # ax.set_xlim([min_pts-10, max_pts+10])
        # ax.set_ylim([0,1.1])
        ax.set_xlabel("Point set size")
        ax.set_ylabel(f"Fraction of {titles[major_id]} Edges in Graph")
        for comp in all_comps:
            major_id, minor_id = comp.split('_')
            xvals = sorted(
                val
                for val in data[comp]
                if min_pts <= val <= max_pts
            )
            comp_means = np.asarray([
                np.mean(data[comp][key])
                for key in xvals
            ])
            comp_stdvs = np.asarray([
                np.std(data[comp][key])
                for key in xvals
            ])
            ax.plot(
                xvals,
                comp_means,
                'o-',
                markersize=3,
                label=labels[minor_id],
                color=colors[minor_id]
            )
            if bands:
                ax.fill_between(
                    xvals,
                    np.clip(comp_means-comp_stdvs, 0, 1),
                    np.clip(comp_means+comp_stdvs, 0, 1),
                    color=colors[minor_id],
                    alpha=0.3
                )
        ax.legend(
            bbox_to_anchor=(1.05, 1),
            loc='upper left',
            title='Graphs',
            fancybox=True
        )
        ax.grid(color='gray', linestyle='--', linewidth=0.5)
        fig.savefig(
            os.path.join(
                plotsdir,
                cloudtype + '_' + major_id + '_vs_graphs.pdf'
            ),
            format='pdf',
            bbox_inches='tight',
            dpi=500
        )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--cloudtype', type=str, required=True)
    config = parser.parse_args().config
    cloudtype = parser.parse_args().cloudtype

    with open(config, "r") as stream:
        try:
            args = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    jobname = args['jobname']
    comps = args['comps']
    subdir = args['subdir']
    min_pts = args['min_pts']
    max_pts = args['max_pts']
    bands = args['bands']

    dirname = cloudtype + "-results"
    cwd = os.getcwd()
    clouddir = os.path.join(cwd, "results", jobname, dirname)
    read_simul_data(
        cloudtype,
        clouddir,
        which_comps=comps,
        subdir=subdir,
        min_pts=min_pts,
        max_pts=max_pts,
        bands=bands
    )
