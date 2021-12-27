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
    
    ax.set_xlim([xlim[0], xlim[1]])
    ax.set_ylim([ylim[0], ylim[1]])
    ax.set_aspect(1.0)
    ax.set_xticks([])
    ax.set_yticks([])
 
    patchSize  = (xlim[1]-xlim[0])/180.0

    for pt in run.points:
        ax.add_patch(mpl.patches.Circle(pt, radius = patchSize,
                     facecolor='blue', edgecolor='black'))

    ax.set_title('Points Inserted: ' + str(len(run.points)), \
                   fontdict={'fontsize':25})
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

            patchSize  = (xlim[1]-xlim[0])/180.0
                   
            ax.clear()

            for pt in run.points:
                ax.add_patch(mpl.patches.Circle(pt, radius = patchSize,
                             facecolor='blue', edgecolor='black'))

            ax.set_title('Points Inserted: ' + str(len(run.points)), \
                          fontdict={'fontsize':25})
            applyAxCorrection(ax)
            fig.canvas.draw()

    return _enterPointsHandler

def wrapperkeyPressHandler(fig,ax, run): 
    def _keyPressHandler(event):
        if event.key in ['n', 'N', 'u', 'U','m','M','o','O','g','G']: 
            numpts = int(input("\nHow many points should I generate?: ")) 
            run.clearAllStates()
            ax.cla()
            applyAxCorrection(ax)

            ax.set_xticks([])
            ax.set_yticks([])
            fig.texts = []
                                  
            if event.key in ['u', 'U'] : 
                run.points = sorted(pts_uni(numpts), key=lambda k: [k[0], k[1]])
            elif event.key in ['m', 'M']:
                nummodes   = int(input("How many modes do you want in the distribution?"))
                sigma      = float(input("What do you want the standard deviation of the local distribution around each mode to be?"))
                run.points = sorted(pts_clusnorm(numpts, numclus=nummodes , mu=0, sigma=sigma), key=lambda k: [k[0], k[1]])
            elif event.key in ['o', 'O']:
                numrings   = int(input("How many rings do you want?"))
                run.points = sorted(pts_concentric_circular_points(numpts, numrings=numrings), key=lambda k: [k[0], k[1]])
            elif event.key in ['g', 'G']:
                numrows    = int(input("How many rows do you want?"))
                run.points = sorted(pts_grid(numpts), key=lambda k: [k[0], k[1]])
            else:
                print("I did not understand that option. Please type one of `n`, `u`, `m`, `o`, `g`")

            patchSize  = (xlim[1]-xlim[0])/180

            for site in run.points:      
                ax.add_patch(mpl.patches.Circle(site, radius = patchSize, \
                             facecolor='blue',edgecolor='black' ))

            ax.set_title('Points generated: ' + str(len(run.points)), fontdict={'fontsize':20})
            fig.canvas.draw()                   
        elif event.key in ['t' or 'T']:
            tsp_graph = get_tsp_graph(run.points, mode='tour', typ='poly')
            # graph_fns = [(get_delaunay_tri_graph, 'Delaunay Triangulation (D)'), \
            #              (get_mst_graph         , 'Minimum Spanning Tree (M)'), \
            #              (get_gabriel_graph     , 'Gabriel'),\
            #              (get_urquhart_graph    , 'Urquhart') ]

            # from functools import partial
            # for k in range(1,5): 
            #     graph_fns.append((partial(get_nng_graph, k=k), str(k)+'_NNG'))

            # tbl             = PrettyTable()
            # tbl.field_names = ["Spanning Graph (G)", "G", "G \cap T", "T", "(G \cap T)/T"]
            # num_tsp_edges   = len(tsp_graph.edges)

            # for ctr, (fn_body, fn_name) in zip(range(1,1+len(graph_fns)), graph_fns):
            #     geometric_graph = fn_body(run.points)
            #     num_graph_edges = len(geometric_graph.edges)
            #     common_edges    = list_common_edges(tsp_graph, geometric_graph)
            #     num_common_edges_with_tsp = num_common_edges(tsp_graph, geometric_graph)

            #     tbl.add_row([fn_name,                 \
            #                  num_graph_edges,           \
            #                  num_common_edges_with_tsp, \
            #                  num_tsp_edges,             \
            #                  "{perc:3.2f}".format(perc=1e2*num_common_edges_with_tsp/num_tsp_edges)+ ' %' ])
                                 
            # print("Table of number of edges in indicated graph")
            # print(tbl)
            render_graph(tsp_graph, fig, ax)
            fig.canvas.draw()
        elif event.key in ['i', 'I']:                     
            algo_str = input("Enter code for the graph you need to span the points:           \n" +\
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

            # elif algo_str == 'onion':
            #     geometric_graph = get_onion_graph(run.points)

            elif algo_str == 'gab':
                geometric_graph = get_gabriel_graph(run.points)

            elif algo_str == 'urq':
                geometric_graph = get_urquhart_graph(run.points)

            elif algo_str == 'dt':
                geometric_graph = get_delaunay_tri_graph(run.points)

            # elif algo_str == 'tspincr':
            #     geometric_graph = get_tsp_incr_graph(run.points)

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

            tsp_tour = get_tsp_graph(run.points, mode='tour')
            tsp_path = get_tsp_graph(run.points, mode='path')
            n_common_edges_tour = num_common_edges(tsp_tour, geometric_graph)
            n_common_edges_path = num_common_edges(tsp_path, geometric_graph)
            print(87*"-")
            print("Number of edges in " + algo_str + " graph:", len(geometric_graph.edges))
            print("\nNumber of edges in Concorde (Euclidean) TSP tour:", len(tsp_tour.edges))
            print("Number of edges in intersection of " + algo_str + " and Concorde (Euclidean) TSP tour:", n_common_edges_tour)
            print("\nNumber of edges in Concorde (Euclidean) TSP path:", len(tsp_path.edges))
            print("Number of edges in intersection of " + algo_str + " and Concorde (Euclidean) TSP path:", n_common_edges_path)
            print(87*"-")

            ax.set_title("Graph Type: " + geometric_graph.graph['type'] + '\n Number of nodes: ' + str(len(run.points)), fontdict={'fontsize':25})
            render_graph(geometric_graph, fig, ax)
            fig.canvas.draw()    
        elif event.key in ['x', 'X']:
            patchSize  = (xlim[1]-xlim[0])/180.0
            print('Removing network edges from canvas')
            ax.cla()                          
            applyAxCorrection(ax)
            ax.set_xticks([])
            ax.set_yticks([])                        
            fig.texts = []
            for pt in run.points:
                ax.add_patch(mpl.patches.Circle(pt, radius = patchSize,
                             facecolor='blue', edgecolor='black'))
            fig.canvas.draw()
        elif event.key in ['c', 'C']: 
            run.clearAllStates()
            ax.cla()
                                                  
            applyAxCorrection(ax)
            ax.set_xticks([])
            ax.set_yticks([])
                                                     
            fig.texts = []
            fig.canvas.draw()
    return _keyPressHandler

def num_common_edges(g1, g2):
    num_common = 0
    for e in g2.edges():
        if g1.has_edge(*e):
            num_common += 1
    return num_common

def shift_and_scale_to_unit_square(points):
     
    # make all coordinates positive by shifting origin
    points = [np.asarray(pt) for pt in points]
    min_x  = min([x for (x,_) in points])
    min_y  = min([y for (_,y) in points])
    m      = min(min_x, min_y)
    origin = np.asarray([m,m])

    # scale to unit-square
    points = [pt - origin for pt in points]
    max_x  = max([x for (x,_) in points])
    max_y  = max([y for (_,y) in points])
    scale  = max(max_x,max_y)
    points = [pt/scale for pt in points]

    return points

def applyAxCorrection(ax):
    ax.set_xlim([xlim[0], xlim[1]])
    ax.set_ylim([ylim[0], ylim[1]])
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
    if G.graph['type'] == 'mst':
        edgecol = 'g'
    elif G.graph['type'] == 'onion':
        edgecol = 'gray'
    elif G.graph['type'] == 'gabriel':
        edgecol = (153/255, 102/255, 255/255)
    elif G.graph['type'] == 'urq':
        edgecol = (255/255, 102/255, 153/255)
    elif G.graph['type'] in ['conc','pytsp']:
        edgecol = 'r'
    elif G.graph['type'] == 'dt':
        edgecol = 'b'
    elif G.graph['type'][-3:] == 'nng':
        edgecol = 'm'
    elif G.graph['type'] == 'bitonic':
        edgecol = (153/255, 0/255, 0/255)
    elif G.graph['type'] == 'pypath':
        edgecol = (255/255, 0/255, 0/255)
    elif G.graph['type'] == 'concorde':
        edgecol = (255/255 , 99/255, 71/255)
    elif G.graph['type'] =='kdel':
        edgecol = (255/255,0/255,255/255)
    if G.graph['type'] not in ['poly']:
          #for elt in list(G.nodes(data=True)):
          #     print(elt)
        for  (nidx1, nidx2) in G.edges:
            x1, y1 = G.nodes[nidx1]['pos']
            x2, y2 = G.nodes[nidx2]['pos']
            ax.plot([x1,x2],[y1,y2],'-', color=edgecol, linewidth=0.8)
    else:
        from networkx.algorithms.traversal.depth_first_search import dfs_edges
        node_coods = []
        for (nidx1, nidx2) in dfs_edges(G):
            node_coods.append(G.nodes[nidx1]['pos'])
            node_coods.append(G.nodes[nidx2]['pos'])

        node_coods = np.asarray(node_coods)

        # mark the nodes
        xs = [pt[0] for pt in node_coods ]
        ys = [pt[1] for pt in node_coods ]
        ax.scatter(xs,ys)

        polygon = Polygon(node_coods, closed=True, alpha=0.40, \
                          facecolor=(72/255,209/255,204/255,0.4), \
                          edgecolor='k', linewidth=0.4)
        ax.add_patch(polygon)

    ax.axis('off') # turn off box surrounding plot
    fig.canvas.draw()

if __name__=='__main__':
    main()
