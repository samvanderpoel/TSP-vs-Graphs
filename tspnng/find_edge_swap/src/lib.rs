use itertools::Itertools;
use petgraph::algo;
use petgraph::prelude::*;
use petgraph::{Graph, Undirected};
use pyo3::prelude::*;
use std::collections::{HashMap, HashSet};

#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(find_edge_swap, m)?)?;
    Ok(())
}

/// Looks for a profitable edge swap.
///
/// Returns a profitable edge swap if one exists. Otherwise, returns `None`. The present function is
/// a thin, public wrapper for `edge_swap_search`, which is intended to be private.
#[pyfunction]
fn find_edge_swap(n: usize, k: usize, suffix: Vec<usize>) -> Option<(Vec<usize>, Vec<usize>)> {
    // edge_list for graphs to be created
    let edge_list = (0..n)
        .map(|x| (x, (x + 1) % n))
        .collect::<Vec<(usize, usize)>>();

    // search for an edge swap; nested loops are here, but factored into several functions
    edge_swap_search(n, k, &suffix, &edge_list)
}

/// Looks for a profitable edge swap.
///
/// Returns a profitable edge swap if one exists. Otherwise, returns `None`. The present function is
/// intended to be private. Used as a helper function in `find_edge_swap`.
fn edge_swap_search(
    n: usize,
    k: usize,
    suffix: &[usize],
    edge_list: &[(usize, usize)],
) -> Option<(Vec<usize>, Vec<usize>)> {
    // iterate over all Snng prefixes (for parallelism via gnu parallel)
    for prefix in snng_parallel(n, k).into_iter().multi_cartesian_product() {
        // instantiate a graph along with hashmaps to keep track of indices
        let (mut g, node_indices, edge_indices) = graph_from_edges(edge_list);

        let sigma = [&prefix[..], suffix].concat();

        if found_edge_swap_sigma(&sigma, n, &mut g, &node_indices, &edge_indices) {
            continue;
        } else {
            return Some((sigma, vec![1; n]));
        }
    }
    None
}

/// Looks for an edge swap associated with a particular `\sigma` vector.
fn found_edge_swap_sigma(
    sigma: &[usize],
    n: usize,
    g: &mut Graph<usize, usize, Undirected>,
    node_indices: &HashMap<usize, NodeIndex>,
    edge_indices: &HashMap<(usize, usize), EdgeIndex>,
) -> bool {
    // iterate over [-1, -1, -1], [-1, -1, 0], ..., [1, 1, 1]
    for e in vec![[-1, 0, 1]; n].into_iter().multi_cartesian_product() {
        // skip the zero vector
        if e.iter().all(|&x| x == 0) {
            continue;
        } else {
            for i in 0..n {
                if e[i] == -1 || e[i] == 1 {
                    if e[i] == -1 {
                        // remove edge (i, (i - 1) % n)
                        if let Some(x) = edge_indices.get(&(i, (i - 1) % n)) {
                            g.remove_edge(*x);
                        }
                        //g.remove_edge(*edge_indices.get(&(i, (i - 1) % n)).unwrap());
                    } else if e[i] == 1 {
                        // remove edge (i, (i + 1) % n)
                        if let Some(x) = edge_indices.get(&(i, (i + 1) % n)) {
                            g.remove_edge(*x);
                        }
                        //g.remove_edge(*edge_indices.get(&(i, (i + 1) % n)).unwrap());
                    }
                }

                // add edge (i, sigma[i])
                g.add_edge(
                    *node_indices.get(&i).unwrap(),
                    *node_indices.get(&sigma[i]).unwrap(),
                    1,
                );
            }
        }
        //println!("{:?}", g);
        //println!("size: {}", g.edge_count());
        // if is_cycle
        if is_cycle(g) {
            return true;
        }
    }
    false
}

/// Instantiates a `petgraph::Graph` from a slice of two-tuples denoting edges.
///
/// Returns the newly instantiated `Graph`, along with `HashMap`s for keeping track of indices.
fn graph_from_edges(
    edge_list: &[(usize, usize)],
) -> (
    Graph<usize, usize, Undirected>,
    HashMap<usize, NodeIndex>,
    HashMap<(usize, usize), EdgeIndex>,
) {
    let mut g = Graph::<usize, usize, Undirected>::new_undirected();
    let mut node_indices = HashMap::<usize, NodeIndex>::new();
    let mut edge_indices = HashMap::<(usize, usize), EdgeIndex>::new();
    for (i, j) in edge_list.iter() {
        // add nodes
        // ix is node i's index
        let ix = g.add_node(*i);
        node_indices.insert(*i, ix);
        // jx is node j's index
        let jx = g.add_node(*j);
        node_indices.insert(*j, jx);

        // add edge
        // ex is edge (ix, jx)'s index
        let ex = g.add_edge(ix, jx, 1);
        edge_indices.insert((*i, *j), ex);
    }

    (g, node_indices, edge_indices)
}

/// Returns a vector of `\sigma` prefixes.
///
/// `found_edge_swap_sigma` uses the elements of the present function's returned vector as
/// arguments.
fn snng_parallel(n: usize, k: usize) -> Vec<Vec<usize>> {
    (0..k)
        .map(|i| snng_set_diff(i, n))
        .collect::<Vec<Vec<usize>>>()
}

/// Performs modular arithmetic and a set difference to produce a vector of indices.
///
/// Used as a helper function in `snng_parallel`.
fn snng_set_diff(i: usize, n: usize) -> Vec<usize> {
    let a = (0..n).collect::<HashSet<usize>>();
    let b = vec![(i - 1) % n, i, (i + 1) % n]
        .into_iter()
        .collect::<HashSet<usize>>();
    a.difference(&b).copied().collect::<Vec<usize>>()
}

/// Tests whether or not a graph is isomorphic to a cycle on at least three vertices.
fn is_cycle(g: &Graph<usize, usize, Undirected>) -> bool {
    is_two_regular(g) && (algo::connected_components(g) != 1)
}

/// Tests whether or not all vertices in a nonempty graph have degree exactly two.
fn is_two_regular(g: &Graph<usize, usize, Undirected>) -> bool {
    for idx in g.node_indices() {
        if g.neighbors(idx).count() != 2 {
            return false;
        }
    }
    true
}
