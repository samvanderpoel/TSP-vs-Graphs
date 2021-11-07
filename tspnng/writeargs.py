import argparse
import itertools
import os

parser = argparse.ArgumentParser()
parser.add_argument('--n', type=int, required=True)
parser.add_argument('--p', type=int, required=True)
parser.add_argument('--q', type=int, required=True)
n = parser.parse_args().n
p = parser.parse_args().p
q = parser.parse_args().q

midinds = list(range(n-(p+q), n-q))
mids = [list( set(range(n))-set([(i-1)%n,i,(i+1)%n]) ) \
        for i in midinds]

with open('args' + str(n) + '.txt', 'w') as f:
    for idx, element in enumerate(itertools.product(*mids)):
        f.write('python tournng.py --mid=\"' + str(list(element)) + \
                '\" --n=' + str(n) + ' --p=' + str(p) + \
                ' --q=' + str(q) + ' --gnuproc=' + str(idx) + '\n')