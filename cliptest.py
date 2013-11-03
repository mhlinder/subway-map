import numpy as np
from scipy.spatial import Voronoi

def CCW(a,b,c):
    n = np.shape(a)[0]
    a11 = np.ones(n)
    a21 = np.ones(n)
    a31 = np.ones(n)
    a12 = a[:,0]
    a13 = a[:,1]
    a22 = b[:,0]
    a23 = b[:,1]
    a32 = c[:,0]
    a33 = c[:,1]

    det = a11*(a22*a33 - a23*a32) - a12*(a21*a33 - a23*a31) + a13*(a21*a32 - a22*a31)
    return det > 0

def intersect(l1,l2):
    n = np.shape(l1)[0]
    result = np.ones(n)
    p11 = l1[:,0:2]
    p12 = l1[:,2:4]
    p21 = l2[:,0:2]
    p22 = l2[:,2:4]
    result[CCW(p11, p21, p22) == CCW(p12, p21, p22)] = 0
    result[CCW(p11, p12, p21) == CCW(p11, p12, p22)] = 0
    return result

# points will be both the points for which we calculate a Voronoi diagram, and the basis of our clipping region
points = np.array([[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]])
vor = Voronoi(points)
# taken from voronoi.py
far_points = []
far_vertices = []
far_ridge_points = []
# adapted from scipy-0.13.0/scipy/spatial/_plotuitls.py
ptp_bound = vor.points.ptp(axis=0)
center = vor.points.mean(axis=0)
vor.ridge_vertices = np.array(vor.ridge_vertices)
for j in np.arange(np.shape(vor.ridge_points)[0]):
    pointidx = vor.ridge_points[j]
    simplex = vor.ridge_vertices[j]

    simplex = np.asarray(simplex)
    if np.any(simplex < 0):
        i = simplex[simplex >= 0][0]  # finite end Voronoi vertex

        t = vor.points[pointidx[1]] - vor.points[pointidx[0]]  # tangent
        t /= np.linalg.norm(t)
        n = np.array([-t[1], t[0]])  # normal

        midpoint = vor.points[pointidx].mean(axis=0)
        direction = np.sign(np.dot(midpoint - center, n)) * n
        far_point = vor.vertices[i] + direction * ptp_bound.max()

        # add new vertex (far_point) to vertices
        vor.vertices = np.vstack([vor.vertices, far_point])
        # reassign negative vertex index (negative value is always first) to newly added vertex
        vor.ridge_vertices[j][0] = np.shape(vor.vertices)[0] - 1

# NEED TO UPDATE VOR.REGIONS

# vertices in points to give clipping region points, in order
clipV = [0, 1, 2, 5, 8, 7, 6, 3, 0]
clips = points[clipV]
clips = np.hstack([clips[:-1],clips[1:]])

voronoi_lines = np.hstack([vor.vertices[vor.ridge_vertices][:,0], vor.vertices[vor.ridge_vertices][:,1]])

# combine all path lines with voronoi lines
# this would do it if a = np.array([1,2,3]): np.transpose([np.tile(a, len(b)), np.repeat(b, len(a))])
# we change this slightly for our two-dimensional arrays
lines = np.hstack([np.tile(clips.T,voronoi_lines.shape[0]).T, voronoi_lines.T.repeat(clips.shape[0],1).T])

result = intersect(lines[:,0:4], lines[:,4:8])
result = result.astype(bool)

intersections = lines[result] # lines that intersect
