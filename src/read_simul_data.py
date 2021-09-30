import argparse
import numpy as np
import matplotlib.pyplot as plt
import os

parser = argparse.ArgumentParser()
parser.add_argument('--randtype', type=str, required=True)
randtype = parser.parse_args().randtype

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

def read_simul_data(randtype, which_comps='all'):

    data = eval(open(randdir + '/data.txt', 'r').read())
    # metadata = eval(open(randtype + '-results/meta.txt', 'r').read())

    if which_comps=='all':
        which_comps = {}
        for comp in data:
            major_id, minor_id = comp.split('_')
            if major_id not in which_comps:
                which_comps[major_id] = []
            which_comps[major_id] += [minor_id]
    else:
        all_comps = ['_'.join([major_id, minor_id]) for major_id in which_comps \
                     for minor_id in which_comps[major_id]]
        for comp in all_comps:
            if comp not in data:
                raise ValueError('Comparison not found in existing data: ' + comp)

    plotsdir = randdir + '/plots'
    if not os.path.isdir(plotsdir):
        os.makedirs(plotsdir)

    colors = {'20pt':'tab:orange', 'del':'m', '1del':'tab:purple', '2del':'tab:pink', 'gab':'g',
              'path':'tab:brown', '2nng':'c', 'urq':'k', 'mst':'b', '1nng':'r', 'bito':'y'}
    titles = {'tour':'TSP Tour', 'path':'TSP Path', 'bito':'Bitonic TSP Tour'}
    labels = {'20pt':'20% NNG', 'del':'Delaunay', '1del':'Order-1 Delaunay', '2del':'Order-2 Delaunay',
              'gab':'Gabriel', 'path':'TSP Path', '2nng':'2-NNG', 'urq':'Urquhart', 'mst':'MST',
              '1nng':'1-NNG', 'bito':'Bitonic TSP'}
    sample = {'pts_uni':'Uniform on Unit Square',
              'pts_annulus':'Non-Random on Annulus',
              'pts_annulus_random': 'Uniform on Annulus',
              'pts_ball':'Uniform on a Disk',
              'pts_clusnorm':'Clusters of Normal Distributions',
              'pts_cubediam':'Uniform on Unit Diagonal',
              'pts_corners':'Uniform on Vertices of a Regular Polygon',
              'pts_grid':'Uniform on Grid',
              'pts_normal':'Bivariate Normal',
              'pts_spokes':'Random Spokes',
              'pts_concentric_circular_points':'Concentric Circular Points'}
    for major_id in which_comps:
        all_comps = ['_'.join([major_id, minor_id]) for minor_id in which_comps[major_id]]
        fig, ax = plt.subplots()
        ax.set_title("    Fraction of " + titles[major_id] + " Edges Occuring in Various " + \
                      "Proximity Graphs\nSampling Type: " + sample[randtype],
                      fontdict={'fontsize':14})
        all_numpts = [num for comp in all_comps for num in data[comp].keys()]
        min_tour, max_tour = min(all_numpts), max(all_numpts)
        ax.set_xlim([min_tour-10,max_tour+10])
        ax.set_ylim([0,1.1])
        ax.set_xlabel("Number of points in point cloud")
        ax.set_ylabel("Fraction")
        for comp in all_comps:
            major_id, minor_id = comp.split('_')
            xvals = sorted(data[comp])
            comp_means = np.asarray([np.mean(data[comp][key]) for key in xvals])
            comp_stdvs = np.asarray([np.std(data[comp][key]) for key in xvals])
            ax.plot(xvals, comp_means, 'o-', markersize=3, label=labels[minor_id], color=colors[minor_id])
            ax.fill_between(xvals, comp_means-comp_stdvs, \
                            comp_means+comp_stdvs ,  color=colors[minor_id], alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(color='gray',linestyle='--',linewidth=0.5)
        fig.savefig(plotsdir + '/' + randtype + '_' + major_id + '_vs_graphs.pdf', format='pdf', bbox_inches='tight', dpi=500)

all_comps = {'tour':['1nng', '2nng', '20pt', 'mst', 'gab', 'urq', 'del', 'bito', 'path'],
             'path':['1nng', '2nng', '20pt', 'mst', 'gab', 'urq', 'del'],
             'bito':['1nng', '2nng', '20pt', 'mst', 'gab', 'urq', 'del']}
which_comps = {'tour':['1nng', '2nng', 'mst', 'gab', 'urq', 'bito', 'del', 'path']}
read_simul_data(randtype, which_comps='all')
