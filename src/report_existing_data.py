import os
import argparse
import numpy as np
from termcolor import colored

parser = argparse.ArgumentParser()
parser.add_argument('--summary', dest='summary', action='store_true')
parser.add_argument('--all', dest='summary', action='store_false')
parser.set_defaults(summary=True)
summary = parser.parse_args().summary

print(str(summary))

cwd = os.getcwd()
contents = os.listdir(os.path.join(cwd, 'results/'))

types = ['uniform-sqr','annulus','annulus-rand','uniform-ball',
         'normal-clust','uniform-diam','corners','uniform-grid',
         'normal-bivar','spokes','concen-circ']
dirnames = [name + '-results' for name in types]
labels = {'20pt':'20% NNG', 'del':'Delaunay', '1del':'Order-1 Delaunay', '2del':'Order-2 Delaunay',
          'gab':'Gabriel', 'path':'TSP Path', '2nng':'2-NNG', 'urq':'Urquhart', 'mst':'MST',
          '1nng':'1-NNG', 'bito':'Bitonic TSP', 'tour':'TSP Tour', 'path':'TSP Path'}

for item in contents:
    itempath = os.path.join(cwd, 'results/' + item)
    if os.path.isdir(itempath) and item in dirnames:
        # try:
        data = eval(open(os.path.join(itempath, 'data.txt'), 'r').read())
        print(colored('\n' + item[:-8].upper() + ' DATA:', 'green'))
        print(colored(55*'-', 'green'))
        for comp, v in data.items():
            majorid, minorid = comp.split('_')
            major_name, minor_name = labels[majorid], labels[minorid]
            print(colored('\n' + major_name + ' vs. ' + minor_name + ' comparisons:', 'red'))
            all_data = np.array([frac for _, data in v.items() for frac in data])
            print('min\t25\tmed\t75\tmax')
            print(str(round(np.percentile(all_data, 0), 3))   + '\t' + \
                  str(round(np.percentile(all_data, 25), 3))  + '\t' + \
                  str(round(np.percentile(all_data, 50), 3))  + '\t' + \
                  str(round(np.percentile(all_data, 75), 3))  + '\t' + \
                  str(round(np.percentile(all_data, 100), 3)))
            print('Fraction of point clouds whose intersection is not 100%: ' + str(round(np.mean(all_data!=1), 3)))
            if not summary:
                for num, data in v.items():
                    print('num pts: ' + str(num) + '\t\t' + str(len(data)) + '\tpoint clouds simulated')
        print(colored(55*'-', 'green'))
        # except:
        #     continue
