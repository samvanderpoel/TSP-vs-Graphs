# For the momement this module contains a set of examples to show that sometimes k successive edges 
# of the TSP can be non-delaunay (for arbitrary k). 
# the list of functions to programmatically generate 
# counter-examples can grow in the future
import sys, os, random, time, colorama, yaml
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D



def get_pts_along_segment(p,q,N):
    """ Here p and q are the endpoints of the segment. 
    The goal is to place N equidistant points (*NOT* including 
    the endpoints p and q). This is a useful routine while 
    constructing counter-examples for the TSP. The points returned 
    lie strictly in the interior of the line segment in R^2 
    formed by p,q
    """
    px,py = p
    qx,qy = q

    xs = np.linspace(px,qx,N)
    ys = np.linspace(py,qy,N)
    
    pts = np.asarray([np.asarray([x,y]) for i,(x,y) in enumerate(zip(xs,ys)) if i not in [0,N-1]])
    return pts

def tack_at_begin(p,pts):
    """ Place point p at the beginning of the array
    """
    pts_x, pts_y = pts 
    pts_x  = [p[0]] + pts_x
    pts_y  = [p[1]] + pts_y
    
    pts = np.asarray(zip(pts_x,pts_y))
    return pts


def tack_at_end(pts,q):
    """ Place point q at the end of the array
    """
    pts_x, pts_y = pts 
    pts_x  =  pts_x + [q[0]]
    pts_y  =  pts_y + [q[1]]
    
    pts = np.asarray(zip(pts_x,pts_y))
    return pts


def sandwich_between(p,pts,q):
    """ Sandwich the list of points between p and q
    """
    pts_x, pts_y = pts 
    pts_x  = [p[0]]  + pts_x + [q[0]] 
    pts_y  = [p[1]]  + pts_y + [q[1]]
    
    pts = np.asarray(zip(pts_x,pts_y))
    return pts


def get_yrefl(p):
    """ Reflect point along Y axis
    """
    return np.asarray([-p[0],p[1]])


def get_xrefl(p):
    """ Reflect point along X axis
    """
    return np.asarray([p[0],-p[1]])

def get_tesla():

   A = np.asarray((0.0  ,1.0)) # do not reflect
   B = np.asarray((2.0  ,2.8)) # do not reflect
   C = np.asarray((4.0  ,2.8))
   D = np.asarray((3.5  ,0.8))
   E = np.asarray((2.0  ,0.9))
   F = np.asarray((3.0 ,1.0))
   G = np.asarray((3.0  ,2.0))
   H = np.asarray((2.0  ,2.0))
   I = np.asarray((0.0  ,0.0))                 

   # Reflect the outline points
   ref_pts = []
   for pt in [C,D,E,F,G,H,I]:
       ref_pts.append(get_yrefl(pt))

   AB = get_pts_along_segment(A,B,N=10)
   BC = get_pts_along_segment(B,C,N=10)
   CD = get_pts_along_segment(C,D,N=10)
   DE = get_pts_along_segment(D,E,N=10)
   EF = get_pts_along_segment(E,F,N=10)
   FG = get_pts_along_segment(F,G,N=10)
   GH = get_pts_along_segment(G,H,N=10)                                          

   # Reflect the interior segment points
   for arr in [AB,BC,CD,DE,EF,FG,GH]:
       for pt in arr:
           ref_pts.append(get_yrefl(pt))

   # xs and ys are the final arrays which will contain 
   # the x and y coordinate of the Tesla example
   xs = [A[0],B[0],C[0],D[0],E[0],F[0],G[0],H[0],I[0]] 
   ys = [A[1],B[1],C[1],D[1],E[1],F[1],G[1],H[1],I[1]] 

   for arr in [AB,BC,CD,DE,EF,FG,GH]:
       for pt in arr:
           xs = xs + [pt[0]]
           ys = ys + [pt[1]]
    
   for pt in ref_pts:
       px, py = pt
       xs = xs + [px]
       ys = ys + [py]

   return xs,ys 


def write_to_yaml_file(data, dir_name, file_name):
   with open(dir_name + '/' + file_name, 'w') as outfile:
          yaml.dump( data, outfile, default_flow_style = False)


# xs, ys = get_tesla()
# data = {}
# data['points'] = [[float(x),float(y)] for (x,y) in zip(xs,ys)]
# write_to_yaml_file(data, '.', 'tesla.yaml')


def get_crab2():
    A=np.asarray((0    ,1.4)) # do not reflect
    B=np.asarray((-1.2 ,0.2))
    C=np.asarray((-1.5 ,0.2))
    D=np.asarray((-1.5 ,-0.5))
    E=np.asarray((-0.8 ,-0.3))
    F=np.asarray((-1   ,0))
    G=np.asarray((0    ,0.5)) # do not reflect


    AB = get_pts_along_segment(A,B,N=10).tolist()
    BC = get_pts_along_segment(B,C,N=10).tolist()
    CD = get_pts_along_segment(C,D,N=10).tolist()
    DE = get_pts_along_segment(D,E,N=10).tolist()
    EF = get_pts_along_segment(E,F,N=10).tolist()

    origpts = [B,C,D,E,F] + AB + BC + CD + DE + EF
    refpts =  [ np.asarray(get_yrefl(pt)) for pt in origpts ]


    total_pts = [A]   +  [G] + origpts + refpts 

    xs = [x for (x,y) in total_pts]
    ys = [y for (x,y) in total_pts]


    #fig,ax = plt.subplots()
    #ax.set_aspect(1.0)
    #ax.plot(xs,ys,'o')
    #plt.show()
    return xs, ys

def get_crab3():
    
    A=np.asarray([ 1         , 1.0  ])
    B=np.asarray([ np.sqrt(2), 0.0  ])
    C=np.asarray([ np.sqrt(2), -0.3 ])
    D=np.asarray([ 1.0       , 0.0  ])
    E=np.asarray([ 0.5       , 0.5  ])
    G=np.asarray([ 0.20      , 0.01 ])
    H=np.asarray([ 0         , 0.95    ])


    AH=get_pts_along_segment(A,H,N=10).tolist()
    AB=get_pts_along_segment(A,B,N=10).tolist()
    BC=get_pts_along_segment(B,C,N=5).tolist()
    CG=get_pts_along_segment(C,G,N=30).tolist()
    GD=get_pts_along_segment(G,D,N=30).tolist()


    orig_pts = [A,B,C,D,E,G] + AH + AB + BC + CG + GD
    ref_pts = [get_yrefl(pt) for pt in orig_pts]
    
    total_pts = [H] + orig_pts + ref_pts 


    xs = [x for (x,y) in total_pts]
    ys = [y for (x,y) in total_pts]


    #fig,ax = plt.subplots()
    #ax.set_aspect(1.0)
    #ax.plot(xs,ys,'o')
    #plt.show()
    return xs,ys
    

xs,ys = get_crab3()
data = {}
data['points'] = [[float(x),float(y)] for (x,y) in zip(xs,ys)]
write_to_yaml_file(data, '.', 'crab3.yaml')

