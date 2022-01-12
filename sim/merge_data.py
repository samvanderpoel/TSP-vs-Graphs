import sys
import os

file1, file2, dest = sys.argv[1], sys.argv[2], sys.argv[3]
data1 = eval(open(file1, 'r').read())
data2 = eval(open(file2, 'r').read())

for comp in data1:
    for num in data1[comp]:
        if comp not in data2:
            data2[comp] = {}
        if num in data2[comp]:
            data2[comp][num] += data1[comp][num]
        else:
            data2[comp][num] = data1[comp][num]

with open(os.path.join(dest), 'w') as f:
    f.write(str(data2))
