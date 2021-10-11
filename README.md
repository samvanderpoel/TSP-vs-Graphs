# SimulateTSP

This repository is part of ongoing research together with [Logan Graham](https://github.com/LoganDGraham), Hugo Mainguy, and 
[Gaurish Telang](https://github.com/gtelang).

SimulateTSP provides functions to explore the intersection behavior of traveling salesman problem (TSP) solutions 
with various proximity graphs through precisely tunable simulations. _TSP_ may refer to the TSP tour, TSP path, or bitonic TSP tour. Proximity graphs of interest include:
- k-nearest neighbor graphs (primarily k=1, 2, 0.2n)
- Minimum spanning tree (MST)
- Gabriel graph
- Urquhart graph
- Order-k Delaunay (primarily k=0, 1, 2; where k=0 coincides with the Delaunay triangulation)

Some motivating questions are:
- What fraction of TSP edges tend to be NNG (or MST, Gabriel, etc.) edges?
- Must the TSP contain at least one NNG (or MST, Gabriel, etc.) edge?
- What is the probability that the TSP is a subset of the order-k Delaunay?

# Setup
## Virtual environment
Create an [Anaconda](https://www.anaconda.com) environment with the necessary libraries:
```
conda create --name tsp python=3.7.3 pip
conda activate tsp
pip install -r requirements.txt
```
Next, set up [PyConcorde](https://github.com/jvkersch/pyconcorde):
```
git clone https://github.com/jvkersch/pyconcorde
cd pyconcorde
pip install -e .
cd ..
```

## Test program

A small test simulation can be executed with `bash test.sh`, the results of which will be stored in results/uniform-sqr-results.

# Main simulation

The main simulation programs are executed with `bash src/sim-serial.sh` (which simulates point cloud distributions serially) or `bash src/sim-parallel.sh`, 
(which simulates point cloud distributions in parallel). To specify the exact graphs to compute and graph comparisons to make, modify the bottom of src/main.py.
