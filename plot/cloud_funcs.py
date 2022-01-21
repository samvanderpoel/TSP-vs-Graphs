# This file contains methods to generate various point distributions. 
# Most of these are sourced from Jon Bentley's experimental TSP paper:
#
#       Bentley, Jon Jouis. "Fast algorithms for geometric traveling salesman problems."
#       ORSA Journal on computing 4.4 (1992): 387-411.
#
# The methods coming from Bentley's article are labaled as such.

import numpy as np

def pts_uni(numpts, xlim=[0,1], ylim=[0,1]):
    """
    Bentley #1. Uniform within the a rectangle of with specificed limits 
    on x and y coordintes. default is unit-square
    """
    xs = xlim[0] + abs(xlim[1]-xlim[0])*np.random.random(numpts)
    ys = ylim[0] + abs(ylim[1]-ylim[0])*np.random.random(numpts)
    return np.asarray(list(zip(xs,ys)))

def pts_annulus(numpts, r_inner=1.0, r_outer=2.0, numrings=10, theta=np.pi/6):
    """
    Place points on consecutive nested concentric circles, with points 
    on each circle differing from previous circle by a scaling and rotation. 
    If numrings is not a divisor of numpts, then not all circles will
    have the same number of points.
    """
    div, rem = divmod(numpts, numrings)
    nums = numrings*[div]
    for i in range(rem):
        nums[i] += 1
    
    pts   = []
    radii = np.linspace(r_inner, r_outer, numrings)
    for r, k, num_in_ring in zip(radii, range(len(radii)), nums):
        xs = r * np.cos([k * 2.0*np.pi/num_in_ring
                         for k in range(num_in_ring)])
        ys = r * np.sin([k * 2.0*np.pi/num_in_ring
                         for k in range(num_in_ring)])
        for x, y in zip(xs, ys):
            rotmat = np.asarray([[np.cos(k*theta), -np.sin(k*theta)],
                                 [np.sin(k*theta),  np.cos(k*theta)]])
            xt, yt = rotmat.dot(np.asarray([x, y]))
            pts.append(np.asarray([xt, yt]))

    return np.asarray(pts)

def pts_annulus_random(numpts, r_inner=1.0, r_outer=2.0, dim=2):
    """
    Sample numpts points uniformly from a d-dimensional
    spherical shell of inner and outer radii r_inner and
    r_outer, respectively. For dim=2 this is an annulus.
    """
    pts = []
    while len(pts) < numpts:
        pt = - r_outer  + 2*r_outer * np.random.random(dim)
        if r_inner < np.linalg.norm(pt) < r_outer:
            pts.append(np.asarray(pt))
    return np.asarray(pts)

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

def pts_clusnorm(numpts, numclus=10 , mu=0, sigma=0.05):
    """
    Bentley #4. Choose numclus points from U[0,1]^2 then put 
    Normal(mu,sigma) at each
    """
    div, rem = divmod(numpts, numclus)
    nums = numclus*[div]
    for i in range(rem):
        nums[i] += 1

    cluspts = pts_uni(numclus, xlim=[0,1], ylim=[0,1])
    pts = []
    for idx, pt in enumerate(cluspts):
        normal_pts_x = np.random.normal(loc=mu, scale=sigma, size=nums[idx])
        normal_pts_y = np.random.normal(loc=mu, scale=sigma, size=nums[idx])
        normal_pts   = np.asarray(list(zip(normal_pts_x, normal_pts_y)))
        for n in normal_pts:
            pts.append(n+pt)

    return np.asarray(pts)

def pts_cubediam(numpts):
    """
    Bentley #5. x = y = U[0,1]. i.e. points are randomly chosen 
    along the diagonal of a square (called cube in bentley speak)
    """
    xs = np.random.random(numpts)
    ys = xs
    return np.asarray(list(zip(xs,ys)))

def pts_corners(numpts, numpolyverts=4, s=0.7):
    """
    Bentley #7. Uniform distribution at the vertices of a regular polygon 
    with `numpolyverts` vertices
    """
    div, rem = divmod(numpts, numpolyverts)
    nums = numpolyverts*[div]
    for i in range(rem):
        nums[i] += 1

    vx = [2.0 * np.cos(k*2.0*np.pi/numpolyverts) for k in range(numpolyverts)]
    vy = [2.0 * np.sin(k*2.0*np.pi/numpolyverts) for k in range(numpolyverts)]
    pts = []
    for x, y, num in zip(vx, vy, nums):
        basept = np.asarray([x, y])
        rx = -s + 2*s * np.random.uniform(size=num)
        ry = -s + 2*s * np.random.uniform(size=num)
        new_pts = [basept + pt for pt in np.asarray(list(zip(rx,ry)))]
        pts.extend(new_pts)

    return np.asarray(pts)

def pts_grid(numpts):
    """
    Bentley #8. Choose numpts from a square grid that contains about 1.3*numpts points
    """
    g = int(np.ceil(np.sqrt(1.3*numpts))) # grid size is g x g (approx equal to) 1.3*N
    pts = []
    for x in range(g):
        for y in range(g):
            pts.append(np.asarray([x,y]))
    ridxs = np.random.choice(g**2, numpts)
    pts = [pts[r] for r in ridxs]
    return np.asarray(perturb_pts(pts))

def pts_normal(numpts, mu=0.5, sigma=1):
    """
    Bentley #9. Each dimension independent from N(mu,sigma)
    """
    xs = np.random.normal(loc=mu, scale=sigma,size=numpts)
    ys = np.random.normal(loc=mu, scale=sigma,size=numpts)
    return np.asarray(list(zip(xs,ys)))

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

def pts_concentric_circular_points(numpts, numrings):
    """
    Places points on numrings concentric circles. If numrings
    is not a divisor of numpts, then not all concentric circles
    will have the same number of points.
    """
    div, rem = divmod(numpts, numrings)
    nums = numrings*[div]
    for i in range(rem):
        nums[i] += 1

    points = []
    center = np.asarray([0.5,0.5])
    for ring in range(numrings):
        radius = (ring+1)*0.5/(numrings+1)
        angles = [idx * 2*np.pi/nums[ring] for idx in range(nums[ring])]
        xs = [center[0] + radius * np.cos(theta) for theta in angles]
        ys = [center[1] + radius * np.sin(theta) for theta in angles]
        points.extend([np.asarray(pt) for pt in zip(xs, ys)])

    return np.asarray(points)

def perturb_pts(points, xptb=0.001, yptb=0.001):
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
