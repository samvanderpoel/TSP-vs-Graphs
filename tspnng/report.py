import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--n', type=int, required=True)
parser.add_argument('--p', type=int, required=True)
n = parser.parse_args().n
p = parser.parse_args().p

dirname = 'tour-reports-' + str(n)
if os.path.exists(dirname):
    linesout = {}
    for gnuproc in range((n-3)**p):
        gnuprocdir = os.path.join(dirname, 'gnuproc' + str(gnuproc))
        if not os.path.exists(gnuprocdir):
            linesout[gnuproc] = ['gnuproc ' + str(gnuproc) + \
                                 '\t\thas not started', 'incomplete']
        elif 'failed.txt' in os.listdir(gnuprocdir):
            fname = os.path.join(gnuprocdir, 'failed.txt')
            message = open(fname).readlines()[0]
            linesout[gnuproc] = [message, 'failed']
        elif 'success.txt' in os.listdir(gnuprocdir):
            fname = os.path.join(gnuprocdir, 'success.txt')
            message = open(fname).readlines()[0]
            linesout[gnuproc] = [message, 'success']
        else:
            linesout[gnuproc] = ['gnuproc ' + str(gnuproc) + \
                                 '\t\tis incomplete', 'incomplete']
    for gnuproc in sorted(linesout):
        print(linesout[gnuproc][0])
    results = [linesout[gnuproc][1] for gnuproc in linesout]
    if 'failed' in results:
        outcome = 'False'
    elif 'failed' not in results and 'incomplete' in results:
        outcome = 'Inconclusive'
    else:
        outcome = 'True'
    print('\n' + outcome)
else:
    print('path does not exist')
    