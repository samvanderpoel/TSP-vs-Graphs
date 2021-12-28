#/usr/bin/python3.6

# The job of this script is to extract the coordinates of 
# each of the euclidean tsplib instaces to a 

import tsplib95
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import sys, os
import yaml
from colorama import Fore


if __name__ == '__main__':

    with open('euclidean_instances.txt') as f:
        filenames = f.readlines()
        filenames = [x.strip() for x in filenames] 

    for pname in filenames:
        print(Fore.CYAN+"Completed "+pname + '...')
        problem  = tsplib95.load_problem(pname+'.tsp')

        # Extract data into separate arrays
        xs, ys = [], []
        for (_, (x,y)) in problem.node_coords.items():
            xs.append(x)
            ys.append(y)


        # Write coordinates to corresponding yaml file    
        with open('euclidean_instances_yaml/'+ pname + '.yml', 'w') as outfile:
            yaml.dump( {'points': list(zip(xs,ys))}, outfile, default_flow_style=False)
   
