import numpy as np
from scipy.spatial import Voronoi

def CCW(a,b,c):
    return np.linalg.det(np.array([ [1, a[0], a[1]],
                                    [1, b[0], b[1]],
                                    [1, c[0], c[1]] ]) ) > 0

def intersect(l1,l2):
    x1 = l1[0]
    y1 = l1[1]
    x2 = l2[0]
    y2 = l2[1]
    if CCW(x1, x2, y2) == CCW(y1, x2, y2):
        return False
    elif CCW(x1, y1, x2) == CCW(x1, y1, y2):
        return False
    return True

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

# for i in np.arange(1, np.shape(clips)[0]):
    # print clips[[i-1, i]]
    # # for j in np.arange(1, np.shape(clips)[0]):
