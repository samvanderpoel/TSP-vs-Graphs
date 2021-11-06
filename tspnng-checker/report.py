import os

for file in sorted(os.listdir('tour-reports')):
    lines = [l[:-1] for l in open('tour-reports/' + file, 'r').readlines()]
    print('proc ' + file[3:-4] + '\t\t'.join([''] + lines))