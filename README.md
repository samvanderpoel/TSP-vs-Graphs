# TSP-vs-Graphs
This repository is part of ongoing research in the Computational Geometry Group at Stony Brook University.

TSP-vs-Graphs includes programs to explore the intersection of traveling salesman problem (TSP) solutions and various proximity graphs. _TSP_ may refer to the TSP tour, TSP path, or bitonic TSP tour. Proximity graphs of interest include:
- k-nearest neighbor graphs (primarily k=1, 2, 0.2n)
- Minimum spanning tree (MST)
- Gabriel graph
- Urquhart graph
- Order-k Delaunay (primarily k=0, 1, 2; where k=0 coincides with the Delaunay triangulation)

Some motivating questions are:
- What fraction of TSP edges tend to be NNG (or MST, Gabriel, etc.) edges?
- Must the TSP contain at least one NNG (or MST, Gabriel, etc.) edge?
- Is the TSP always a subset of the order-k Delaunay for some k?

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
[GNU Parallel](https://www.gnu.org/software/parallel/) is also required for this repository.

## Test program
A small test simulation can be executed with `bash sim/test.sh`, the results of which will be stored in results/uniform-sqr-results.

# Main simulation
The main simulation is executed with `bash sim/simulate.sh`. All simulation parameters are specified at the top of sim/simulate.sh.
## Simulation parameters
- `minpts` and `maxpts` delineate the min and max point cloud sizes to simulate
- `interval` specifies the spacing between consecutive point cloud sizes
- `numrunsper` specifies how many point clouds to simulate per point cloud size
- `batch` specifies the number of point clouds to simulate concurrently
- `cloudtypes` lists the point cloud types to sample from (options are listed in sim/simulate.sh)
- `tour`, `path`, and `bito` list the specific comparisons to make between graphs. Graphs are specified by major_id and minor_id, as described at the top of sim/main.py
- `anoms` specifies which 'anomalies' to check for and record (if found); must be formatted as a Python dictionary. For example, "{'tour_6del':'<1','path_mst':'==1'}" checks for point clouds whose TSP tours are not a subset of the order-6 Delaunay; and point clouds whose TSP paths are equal to the MST.
- `par` specifies whether point cloud _types_ should be simulated in parallel (requires GNU's `parallel`)
- `concurrently` specifies number of point cloud types to simulate concurrently (if `par` is true)
