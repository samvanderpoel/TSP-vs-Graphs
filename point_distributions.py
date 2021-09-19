# This file contains methods to generate various point distributions. 
# Most of these are sourced from the paper of Jon Bentley's experimental TSP paper:
#
#       Bentley, Jon Jouis. "Fast algorithms for geometric traveling salesman problems."
#       ORSA Journal on computing 4.4 (1992): 387-411.
#
# The methods coming from Bentley's article are labaled as such.

import matplotlib.pyplot as plt
import scipy as sp
import numpy as np
import sys,os,time, random
from colorama import Fore, Style

##-------------------------------------------------------------------------
def pts_uni(numpts, xlim=[0,1], ylim=[0,1]):
    """
    Bentley #1. Uniform within the a rectangle of with specificed limits 
    on x and y coordintes. default is unit-square
    """
    xs = xlim[0] + abs(xlim[1]-xlim[0])*np.random.random(numpts)
    ys = ylim[0] + abs(ylim[1]-ylim[0])*np.random.random(numpts)
    return np.asarray(list(zip(xs,ys)))

##-------------------------------------------------------------------------
def pts_annulus(numpts, r_inner=1.0, r_outer=2.0, numrings=10, theta=np.pi/6):
    """ Place points on consecutive nested concentric circles, with points 
    on each circle differing from previous circle by a scaling and rotation. 
    All circles have the same number of points on them
    """
    numptsperring = numpts//numrings
    numptsrem     = numpts%numrings
    
    xunit = np.cos( [k * 2.0*np.pi/numptsperring  for k in range(numptsperring)] )
    yunit = np.sin( [k * 2.0*np.pi/numptsperring  for k in range(numptsperring)] )
    pts   = []
    
    radii  = np.linspace(r_inner,r_outer,numrings)
    
    for r,k in zip(radii, range(len(radii))) :
        print(r,k)
        xs = r*xunit
        ys = r*yunit
        
        for x,y in zip(xs,ys):
             rotmat =  np.asarray([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
             xt,yt  =  np.linalg.matrix_power(rotmat,k).dot(np.asarray([x,y]))
             pts.append(r*np.asarray([xt,yt]))

    # place them uniformly on a disk with radius somewhere between the inner and outer radius
    if numptsrem:
        xrem = (1.0 + r_outer/r_inner)/2.0  * r_inner * np.cos( [k*2*np.pi/numptsrem  for k in range(numptsrem)] )
        yrem = (1.0 + r_outer/r_inner)/2.0  * r_inner * np.sin( [k*2*np.pi/numptsrem  for k in range(numptsrem)] )
        pts.extend(list(zip(xrem,yrem)))
    return np.asarray(pts)


##-------------------------------------------------------------------------
def pts_annulus_random(numpts, r_inner=1.0, r_outer=2.0):

    pts = []
    while(len(pts)<numpts):
      x,y = - r_outer  + 2*r_outer * np.random.random(2)
      normpt = np.linalg.norm(np.asarray([x,y]))
      if normpt < r_outer and normpt > r_inner:
            pts.append(np.asarray([x,y]))
      else:
            continue
    return np.asarray(pts)

##-------------------------------------------------------------------------
def pts_ball(numpts, r=1):
    """
    Bentley #3. Uniform inside a circle of radius r
    """
    xs,ys = [],[]
    pts   = []
    
    while(len(pts)<numpts):
        x,y = -r + 2*r*np.random.random(2)
        if x**2 + y**2 < r**2:
            pts.append(np.asarray([x,y]))
        else:
            continue
    return np.asarray(pts)

##-------------------------------------------------------------------------
def pts_clusnorm(numpts, numclus=10 , mu=0,sigma=0.05):
    """
    Bentley #4. Choose numclus points from U[0,1]^2 then put 
    Normal(mu,sigma) at each
    """
    cluspts = pts_uni(numclus, xlim=[0,1], ylim=[0,1])
    pts     = []
    numptsrem = numpts%numclus
   
    for pt in cluspts:
        normal_pts_x = np.random.normal(loc=mu,scale=sigma,size=numpts//numclus)
        normal_pts_y = np.random.normal(loc=mu,scale=sigma,size=numpts//numclus)
        normal_pts   = np.asarray(list(zip(normal_pts_x, normal_pts_y)))
        for n in normal_pts:
            pts.append(n+pt)
    
    if numptsrem:
        tmp = pts_uni(numptsrem,xlim=[0,1],ylim=[0,1])
        for pt in tmp:
            pts.append(pt)

    return np.asarray(pts)
        
##-------------------------------------------------------------------------
def pts_cubediam(numpts):
    """
    Bentley #5. x = y = U[0,1]. i.e. points are randomly chosen 
    along the diagonal of a square (called cube in bentley speak)
    """
    xs = np.random.random(numpts)
    ys = xs
    return np.asarray(list(zip(xs,ys)))

##-------------------------------------------------------------------------
def pts_corners(numpts,numpolyverts=4,s=0.7):
    """
    Bentley #7. Uniform distribution at the vertices of a regular polygon 
    with `numpolyverts` vertices
    """
    vx = [2.0 * np.cos(k*2.0*np.pi/numpolyverts) for k in range(numpolyverts)]
    vy = [2.0 * np.sin(k*2.0*np.pi/numpolyverts) for k in range(numpolyverts)]

    numptsrem  = numpts%numpolyverts
    pts = []

    for x,y in zip(vx,vy):
        basept = np.asarray([x,y])
        rx = -s + 2*s * np.random.uniform(size=numpts//numpolyverts)
        ry = -s + 2*s * np.random.uniform(size=numpts//numpolyverts)
        tmp = [basept + pt for pt in np.asarray(list(zip(rx,ry)))]
        for t in tmp:
            pts.append(t)

    if numptsrem:
        tmp = pts_uni(numptsrem,xlim=[0,1],ylim=[0,1])
        for pt in tmp:
            pts.append(pt)

    assert len(pts) == numpts, "length of pts array should be the same as numpts returned"
    return np.asarray(pts)
##-------------------------------------------------------------------------
def pts_grid(numpts):
    """
    Bentley #8. Choose numpts from a square grid that contains about 1.3*numpts points
    """
    g = int(np.ceil(np.sqrt(1.3*numpts))) # grid size is `g x g (approx equal to) 1.3*N `
    pts = []
    for x in range(g):
        for y in range(g):
            pts.append(np.asarray([x,y]))
    ridxs = np.random.choice(list(range(numpts)), numpts)
    pts   = [pts[r] for r in ridxs]
    return np.asarray(perturb_pts(pts))

##-------------------------------------------------------------------------
def pts_normal(numpts, mu=0.5, sigma=1):
    """
    Bentley #9. Each dimension independent from N(mu,sigma)
    """
    xs = np.random.normal(loc=mu, scale=sigma,size=numpts)
    ys = np.random.normal(loc=mu, scale=sigma,size=numpts)
    return np.asarray(list(zip(xs,ys)))

##-------------------------------------------------------------------------
def pts_spokes(numpts):
    """
    Bentley #10. N/2 points at (U[0,1],1/2) 
    and N/2 points at (1/2,U[0,1])
    """
    nh   = numpts//2
    nrem = numpts-nh
    
    pts1 = [np.asarray([r,0.5]) for r in np.random.uniform(size=nh)]
    pts2 = [np.asarray([0.5,r]) for r in np.random.uniform(size=nh)]

    pts = pts1+pts2
    return np.asarray(pts)
    
##-------------------------------------------------------------------------
def pts_concentric_circular_points(numpts, numrings):
    numpts_per_ring = int(numpts/numrings)
    points = []
    center = np.asarray([0.5,0.5])
    for ring in range(numrings):
        radius = (ring+1)*0.5/(numrings+1)
        print("Radius computed is ", radius)
        angles = [idx * 2*np.pi/numpts_per_ring for idx in range(numpts_per_ring)]
        xs = [center[0] + radius * np.cos(theta) for theta in angles ]
        ys = [center[1] + radius * np.sin(theta) for theta in angles ]
        points.extend([np.asarray(pt) for pt in zip(xs,ys)])

    num_points_rem = numpts%numrings
    if num_points_rem != 0:
        xrs = np.random.rand(num_points_rem)
        yrs = np.random.rand(num_points_rem)
        points.extend([np.asarray(pt) for pt in zip(xrs,yrs)])
    return points

#########################
# Auxiliary functions
#########################
def perturb_pts(points,xptb=0.001, yptb=0.001):
    """ For randomly perturbing (uniformly) the x coordinate and ycoordinate of points
    within an interval [x-xptb, x+xptb] and [y-yptb,y+yptb] for all points
    Useful if we want to tweak an underlying point-distribution to remove degeneracies
    """
    points = np.asarray(points)
    dxs    = -xptb + 2*xptb*np.random.random(len(points))
    dys    = -yptb + 2*yptb*np.random.random(len(points))
    dps    = np.asarray(list(zip(dxs,dys)))
    points = points + dps
    return points

def render_points(ax,pts):
    xs = [ x for (x,_) in pts]
    ys = [ y for (_,y) in pts]
    ax.set_aspect(1.0)
    ax.plot(xs,ys,'bo')

def main():
    #pts = pts_uni(numpts=200)
    #pts = pts_ball(numpts=200)
    #pts = pts_cubediam(numpts=200)
    #pts = pts_normal(numpts=200)
    #pts = pts_grid(numpts=200)
    #pts = pts_clusnorm(numpts=200)
    #pts = pts_concentric_circular_points(numpts=200,numrings=4)
    #pts = pts_spokes(numpts=200)
    #pts = pts_annulus(numpts=200)
    pts = pts_annulus_random(numpts=200)
    fig, ax = plt.subplots()
    render_points(ax,pts)
    plt.show()

if __name__=="__main__":
    main()
