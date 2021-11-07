import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--n', type=int, required=True)
n = parser.parse_args().n

dirname = 'tour-reports-' + str(n)
if os.path.exists(dirname):
    linesout = {}
    for file in os.listdir(dirname):
        lines = [l[:-1] for l in open(dirname + '/' + file, 'r').readlines()]
        linesout[int(file[3:-4])] = 'proc ' + file[3:-4] + '\t' + '\t'.join(lines)
    for line in sorted(linesout):
        print(linesout[line])
else:
    print('path does not exist')
    