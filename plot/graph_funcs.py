import os
import sys
import itertools as it
import scipy as sp
import numpy as np
import networkx as nx
import math

from sklearn.neighbors import NearestNeighbors
from scipy.spatial import Delaunay
from scipy.spatial import Voronoi
from concorde.tsp import TSPSolver
from orderk_delaunay import *

def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def perturb_pts(points, xptb=0.001, yptb=0.001):
    """
    Perturb (uniformly) the x- and y-coordinates of points
    within intervals [x-xptb, x+xptb], [y-yptb,y+yptb]
    Useful for removing degeneracies
    """
    points = np.asarray(points)
    dxs = -xptb + 2*xptb*np.random.random(len(points))
    dys = -yptb + 2*yptb*np.random.random(len(points))
    dps = np.asarray(list(zip(dxs,dys)))
    points = points + dps
    return points

def get_nng_graph(points, k=None, pct=None, metric=2):
    n = len(points)
    if pct is not None:
        k = math.ceil(pct * n)
    points     = np.array(points)
    coords     = [{"pos":pt} for pt in points]
    nng_graph = nx.Graph()
    nng_graph.add_nodes_from(zip(range(len(points)), coords))
    if metric=='inf':
        nbrs = NearestNeighbors(
            n_neighbors=(k+1),
            algorithm='ball_tree',
            metric='chebyshev'
        ).fit(points)
    else:
        nbrs = NearestNeighbors(
            n_neighbors=(k+1),
            algorithm='ball_tree',
            metric='minkowski',
            p=float(metric)
        ).fit(points)
    distances, indices = nbrs.kneighbors(points)
    edge_list = []

    for nbidxs in indices:
        nfix = nbidxs[0]
        edge_list.extend([(nfix,nvar) for nvar in nbidxs[1:]])

    nng_graph.add_edges_from(edge_list)
    if pct is not None:
        nng_graph.graph['type'] = f"{100*pct}-pct-nng"
    else:
        nng_graph.graph['type'] = 'nng'
    return nng_graph

def get_delaunay_tri_graph(points):
    points       = np.array(points)
    coords       = [{"pos":pt} for pt in points]
    tri          = Delaunay(points)
    deltri_graph = nx.Graph()

    deltri_graph.add_nodes_from(zip(range(len(points)), coords))

    edge_list = []
    for (i,j,k) in tri.simplices:
        edge_list.extend([(i,j),(j,k),(k,i)])    
    deltri_graph.add_edges_from(edge_list)
     
    total_weight_of_edges = 0.0
    for edge in deltri_graph.edges:
        n1, n2 = edge
        pt1 = deltri_graph.nodes[n1]['pos'] 
        pt2 = deltri_graph.nodes[n2]['pos']
        edge_wt = np.linalg.norm(pt1-pt2)
        deltri_graph.edges[n1,n2]['weight'] = edge_wt
        total_weight_of_edges = total_weight_of_edges + edge_wt 
    deltri_graph.graph['weight'] = total_weight_of_edges
    deltri_graph.graph['type'] = 'dt'
    
    return deltri_graph

def get_mst_graph(points):
    points = np.array(points)
    coords = [{"pos":pt} for pt in points]
    tri = Delaunay(points)
    deltri_graph = nx.Graph()
    deltri_graph.add_nodes_from(zip(range(len(points)), coords))
    edge_list = []
    for (i,j,k) in tri.simplices:
        edge_list.extend([(i,j),(j,k),(k,i)])    
    deltri_graph.add_edges_from(edge_list)
    for edge in deltri_graph.edges:
        n1, n2 = edge
        pt1 = deltri_graph.nodes[n1]['pos'] 
        pt2 = deltri_graph.nodes[n2]['pos']
        edge_wt = np.linalg.norm(pt1-pt2)
        deltri_graph.edges[n1,n2]['weight'] = edge_wt

    mst_graph = (
        nx
        .algorithms
        .tree
        .mst
        .minimum_spanning_tree(
            deltri_graph, algorithm='kruskal'
        )
    )
    mst_graph.graph['type'] = 'mst'
    
    return mst_graph

def get_gabriel_graph(points):
    points = np.array(points)
    coords = [{"pos":pt} for pt in points]
    gabriel = nx.Graph()
    gabriel.add_nodes_from(zip(range(len(points)), coords))
    vor = Voronoi(points)
    center = vor.points.mean(axis=0)
    
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        if v2<0:
            v1, v2 = v2, v1
        if v1 >= 0: # bounded Voronoi edge
            if intersect(vor.points[p1], vor.points[p2],
                         vor.vertices[v1], vor.vertices[v2]):
                gabriel.add_edge(p1,p2)
            continue
        elif v2 >= 0: # one-sided unbounded Voronoi edge
            # compute "unbounded" edge
            p1p2 = vor.points[p2] - vor.points[p1]
            p1p2 /= np.linalg.norm(p1p2)
            normal = np.array([-p1p2[1], p1p2[0]])

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(
                np.dot(midpoint - center, normal)
            ) * normal
            length = 2 * max(
                np.linalg.norm(vor.points[p1]-vor.vertices[v2]),
                np.linalg.norm(vor.points[p2]-vor.vertices[v2])
            )
            far_point = vor.vertices[v2] + direction * length
            
            if intersect(vor.points[p1], vor.points[p2],
                         vor.vertices[v2], far_point):
                gabriel.add_edge(p1,p2)
        elif v2 < 0: # two-sided unbounded Voronoi edge
            gabriel.add_edge(p1,p2)
    gabriel.graph['type'] = 'gabriel'
    
    return gabriel

def get_urquhart_graph(points):
    points       = np.array(points)
    coords       = [{"pos":pt} for pt in points]
    tri          = Delaunay(points)
    urq_graph = nx.Graph()

    urq_graph.add_nodes_from(zip(range(len(points)), coords))

    edge_list = []
    longest_edge_list = []
    for (i,j,k) in tri.simplices:
        edges = [(i,j),(j,k),(k,i)]
        norms = [np.linalg.norm(points[j]-points[i]),
                 np.linalg.norm(points[k]-points[j]),
                 np.linalg.norm(points[i]-points[k])]
        zipped = zip(edges,norms)
        sorted_edges = sorted(zipped, key = lambda t: t[1])
        longest_edge_list.append(sorted_edges[2][0])
        edge_list.extend([(i,j),(j,k),(k,i)])    
    urq_graph.add_edges_from( edge_list )
    urq_graph.remove_edges_from( longest_edge_list )
     
    total_weight_of_edges = 0.0
    for edge in urq_graph.edges:
        n1, n2 = edge
        pt1 = urq_graph.nodes[n1]['pos'] 
        pt2 = urq_graph.nodes[n2]['pos']
        edge_wt = np.linalg.norm(pt1-pt2)
        urq_graph.edges[n1,n2]['weight'] = edge_wt
        total_weight_of_edges = total_weight_of_edges + edge_wt 
    urq_graph.graph['weight'] = total_weight_of_edges
    urq_graph.graph['type']   = 'urq'
    
    return urq_graph

def get_bitonic_tour(points):
    points = perturb_pts(np.array(points))
    points = sorted(points , key=lambda k: [k[0], k[1]])
    coords = [{"pos":pt} for pt in points]
    bitonic_tour = nx.Graph()
    bitonic_tour.add_nodes_from(zip(range(len(points)), coords))
    n = len(points)
    
    # records lengths of latest partial path
    min_lengths = [0, np.linalg.norm(points[0]-points[1])]
    # records partial bitonic paths at each iteration l
    partial_bitonic_path_edges = {1:[[1,0]]}
    for l in range(2,n):
        path_values = []
        for i in range(2,l+1):
            # record lengths of candidate paths at the l-th step
            path_values.append(
                np.linalg.norm(points[l]-points[i-2]) +
                min_lengths[i-1] +
                sum(
                    [
                        np.linalg.norm(points[k]-points[k-1])
                        for k in range(i,l)
                    ]
                )
            )
        # determine length and index of shortest candidate path
        path_lngth, idx = min(
            (val, idx)
            for (idx, val) in enumerate(path_values)
        )
        min_lengths = min_lengths + [path_lngth]
        # update latest partial bitonic path
        partial_bitonic_path_edges[l] = (
            partial_bitonic_path_edges[idx+1] +
            [[l,idx]] +
            [[k-1,k] for k in range(idx+2,l)]
        )
    bitonic_tour_edges = partial_bitonic_path_edges[n-1] + [[n-2,n-1]]
    bitonic_tour.add_edges_from(bitonic_tour_edges)

    total_weight_of_edges = 0.0
    for edge in bitonic_tour.edges:
        n1, n2 = edge
        pt1 = bitonic_tour.nodes[n1]['pos'] 
        pt2 = bitonic_tour.nodes[n2]['pos']
        edge_wt = np.linalg.norm(pt1-pt2)
        bitonic_tour.edges[n1,n2]['weight'] = edge_wt
        total_weight_of_edges = total_weight_of_edges + edge_wt 
    bitonic_tour.graph['weight'] = total_weight_of_edges
    bitonic_tour.graph['type']   = 'bitonic'
    
    return bitonic_tour

def get_onion_graph(points):
    from scipy.spatial import ConvexHull
    points = np.asarray(points)   
    points = sorted(points , key=lambda k: [k[0], k[1]])  
    points_tmp = points.copy()
    numpts = len(points)
    onion_graph = nx.Graph()
    numpts_proc = -1

    def circular_edge_zip(xs):
        xs = list(xs)
        if len(xs) in [0,1] :
            zipl = []
        elif len(xs) == 2 :
            zipl = [(xs[0],xs[1])]
        else:
            zipl = list(zip(xs,xs[1:]+xs[:1]))
        return zipl

    while len(points_tmp) >= 3:
        hull = ConvexHull(points_tmp)
        pts_on_hull = [points_tmp[i] for i in hull.vertices]
        coords = [{"pos":pt} for pt in pts_on_hull]
        new_node_idxs = range(
            numpts_proc + 1,
            numpts_proc + len(hull.vertices) + 1
        )
        onion_graph.add_nodes_from(zip(new_node_idxs, coords))
        onion_graph.add_edges_from(circular_edge_zip(new_node_idxs))
        numpts_proc = numpts_proc + len(hull.vertices)
        rem_pts_idxs = list(
            set(range(len(points_tmp))) - set(hull.vertices)
        ) 
        points_tmp = [ points_tmp[idx] for idx in rem_pts_idxs ]
        coords = [{"pos":pt} for pt in points]

    if len(points_tmp) == 2:
        p, l = numpts_proc+1, numpts_proc+2
        onion_graph.add_node(p)
        onion_graph.add_node(l)
        onion_graph.nodes[p]['coods'] = points_tmp[0]
        onion_graph.nodes[l]['coods'] = points_tmp[1]
        onion_graph.add_edge(p,l)
    elif len(points_tmp) == 1:
        l = numpts_proc+1 
        onion_graph.add_node(l)
        onion_graph.nodes[l]['cood'] = points_tmp[0]
 
    onion_graph.graph['type'] = 'onion'
    return onion_graph

##### Generate Distance matrix ##### 
def generate_distance_matrix(pts, metric, mode):
    N   = len(pts)
    t = 0 if mode=='tour' else 1
    if metric=='inf':
        D   = np.zeros((N+t,N+t))
        for i in range(N):
            for j in range(N):
                D[i,j] = max(abs(pts[i]-pts[j]))
        return D
    else:
        D   = np.zeros((N+t,N+t))
        for i in range(N):
            for j in range(N):
                D[i,j] = np.linalg.norm(
                    pts[i]-pts[j],
                    ord=float(metric)
                )
    return D

#### Write distance matrix to file ####
def write_distance_matrix_to_file(D,fname, dscale = 10000):
    with open(fname, 'w') as file:
        numrows, numcols = D.shape[0], D.shape[1]
        assert numrows == numcols, "row length must equal column length"

        file.write(
            "NAME: sampleinstance\n"
            "TYPE: TSP\n"
            f"COMMENT: Distance matrix given; scaling factor {dscale}\n"
            f"DIMENSION: {numrows}\n"
            "EDGE_WEIGHT_TYPE: EXPLICIT\n"
            "EDGE_WEIGHT_FORMAT: FULL_MATRIX\n"
            "EDGE_WEIGHT_SECTION\n"
        )
        
        # distances must be integers. so scaling factor is used
        for i in range(numrows):
            for j in range(numcols):
                file.write(f'{int(dscale*D[i,j])} \t')
            file.write('\n')
        file.write('EOF')

#### Solve with Concorde from file ####
def solve_tsp_from_file(fname):
    solver   = TSPSolver.from_tspfile(fname)
    solution = solver.solve()
    return solution

#### Concorde TSP for tour/path for any metric ####
def get_tsp_graph(points, mode, metric='2', typ=None):
    points = np.array(points)
    n = len(points)
    coords = [{"pos":pt} for pt in points]
    tsp_graph = nx.Graph()
    tsp_graph.add_nodes_from(zip(range(len(points)), coords))
    if n == 3:
        tsp_graph.add_edges_from([[0,1],[1,2],[2,0]])
        tsp_graph.graph['type'] = typ
        tsp_graph.graph['weight'] = 0.0
        for n1, n2 in tsp_graph.edges:
            pt1 = tsp_graph.nodes[n1]['pos'] 
            pt2 = tsp_graph.nodes[n2]['pos']
            edge_wt = np.linalg.norm(pt1-pt2)
            tsp_graph.edges[n1,n2]['weight'] = edge_wt
            tsp_graph.graph['weight'] += edge_wt 
        return tsp_graph

    cwd = os.getcwd()
    new_wd = os.path.join(cwd, 'plot/tsp-wd/')
    if not os.path.isdir(new_wd):
        os.makedirs(new_wd)
    os.chdir(new_wd)

    scaling_factor=10000
    # Solve correct problem
    if metric=='2' and mode=='tour':
        xs = [int(scaling_factor*pt[0]) for pt in points]
        ys = [int(scaling_factor*pt[1]) for pt in points]
        solver = TSPSolver.from_data(xs, ys, norm='EUC_2D', name=None)
        solution = solver.solve()
    else:
        D = generate_distance_matrix(points, metric=metric, mode=mode)
        write_distance_matrix_to_file(
            D,
            fname='instance.tsp',
            dscale=1000000
        )
        solution = solve_tsp_from_file('instance.tsp')

    # get solution inds and add nodes
    idxs_along_tsp = list(solution.tour)

    # add correct edges to graph
    if mode=='tour':
        edge_list = (
            list(zip(idxs_along_tsp, idxs_along_tsp[1:])) +
            [(idxs_along_tsp[-1],idxs_along_tsp[0])]
        )
        tsp_graph.add_edges_from(edge_list)
    elif mode=='path':
        dummy_node_ind = idxs_along_tsp.index(n)
        if dummy_node_ind == 0:
            path = idxs_along_tsp[1:]
        else:
            path = (
                idxs_along_tsp[dummy_node_ind+1:] +
                idxs_along_tsp[:dummy_node_ind]
            )
        for i in range(0,n-1):
            tsp_graph.add_edge(path[i], path[i+1])

    total_weight_of_edges = 0.0
    for edge in tsp_graph.edges:
        n1, n2 = edge
        pt1 = tsp_graph.nodes[n1]['pos'] 
        pt2 = tsp_graph.nodes[n2]['pos']
        edge_wt = np.linalg.norm(pt1-pt2)
        tsp_graph.edges[n1,n2]['weight'] = edge_wt
        total_weight_of_edges = total_weight_of_edges + edge_wt 
    tsp_graph.graph['weight'] = total_weight_of_edges
    if typ is not None:
        tsp_graph.graph['type'] = 'poly'
    else:
        tsp_graph.graph['type'] = 'concorde'

    for file in os.listdir(os.getcwd()):
        os.remove(os.path.join(os.getcwd(), file))
    os.chdir(cwd)
    os.rmdir(new_wd)

    return tsp_graph

#### Order-k Delaunay Graph ####
def get_kdelaunay_graph(points, order):
    """
    Returns the k-Delaunay graph.
    The k-Delaunay graph (a.k.a., the order k Delaunay graph)
    contains an edge ij if and only if there exists a disk
    containing i and j and at most k additional points. See
    that the 0-Delaunay graph is the standard Delaunay graph.
    Moreover, for any natural k, k-Delaunay subseteq (k+1)-
    Delaunay.

    Args:
        points (list):
            List (len n) of lists (len 2) of floats representing
            coordinates.
        order (int):
            The order (k) of the graph to be computed.
    """
    assert (order >= 0) and isinstance(order, int)
    # compute k_delaunay graph
    # we use 0-Delaunay = Delaunay triangulation, whereas those
    # who implemented OrderKDelaunay use 1-Delaunay = Delaunay.
    # As such, we increment the order to match the OrderKDelaunay
    # software's convention.
    k_delaunay = OrderKDelaunay(points, order + 1)
    k_delaunay_edges = []

    # vertex sets on which cliques exist
    vertex_idxs = [
        set(np.array(cell_list).flatten())
        for cell_list in k_delaunay.diagrams_cells[-1]
    ]

    for clique_idxs in vertex_idxs:
        for pair in it.combinations(clique_idxs, 2):
            k_delaunay_edges.append(list(pair))

    k_delaunay_edges = set(
        [
            tuple(sorted(edge))
            for edge in k_delaunay_edges
        ]
    )

    k_delaunay = nx.Graph()
    points = np.array(points)
    n = len(points)
    coords = [{"pos":pt} for pt in points]
    k_delaunay.add_nodes_from(zip(range(len(points)), coords))
    edges = [
        (v, w, np.linalg.norm(points[v] - points[w]))
        for (v, w) in k_delaunay_edges
    ]
    k_delaunay.add_weighted_edges_from(edges)
    k_delaunay.graph['type'] = 'kdel'

    return k_delaunay
