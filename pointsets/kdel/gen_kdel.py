import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--mode', type=str, required=True)
parser.add_argument('--k', type=int, required=True)
mode = parser.parse_args().mode
k = parser.parse_args().k

fname = 'pointsets/kdel/' + mode + '-' + str(k) + 'del.yaml'

with open(fname, 'w') as f:
    if mode == 'tour':
        lines = ['points:\n',
                 '  - [0,0]\n',
                 '  - [1,0]\n',
                 '  - [4,0]\n',
                 '  - [4,1]\n',
                 '  - [5,2]\n']
        p1, p2 = np.array([0,0]), np.array([1,0])
        p3, p4 = np.array([4,1]), np.array([5,2])
    elif mode == 'path':
        lines = ['points:\n',
                 '  - [0,0]\n',
                 '  - [5,1]\n',
                 '  - [5.1,6]\n',
                 '  - [7,0]\n',
                 '  - [9,6]\n']
        p1, p2 = np.array([5,1]), np.array([7,0])
        p3, p4 = np.array([5.1,6]), np.array([9,6])
    l1 = [list(p1 + (i+1)*(p2-p1)/(k+1)) for i in range(k)]
    l2 = [list(p3 + (i+1)*(p4-p3)/(k+1)) for i in range(k)]
    for pt in l1 + l2:
        lines.append('  - ' + str(pt) + '\n')
    f.writelines(lines)
