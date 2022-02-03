import argparse
import itertools
import os

parser = argparse.ArgumentParser()
parser.add_argument('--n', type=int, required=True)
parser.add_argument('--p', type=int, required=True)
parser.add_argument('--q', type=int, required=True)
parser.add_argument('--update', dest='update', action='store_true')
parser.set_defaults(update=False)
n = parser.parse_args().n
p = parser.parse_args().p
q = parser.parse_args().q
update = parser.parse_args().update

incomplete = []
if update:
    dirname = 'tour-reports-' + str(n)
    if os.path.exists(dirname):
        for gnuproc in range((n-2)**p):
            gnuprocdir = os.path.join(dirname, 'gnuproc' + str(gnuproc))
            if not os.path.exists(gnuprocdir):
                incomplete.append(gnuproc)
            elif 'success.txt' not in os.listdir(gnuprocdir):
                incomplete.append(gnuproc)
            elif 'failed.txt' in os.listdir(gnuprocdir):
                print('gnuproc ' + str(gnuproc) + ' failed')
    else:
        for gnuproc in range((n-2)**p):
            incomplete.append(gnuproc)

part1 = [
    list(
        set(range(n, 2*n)) - set([n+i, n+(i-1)%n])
    )
    for i in range(n)
]
part2 = [
    list(
        set(range(n)) - set([i%n, (i+1)%n])
    )
    for i in range(n, 2*n)
]
both = part1 + part2
mids = both[2*n-(p+q):2*n-q]

with open('args' + str(n) + '.txt', 'w') as f:
    for idx, element in enumerate(itertools.product(*mids)):
        if update and idx not in incomplete:
            continue
        f.write("python tournng.py" \
                + " --mid=\"" + str(list(element)) + "\"" \
                + " --n=" + str(n) \
                + " --p=" + str(p) \
                + " --q=" + str(q) \
                + " --gnuproc=" + str(idx) + "\n")
