import os

cwd = os.getcwd()
contents = os.listdir(cwd)
for item in contents:
    itempath = os.path.join(cwd, item)
    if os.path.isdir(itempath) and item.startswith('pts_'):
        try:
            data = eval(open(os.path.join(itempath, 'data.txt'), 'r').read())
            print('\n' + item.split('-')[0].upper() + ' DATA:\n' + 55*'-')
            for k, v in data.items():
                print(k + ' comparisons:')
                for num, data in v.items():
                    print('num pts: ' + str(num) + '\t\t' + str(len(data)) + '\tpoint clouds simulated')
            print(55*'-')
        except:
            continue
