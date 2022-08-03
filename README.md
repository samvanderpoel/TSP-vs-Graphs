# TSP-vs-Graphs

<img src="point-sets/aggregate.png" width=max-width>

Associated paper: [On Some Relations Between Optimal TSP Solutions and Proximity Graphs in the Plane](https://eurocg2022.unipg.it/booklet/EuroCG2022-Booklet.pdf#page=495) with [Logan D. Graham](https://github.com/LoganDGraham), Joseph S. B. Mitchell, and [Gaurish Telang](https://github.com/gtelang).

TSP-vs-Graphs is a repository for researching relations between the traveling salesman problem (TSP) and proximity graphs. It includes
- a simulation API
- a GUI for plotting point sets and computing the TSP and proximity graphs
- the experimental results of our paper
- a highly optimized implementation of the TSP-NNG enumeration algorithm
- a collection of Euclidean TSPLIB instances ready for plotting

The TSP tour, TSP path, and bitonic TSP tour are implemented. Proximity graphs of interest include the k-nearest neighbor graph (k-NNG), minimum spanning tree (MST), Gabriel graph, Urquhart graph, and order-k Delaunay (primarily k=0, 1, 2).

## Contents
1. [Setup](#setup)
2. [Simulation](#simulation)
3. [Graphical User Interface](#graphical-user-interface)
4. [Point Sets](#point-sets)
5. [TSP-NNG Enumeration Algorithm](#tsp-nng-enumeration-algorithm)

# Setup
```
git clone https://github.com/samvanderpoel/TSP-vs-Graphs
cd TSP-vs-Graphs
```
The most reliable way to set up the necessary libraries is by creating the following [Conda](https://www.anaconda.com) environment:
```
conda env create -f tsp_env.yml
conda activate tsp
conda install matplotlib-base=3.5.0
```
Alternatively, you may use pip (with Python 3.7), which is sufficient for the simulation API and GUI. If you use pip, we recommend initializing a virtual environment first (this could be a conda virtual environment).
```
pip install -r requirements.txt
```

Another (arguably better) way to setup the necessary libraries using pip is to navigate to the top of the TSP-vs-Graphs directory and run
```
pip install .
```
(If you intend to make edits to the TSP-vs-Graphs source code, then run `pip install -e .` instead).

If you use pip, you will need to install a separate [Rust](https://rustup.rs) compiler for the TSP-NNG algorithm.

Next, set up [PyConcorde](https://github.com/jvkersch/pyconcorde):
```
git clone https://github.com/jvkersch/pyconcorde
cd pyconcorde
pip install .
cd ..
```
(If you intend to make edits to the PyConcorde source code, then run `pip install -e .` instead).
[GNU Parallel](https://www.gnu.org/software/parallel/) is used in our parallel TSP-NNG implementation, and it is optionally used in the [Simulation](#simulation) code.

# Simulation
We illustrate usage of the simulation API by way of an example simulation called `test`. The `test` simulation is specified by the following items:
- a top-level script sim/test.sh
- a simulation config file sim/config_simul/test.yaml
- a plotting config file sim/config_plots/test.yaml

Run the simulation with `bash sim/test.sh`. Several simulation jobs can run concurrently as long as they have distinct `jobname`s as specified in their config files.

The results of the `test` simulation will appear in results/test, and they are organized by point set distributions (e.g. uniform on [0,1]x[0,1], bivariate normal, etc.). Graph comparison results are stored in files 'data.txt', simulation meta-data are stored in files 'meta.txt', and simulation compute times are stored in files 'compute-times.txt'.

In simulation and plotting scripts, each graph type has a unique string IDs to track comparisons and organize results. The graph IDs are:
- TSP tour: `tour`
- TSP path: `path`
- Bitonic TSP tour: `bito`
- k-NNG: `{k}nng` (e.g. 1-NNG: `1nng`; 2-NNG: `2nng`)
- 20%-NNG: `20pt`
- MST: `mst`
- Urquhart graph: `urq`
- Gabriel graph: `gab`
- Delaunay triangulation: `del`
- Order-k Delaunay: `{k}del` (e.g. 1-Delaunay: `1del`; 2-Delaunay: `2del`)

## Print a Summary of Simulation Results
Existing data from the `test` simulation are printed to standard output with
```
python sim/report_existing_data.py --jobname test
```
The optional flag `--all` verbosely prints data for each point set size, and the flag `--export` writes statistics to .csv:
```
python sim/report_existing_data.py --jobname test --all --export
```

## Plot Simulation Results
Plotting of simulation results can be done individually, as in
```
python sim/plot_simul_data.py --config sim/config_plots/test.yaml --cloudtype uniform-sqr
```
or in a batch, as in sim/gen_plots.sh.

## Merge simulation data files
Merge two simulation data files path/to/data1.txt and path/to/data2.txt into a new data file path/to/data.txt via the command
```
python sim/merge_data.py path/to/data1.txt path/to/data2.txt path/to/data.txt
```

## Graph comparison and anomaly detection
The primary purpose of the simulation API is large-scale edgewise graph comparison, but it is sufficiently general that other graph theoretic or geometric properties can be tested at scale. The function `sim.utils.compare` tests whether simulated graphs satisfy a given criterion and, if so, saves the corresponding point set to a yaml file.

For example, one may wish to test whether it is possible for the TSP tour to properly cross the MST. One would test this in `sim.utils.compare` when `comp=='tour_mst'` by implementing a routine to check for graph crossing.

Simple anomalies to search for (and record) may be specified in the `anoms` section of a simulation config. For example,
```
anoms:
  tour_1del: '<1'
  path_mst: '==1'
```
records the coordinates of a point set if its TSP tour is not a subset of its 1-Delaunay graph, or if its TSP path is equal to its MST.

# Graphical User Interface
## Basic interactive mode
The GUI is launched with
```
python plot/plot.py --interactive
```
Points may be double-clicked directly onto the canvas. To compute graphs for a point set on the canvas, the current window must be the GUI canvas, and press `i`. You will see a set of options appear in the terminal; enter the string associated with the graph you would like to compute.

To clear all edges from the current point cloud, press `x`; to clear all points and edges, press `c`.

Points sets may be sampled from various distributions. Press `n` (with the GUI as the current window) to see a list of options; answer the prompts in your terminal to specify the distribution.

Pressing `o` activates automatic comparison of edges of each graph computed with edges of the Euclidean TSP tour and path.

To export the current figure to the plot directory, press `e`.

## Plotting a point cloud from YAML
All point sets are stored in .yaml files in this repository. For example, to plot TSPLIB instance TSP225, run
```
python plot/plot.py --file tsplib/instances/euclidean_instances/tsp225.yaml
```
Compute and plot graphs as described above (by pressing `i`), or press `t` while the GUI is selected to display the following

<p align="center">
  <img src="point-sets/tsplib.png" width=500>
</p>

# Point Sets
Coordinates and figures are provided for salient point sets.

Scripts are provided to generate point sets that 'witness' a certain claim. For example, point-sets/kdel/gen_kdel.py generates a point set with the property that its Euclidean TSP tour or path is _not_ a subset of its corresponding k-Delaunay graph, for any user-specified k. A typical usage is
```
python point-sets/kdel/gen_kdel.py --mode tour --k 3
python plot/plot.py --file point-sets/kdel/tour-3del.yaml
```

Similarly, point-sets/kgab/gen_kgab.py generates a point set of size n with the property that only two of its Euclidean TSP tour edges belong to its Gabriel graph:
```
python point-sets/kgab/gen_kgab.py --n 9
python plot/plot.py --file point-sets/kgab/gab9.yaml
```

# TSP-NNG Enumeration Algorithm
The TSP-NNG enumeration algorithm is presented in tspnng/pseudocode.pdf and implemented in tspnng/main.py. The script tspnng/run_tour_nng.sh executes the algorithm for a specific value of `n` and user-specified degrees of parallelism (provided by GNU parallel and Python's multiprocessing). Execute run_tour_nng.sh from the tspnng directory.

The user may use NetworkX, graph-tool, or petgraph (Rust) as the underlying graph library for the algorithm. The specific method is set in tspnng/main.py.

The high-performance version of the algorithm uses Rust. To set up the Rust library,
```
cd tspnng/find_edge_swap
maturin develop
cd ..
```

If you wish to use the graph-tool method, first
```
conda install -c conda-forge graph-tool
```

The script tspnng/run_tour_nng_serial.py is a serial implementation of the enumeration algorithm for illustrative purposes. On a PC, it is reasonable to run this up to n=8 or so.
