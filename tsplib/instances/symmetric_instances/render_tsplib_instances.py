# TSPLIB95 is a suite of test problem instances for the travelling salesman problem
# This little script is just meant to test the tsplib95 parser
import tsplib95
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import sys, os, colorama

pname = 'eil101'
problem  = tsplib95.load_problem(pname+'.tsp')
solution = tsplib95.load_solution(pname+'.opt.tour')

print(problem.node_coords)
print(solution)

xs, ys = [], []

for (_, (x,y)) in problem.node_coords.items():
   xs.append(x)
   ys.append(y)

# rearrange the coordinates according to the optimal tour
solution.tour = [ i-1 for i in solution.tours[0]]
xs = [xs[i] for i in solution.tour]
ys = [ys[i] for i in solution.tour]

fig, ax = plt.subplots()
ax.set_aspect(1.0)
plt.plot(xs+[xs[0]],ys+[ys[0]],'o-',  markersize=5)
plt.plot()
plt.show()
