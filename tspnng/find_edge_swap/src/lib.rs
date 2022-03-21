use itertools::Itertools;
use petgraph::algo;
use petgraph::prelude::*;
use petgraph::{Graph, Undirected};
use pyo3::prelude::*;
use std::collections::{hash_map, HashMap, HashSet};

#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(find_edge_swap, m)?)?;
    Ok(())
}

/// Looks for a profitable edge swap.
///
/// Returns `None` if a profitable edge swap exists. Otherwise, returns a witness `\sigma`. The
/// present function is a thin, public wrapper for `edge_swap_search`, which is intended to be
/// private.
#[pyfunction]
fn find_edge_swap(n: usize, k: usize, suffix: Vec<usize>) -> Option<Vec<usize>> {
    // edge_list for graphs to be created
    let edge_list = (0..n)
        .map(|x| (x, (x + 1) % n))
        .collect::<Vec<(usize, usize)>>();

    // search for an edge swap; nested loops are here, but factored into several functions
    edge_swap_search(n, k, &suffix, &edge_list)
}

/// Looks for a profitable edge swap.
///
/// Returns `None` if a profitable edge swap exists; otherwise, returns a witness `\sigma`. The
/// present function is intended to be private. Used as a helper function in `find_edge_swap`.
fn edge_swap_search(
    n: usize,
    k: usize,
    suffix: &[usize],
    edge_list: &[(usize, usize)],
) -> Option<Vec<usize>> {
    // iterate over all Snng prefixes (for parallelism via gnu parallel)
    for prefix in snng_parallel(n, k).into_iter().multi_cartesian_product() {
        // instantiate a graph along with hashmaps to keep track of indices
        let (g, node_indices, edge_indices) = graph_from_edges(edge_list);

        let sigma = [&prefix[..], suffix].concat();

        if found_edge_swap_sigma(&sigma, n, &g, &node_indices, &edge_indices) {
            continue;
        } else {
            return Some(sigma);
        }
    }
    None
}

/// Looks for an edge swap associated with a particular `\sigma` vector.
fn found_edge_swap_sigma(
    sigma: &[usize],
    n: usize,
    g: &Graph<usize, usize, Undirected>,
    node_indices: &HashMap<usize, NodeIndex>,
    edge_indices: &HashMap<(usize, usize), EdgeIndex>,
) -> bool {
    // iterate over [-1, -1, -1], [-1, -1, 0], ..., [1, 1, 1]
    for e in vec![[-1, 0, 1]; n].into_iter().multi_cartesian_product() {
        let mut g_prime = g.clone();
        // skip the zero vector
        if e.iter().all(|&x| x == 0) {
            continue;
        } else {
            for i in 0..n {
                // if i == 0, then the subtraction i-1 won't work (usize underflow), so we handle
                // this case separately
                if e[i] == -1 && i == 0 {
                    // remove edge (i, n - 1)
                    if let Some(x) = edge_indices.get(&(i, n - 1)) {
                        g_prime.remove_edge(*x);
                        // add edge (i, sigma[i])
                        g_prime.add_edge(
                            *node_indices.get(&i).unwrap(),
                            *node_indices.get(&sigma[i]).unwrap(),
                            1,
                        );
                    }
                } else if e[i] == -1 && i >= 1 {
                    // remove edge (i, (i - 1) % n)
                    if let Some(x) = edge_indices.get(&(i, (i - 1) % n)) {
                        g_prime.remove_edge(*x);
                        // add edge (i, sigma[i])
                        g_prime.add_edge(
                            *node_indices.get(&i).unwrap(),
                            *node_indices.get(&sigma[i]).unwrap(),
                            1,
                        );
                    }
                } else if e[i] == 1 {
                    // remove edge (i, (i + 1) % n)
                    if let Some(x) = edge_indices.get(&(i, (i + 1) % n)) {
                        g_prime.remove_edge(*x);
                        // add edge (i, sigma[i])
                        g_prime.add_edge(
                            *node_indices.get(&i).unwrap(),
                            *node_indices.get(&sigma[i]).unwrap(),
                            1,
                        );
                    }
                }
            }
            // if g is a cycle
            if is_cycle(&g_prime) {
                return true;
            }
        }
    }
    false
}

/// A `petgraph::Graph` along with `HashMap`s for indexing into nodes and edges with `usize`s.
///
/// The `HashMap`s keep track of the `NodeIndex` and `EdgeIndex` values.
type IndexableGraph = (
    Graph<usize, usize, Undirected>,
    HashMap<usize, NodeIndex>,
    HashMap<(usize, usize), EdgeIndex>,
);

/// Instantiates a `petgraph::Graph` from a slice of two-tuples denoting edges.
///
/// Returns the newly instantiated `Graph`, along with `HashMap`s for keeping track of indices.
fn graph_from_edges(edge_list: &[(usize, usize)]) -> IndexableGraph {
    let mut g = Graph::<usize, usize, Undirected>::default();
    let mut node_indices = HashMap::<usize, NodeIndex>::new();
    let mut edge_indices = HashMap::<(usize, usize), EdgeIndex>::new();
    for (i, j) in edge_list.iter() {
        // add nodes
        // ix is node i's index
        let ix = safe_add_node(*i, &mut g, &mut node_indices);
        // jx is node j's index
        let jx = safe_add_node(*j, &mut g, &mut node_indices);

        // add edge
        // ex is edge (ix, jx)'s index
        safe_add_edge(*i, *j, ix, jx, &mut g, &mut edge_indices);
    }

    (g, node_indices, edge_indices)
}

/// Adds a node to graph `g` if it is not currently present in `g`.
///
/// Returns the node's `NodeIndex`. If the node was already present in `g`, then this is the current
/// `NodeIndex`, and no node is added to `g`. This behavior is what we mean by "safe."
fn safe_add_node(
    weight: usize,
    g: &mut Graph<usize, usize, Undirected>,
    node_indices: &mut HashMap<usize, NodeIndex>,
) -> NodeIndex {
    if let hash_map::Entry::Vacant(e) = node_indices.entry(weight) {
        let ix = g.add_node(weight);
        e.insert(ix);
        ix
    } else {
        *node_indices.get(&weight).unwrap()
    }
}

/// Adds an edge between two nodes `i`, `j` in `g` if it is not currently present in `g`.
///
/// If there is already an edge between nodes `i` and `j` in `g`, then no edge is added. This
/// behavior is what we mean by "safe."
fn safe_add_edge(
    i_weight: usize,
    j_weight: usize,
    ix: NodeIndex,
    jx: NodeIndex,
    g: &mut Graph<usize, usize, Undirected>,
    edge_indices: &mut HashMap<(usize, usize), EdgeIndex>,
) {
    if let hash_map::Entry::Vacant(e) = edge_indices.entry((i_weight, j_weight)) {
        let ex = g.add_edge(ix, jx, 1);
        e.insert(ex);
    } else if let hash_map::Entry::Vacant(e) = edge_indices.entry((j_weight, i_weight)) {
        let ex = g.add_edge(jx, ix, 1);
        e.insert(ex);
    }
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
    if i == 0 {
        let b = vec![n - 1, i, (i + 1) % n]
            .into_iter()
            .collect::<HashSet<usize>>();
        a.difference(&b).copied().collect::<Vec<usize>>()
    } else {
        let b = vec![(i - 1) % n, i, (i + 1) % n]
            .into_iter()
            .collect::<HashSet<usize>>();
        a.difference(&b).copied().collect::<Vec<usize>>()
    }
}

/// Tests whether or not a graph is isomorphic to a cycle on at least three vertices.
fn is_cycle(g: &Graph<usize, usize, Undirected>) -> bool {
    is_two_regular(g) && (algo::connected_components(g) == 1)
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
