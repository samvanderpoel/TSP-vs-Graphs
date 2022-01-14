import yaml
import numpy as np

import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

from cloud_funcs import *
from graph_funcs import *

xlim, ylim = [0,1], [0,1]
compare_graphs = False
patchSize  = (xlim[1]-xlim[0])/250
edgewwidth = 1.0

class TSPNNGInput:
    def __init__(self, points=[]):
        self.points            = points
    def clearAllStates (self):
        self.points = []
    def generate_geometric_graph(self,graph_code):
        pass

def main():
    if len(sys.argv)>=2 and sys.argv[1] == '--file':
        filename = sys.argv[2]
        with open(filename, 'r') as stream:
            try:
                file_data = yaml.safe_load(stream)
                points    = [np.asarray(pt) for pt in file_data['points']]

                print("\nPoints read from the input file are ")
                for pt in points:
                    print(" ",pt)
                print("\nOpening interactive canvas with provided input points")
                points = shift_and_scale_to_unit_square(points)
                run_handler(points=points)

            except yaml.YAMLError as exc:
                print(exc)
    elif len(sys.argv)>=2 and sys.argv[1] == '--tsplibinstance':
        
        tsplibfiledir=os.getcwd()
        filename = sys.argv[2]
        filename = tsplibfiledir + filename + '.yml'
        with open(filename, 'r') as stream:
            try:
                file_data = yaml.load(stream,Loader=yaml.Loader)
                points=file_data['points']
                points=[np.asarray(pt) for pt in points]
                   
                xmax = max([pt[0] for pt in points])
                ymax = max([pt[1] for pt in points])

                print("Scaling TSPLIB points to lie in unit-square")

                # The eps is for increasing the scaling factor slightly so 
                # that all points in the data-set falls inside unit box
                eps    = 1.0
                M      = max(xmax,ymax) + eps
                points = [pt/M for pt in points]

                print("\nPoints read from the input file are ")
                for pt in points:
                    print(" ",pt)
                print("\nOpening interactive canvas with scaled input points from TSPLIB")
                run_handler(points=points)

            except yaml.YAMLError as exc:
                print(exc)

    elif len(sys.argv)>=2 and sys.argv[1] == '--interactive':
        run_handler()
    else:
        print("Please run as one of:")
        print("-->   python src/main.py --interactive")
        print("-->   python src/main.py --file <file.yaml>")
        print("-->   python src/main.py --tsplibinstance <instancename>")
        sys.exit()

def run_handler(points=[]):
    fig, ax =  plt.subplots()
    run = TSPNNGInput(points=points)
    
    buff = max(xlim[1] - xlim[0], ylim[1] - ylim[0]) / 10
    ax.set_xlim([xlim[0] - buff, xlim[1] + buff])
    ax.set_ylim([ylim[0] - buff, ylim[1] + buff])
    ax.set_aspect(1.0)
    ax.set_xticks([])
    ax.set_yticks([])

    for pt in run.points:
        ax.add_patch(mpl.patches.Circle(pt, radius = patchSize,
                     facecolor='black', edgecolor='black', zorder=2.5))

    ax.set_title('Points Inserted: ' + str(len(run.points)), \
                   fontdict={'fontsize':12})
    applyAxCorrection(ax)
    fig.canvas.draw()

    mouseClick = wrapperEnterRunPointsHandler(fig,ax, run)
    fig.canvas.mpl_connect('button_press_event' , mouseClick)
      
    keyPress = wrapperkeyPressHandler(fig,ax, run)
    fig.canvas.mpl_connect('key_press_event', keyPress)
    plt.show()

def wrapperEnterRunPointsHandler(fig, ax, run):
    def _enterPointsHandler(event):
        if event.name      == 'button_press_event' and \
           (event.button   == 1)                   and \
            event.dblclick == True                 and \
            event.xdata  != None                   and \
            event.ydata  != None:

            newPoint = np.asarray([event.xdata, event.ydata])
            run.points.append( newPoint  )
            print("You inserted ", newPoint)
                   
            ax.clear()

            for pt in run.points:
                ax.add_patch(mpl.patches.Circle(pt, radius = patchSize,
                             facecolor='black', edgecolor='black', zorder=2.5))

            ax.set_title('Points Inserted: ' + str(len(run.points)), \
                          fontdict={'fontsize':12})
            applyAxCorrection(ax)
            fig.canvas.draw()

    return _enterPointsHandler

def wrapperkeyPressHandler(fig,ax, run):

    def _keyPressHandler(event):
        if event.key in ['o', 'O']:
            global compare_graphs
            compare_graphs = True
            print('Comparison of graphs with Euclidean TSP activated.')
        elif event.key in ['n', 'N']:

            run.clearAllStates()
            ax.cla()
            applyAxCorrection(ax)
            ax.set_xticks([])
            ax.set_yticks([])
            fig.texts = []

            numpts = int(input("\nHow many points should I generate?: "))
            smpl_str = input("\nEnter code for sampling type:                               \n" +\
                             "(usqr)      Uniform on the unit square                        \n" +\
                             "(uball)     Uniform on the unit disk                          \n" +\
                             "(bivar)     Bivariate normal                                  \n" +\
                             "(clus)      Bivariate normal at several modes in unit square  \n" +\
                             "(ann)       Non-random points on concentric circles           \n" +\
                             "(annrand)   Random points in an annulus                       \n" +\
                             "(corners)   Uniform distrs. centered at corners of a square   \n" +\
                             "(grid)      Random points on a grid (having 1.3*N gridpoints) \n" +\
                             "(spokes)    N/2 points at (U[0,1], 0.5) and (0.5, U[0,1])     \n" +\
                             "(concen)    Non-random concentric circular points             \n")
            smpl_str = smpl_str.lstrip()
            if smpl_str == 'usqr':
                run.points = sorted(pts_uni(numpts), key=lambda k: [k[0], k[1]])
            elif smpl_str == 'uball':
                run.points = sorted(pts_ball(numpts, r=1), key=lambda k: [k[0], k[1]])
            elif smpl_str == 'bivar':
                sigma      = float(input("Enter standard deviation (typical value: 0.05): "))
                run.points = sorted(pts_normal(numpts, mu=0.5, sigma=sigma), key=lambda k: [k[0], k[1]])
            elif smpl_str == 'clus':
                nummodes   = int(input("Enter number of modes: "))
                sigma      = float(input("Enter standard deviation about each mode (typical value: 0.05): "))
                run.points = sorted(pts_clusnorm(numpts, numclus=nummodes,
                                                 mu=0, sigma=sigma), key=lambda k: [k[0], k[1]])
            elif smpl_str == 'ann':
                run.points = sorted(pts_annulus(numpts, r_inner=1.0, r_outer=2.0,
                                    numrings=10, theta=np.pi/6), key=lambda k: [k[0], k[1]])
            elif smpl_str == 'annrand':
                run.points = sorted(pts_annulus_random(numpts, r_inner=1.0, r_outer=2.0),
                                    key=lambda k: [k[0], k[1]])
            elif smpl_str == 'corners':
                run.points = sorted(pts_corners(numpts, numpolyverts=4, s=0.7),
                                    key=lambda k: [k[0], k[1]])
            elif smpl_str == 'grid':
                run.points = sorted(pts_grid(numpts), key=lambda k: [k[0], k[1]])
            elif smpl_str == 'spokes':
                run.points = sorted(pts_spokes(numpts), key=lambda k: [k[0], k[1]])
            elif smpl_str == 'concen':
                numrings = int(input("Enter number of concentric rings: "))
                run.points = sorted(pts_concentric_circular_points(numpts, numrings),
                                    key=lambda k: [k[0], k[1]])

            run.points = shift_and_scale_to_unit_square(run.points)
            for point in run.points:     
                ax.add_patch(mpl.patches.Circle(point, radius = patchSize, \
                             facecolor='black',edgecolor='black', zorder=2.5))
            ax.set_title('Points generated: ' + str(len(run.points)), fontdict={'fontsize':12})
            applyAxCorrection(ax)
            fig.canvas.draw()

        elif event.key in ['t' or 'T']:
            tsp_graph = get_tsp_graph(run.points, mode='tour', typ='poly')
            render_graph(tsp_graph, fig, ax)
            fig.canvas.draw()
        elif event.key in ['i', 'I']:                     
            algo_str = input("\nEnter code for the graph you need to span the points:         \n" +\
                             "(knng)      k-Nearest Neighbor Graph                            \n" +\
                             "(mst)       Minimum Spanning Tree                               \n" +\
                             "(onion)     Onion                                               \n" +\
                             "(gab)       Gabriel Graph                                       \n" +\
                             "(urq)       Urquhart Graph                                      \n" +\
                             "(dt)        Delaunay Triangulation                              \n" +\
                             "(kdel)      Order-k Delaunay                                    \n" +\
                             "(bitonic)   Bitonic tour                                        \n" +\
                             "(concorde)  Tour or path in any metric using Concorde           \n")
            algo_str = algo_str.lstrip()

            if algo_str == 'knng':
                k = int(input('>> Enter value of k: '))
                metric = input('>> Enter metric (inf for L_infty metric): ')
                geometric_graph = get_nng_graph(run.points, k=k, metric=metric)

            elif algo_str == 'mst':
                geometric_graph = get_mst_graph(run.points)

            elif algo_str == 'onion':
                geometric_graph = get_onion_graph(run.points)

            elif algo_str == 'gab':
                geometric_graph = get_gabriel_graph(run.points)

            elif algo_str == 'urq':
                geometric_graph = get_urquhart_graph(run.points)

            elif algo_str == 'dt':
                geometric_graph = get_delaunay_tri_graph(run.points)

            elif algo_str == 'bitonic':
                geometric_graph = get_bitonic_tour(run.points)

            elif algo_str == 'concorde':
                mode = input('>> Enter tour or path: ')
                metric = input('>> Enter metric (inf for L_infty metric): ')
                geometric_graph = get_tsp_graph(run.points, metric=metric, mode=mode)

            elif algo_str == 'kdel':
                k = input('>> Enter order: ')
                geometric_graph = get_kdelaunay_graph(run.points, order=int(k))

            # elif algo_str in ['d','D']:
            #     build_delaunay_forest(run.points,stopnum=10) 
            #     sys.exit()

            # elif algo_str in ['v','V']:
            #     render_max_disp_graph_hierarchy(run.points,graphfn=get_mst_graph ,stopnum=4)


            else:
                print("I did not recognize that option.")
                geometric_graph = None

            ax.set_title("Graph Type: " + geometric_graph.graph['type'] + \
                         "\n Number of nodes: " + str(len(run.points)), fontdict={'fontsize':12})
            render_graph(geometric_graph, fig, ax)
            fig.canvas.draw()

            if compare_graphs:
                tsp_tour = get_tsp_graph(run.points, mode='tour')
                tsp_path = get_tsp_graph(run.points, mode='path')
                n_common_edges_tour = num_common_edges(tsp_tour, geometric_graph)
                n_common_edges_path = num_common_edges(tsp_path, geometric_graph)
                print(87*"-")
                print("Number of edges in " + algo_str + " graph:", len(geometric_graph.edges))
                print("\nNumber of edges in Concorde (Euclidean) TSP tour:", len(tsp_tour.edges))
                print("Number of edges in intersection of " + algo_str + \
                      " and Concorde (Euclidean) TSP tour:", n_common_edges_tour)
                print("\nNumber of edges in Concorde (Euclidean) TSP path:", len(tsp_path.edges))
                print("Number of edges in intersection of " + algo_str + \
                      " and Concorde (Euclidean) TSP path:", n_common_edges_path)
                print(87*"-")   
        elif event.key in ['x', 'X']:
            print('Removing network edges from canvas')
            ax.cla()                          
            applyAxCorrection(ax)
            ax.set_xticks([])
            ax.set_yticks([])                        
            fig.texts = []
            for pt in run.points:
                ax.add_patch(mpl.patches.Circle(pt, radius = patchSize,
                             facecolor='black', edgecolor='black', zorder=2.5))
            fig.canvas.draw()
        elif event.key in ['c', 'C']: 
            run.clearAllStates()
            ax.cla()
                                                  
            applyAxCorrection(ax)
            ax.set_xticks([])
            ax.set_yticks([])
                                                     
            fig.texts = []
            fig.canvas.draw()
        elif event.key in ['e','E']:
            print('Exporting figure to jpg.')
            fig.savefig('plot/mpl-savefig.jpg', dpi=500)
    return _keyPressHandler

def num_common_edges(g1, g2):
    num_common = 0
    for e in g2.edges():
        if g1.has_edge(*e):
            num_common += 1
    return num_common

def shift_and_scale_to_unit_square(points):
    """
    Shifts and scales points to the unit square
    """
    points = [np.asarray(pt) for pt in points]
    min_x, max_x = min([x for (x,_) in points]), max([x for (x,_) in points])
    min_y, max_y = min([y for (_,y) in points]), max([y for (_,y) in points])
    x_range = max_x - min_x
    y_range = max_y - min_y
    if x_range > y_range:
        xtrans = -min_x
        ymid = min_y + y_range/2
        ytrans = x_range/2 - ymid
        scale_fac = x_range
    else:
        ytrans = -min_y
        xmid = min_x + x_range/2
        xtrans = y_range/2 - xmid
        scale_fac = y_range
    trans_pts = [pt + np.asarray([xtrans, ytrans]) for pt in points]
    new_pts = [pt/scale_fac for pt in trans_pts]
    return new_pts

def applyAxCorrection(ax):
    buff = max(xlim[1] - xlim[0], ylim[1] - ylim[0]) / 10
    ax.set_xlim([xlim[0] - buff, xlim[1] + buff])
    ax.set_ylim([ylim[0] - buff, ylim[1] + buff])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off') # turn off box surrounding plot
    ax.set_aspect(1.0)

def clearPatches(ax):
    for index , patch in zip(range(len(ax.patches)), ax.patches):
        if isinstance(patch, mpl.patches.Polygon) == True:
            patch.remove()
    ax.lines[:]=[]
    applyAxCorrection(ax)

def clearAxPolygonPatches(ax):

    for index , patch in zip(range(len(ax.patches)), ax.patches):
        if isinstance(patch, mpl.patches.Polygon) == True:
            patch.remove()
    ax.lines[:]=[]
    applyAxCorrection(ax)

def render_graph(G,fig,ax):
    if G is None:
        return None
    edgecol = None
    edgecols = {'mst':'g',
                'onion':'gray',
                'gabriel':(255/255,0/255,0/255),
                'urq':(0,0,0),
                'conc':'r',
                'pytsp':'r',
                'dt':'b',
                'nng':'m',
                'bitonic':(153/255, 0/255, 0/255),
                'pypath':(255/255, 0/255, 0/255),
                'concorde':(0,255/255,255/255),
                'kdel':(255/255,0/255,255/255)}
    if G.graph['type'] in edgecols:
        edgecol = edgecols[G.graph['type']]
    if G.graph['type'] not in ['poly']:
          #for elt in list(G.nodes(data=True)):
          #     print(elt)
        for  (nidx1, nidx2) in G.edges:
            x1, y1 = G.nodes[nidx1]['pos']
            x2, y2 = G.nodes[nidx2]['pos']
            ax.plot([x1,x2],[y1,y2],'-', color=edgecol, linewidth=edgewwidth,
                    zorder = 2)
    else:
        from networkx.algorithms.traversal.depth_first_search import dfs_edges
        node_coods = []
        for (nidx1, nidx2) in dfs_edges(G):
            node_coods.append(G.nodes[nidx1]['pos'])
            node_coods.append(G.nodes[nidx2]['pos'])
        node_coods = np.asarray(node_coods)

        # mark the nodes
        # xs = [pt[0] for pt in node_coods]
        # ys = [pt[1] for pt in node_coods]
        # ax.scatter(xs, ys, s = 0.5, zorder=2.5)

        polygon = Polygon(node_coods, closed=True, alpha=0.40, \
                          facecolor=(72/255,209/255,204/255, 0.4), \
                          edgecolor='k', linewidth=0, zorder=1)
        ax.add_patch(polygon)

    applyAxCorrection(ax)
    fig.canvas.draw()

if __name__=='__main__':
    main()
