# TSP-vs-Graphs
TSP-vs-Graphs is a repository for studying relations between the traveling salesman problem (TSP) and proximity graphs.

The TSP tour, TSP path, and bitonic TSP tour are implemented and studied. Proximity graphs of interest include the k-nearest neighbor graph (k-NNG), minimum spanning tree (MST), Gabriel graph, Urquhart graph, and order-k Delaunay (primarily k=0, 1, 2).

## Contents
1. [Setup](#setup)
2. [Simulation](#simulation)
3. [Graphical User Interface](#graphical-user-interface)
4. [TSP-NNG Intersection Algorithm](#tsp-nng-intersection-algorithm)

# Setup
Clone and `cd` into this repository:
```
git clone https://github.com/samvanderpoel/TSP-vs-Graphs
cd TSP-vs-Graphs
```
Create a Conda environment (see [Anaconda](https://www.anaconda.com)) with the necessary libraries:
```
conda create --name tsp python=3.7.3 pip
conda activate tsp
conda install -c conda-forge graph-tool
pip install -r requirements.txt
```
Next, set up [PyConcorde](https://github.com/jvkersch/pyconcorde):
```
git clone https://github.com/jvkersch/pyconcorde
cd pyconcorde
pip install -e .
cd ..
```
[GNU Parallel](https://www.gnu.org/software/parallel/) is optionally used in the simulation code (see [Simulation Parameters](#simulation-parameters)).

# Simulation
Simulation jobs are specified in scripts having the format of srs/simulate.sh, and simulations are executed with `bash sim/simulate.sh`. Several jobs may be run concurrently as long as they have distinct `jobname`s.

## Simulation Parameters
- `jobname` is the unique name identifying the current simulation job
- `minpts` and `maxpts` delineate the min and max point cloud sizes to simulate
- `interval` specifies the spacing between consecutive point cloud sizes
- `numrunsper` specifies how many point clouds to simulate per point cloud size
- `batch` specifies the number of point clouds to simulate concurrently
- `cloudtypes` lists the point cloud types to sample from (options are listed in sim/simulate.sh)
- `tour`, `path`, and `bito` list the specific comparisons to make between graphs. Graphs are specified by major_id and minor_id, as described at the top of sim/main.py
- `anoms` specifies which 'anomalies' to check for and record (if found); must be formatted as a Python dictionary. For example, "{'tour_6del':'<1','path_mst':'==1'}" checks for point clouds whose TSP tours are not a subset of the order-6 Delaunay; and point clouds whose TSP paths are equal to the MST.
- `par` specifies whether point cloud _types_ should be simulated in parallel (requires GNU's `parallel`)
- `concurrently` specifies number of point cloud types to simulate concurrently (if `par` is true)

## Test Program
A test simulation can be executed with `bash sim/test.sh`, the results of which will be stored in results/test/uniform-sqr-results.

## Printing a Summary of Simulation Results
Existing data from job "myjob" are printed to standard output with
```
python sim/report_existing_data.py --jobname myjob
```
The optional flag ``--all`` verbosely prints data for each point cloud size, and the flag ``--export`` writes statistics to a csv file:
```
python sim/report_existing_data.py --jobname myjob --all --export
```

## Plotting Simulation Results

# Graphical User Interface

# TSP-NNG Intersection Algorithm
