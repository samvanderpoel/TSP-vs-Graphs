import os

cwd = os.getcwd()
contents = os.listdir(os.path.join(cwd, 'results/'))

types = ['uniform-sqr','annulus','annulus-rand','uniform-ball',
         'normal-clust','uniform-diam','corners','uniform-grid',
         'normal-bivar','spokes','concen-circ']
dirnames = [name + '-results' for name in types]

for item in contents:
    itempath = os.path.join(cwd, 'results/' + item)
    if os.path.isdir(itempath) and item in dirnames:
        try:
            data = eval(open(os.path.join(itempath, 'data.txt'), 'r').read())
            print('\n' + item[:-8].upper() + ' DATA:\n' + 55*'-')
            for k, v in data.items():
                print(k + ' comparisons:')
                for num, data in v.items():
                    print('num pts: ' + str(num) + '\t\t' + str(len(data)) + '\tpoint clouds simulated')
            print(55*'-')
        except:
            continue
