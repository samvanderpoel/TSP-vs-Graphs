import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--n', type=int, required=True)
n = parser.parse_args().n

fname = 'example-graphs/kgab/gab' + str(n) + '.yaml'

with open(fname, 'w') as f:
    lines = ['points:\n', '  - [0,0]\n']
    for i in range(1, n-1):
        lines.append('  - ' + str([5*i,(-1)**i]) + '\n')
    lines.append('  - ' + str([5*(n-1),0]) + '\n')
    f.writelines(lines)
