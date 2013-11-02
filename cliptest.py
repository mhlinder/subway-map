import numpy as np
from scipy.spatial import Voronoi

# points will be both the points for which we calculate a Voronoi diagram, and the basis of our clipping region
points = np.array([[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]])
vor = Voronoi(points)
# taken from voronoi.py
far_points = []
far_vertices = []
far_ridge_points = []
# taken from scipy-0.13.0/scipy/spatial/_plotuitls.py
ptp_bound = vor.points.ptp(axis=0)
center = vor.points.mean(axis=0)
for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
    simplex = np.asarray(simplex)
    if np.any(simplex < 0):
        i = simplex[simplex >= 0][0]  # finite end Voronoi vertex

        t = vor.points[pointidx[1]] - vor.points[pointidx[0]]  # tangent
        t /= np.linalg.norm(t)
        n = np.array([-t[1], t[0]])  # normal

        midpoint = vor.points[pointidx].mean(axis=0)
        direction = np.sign(np.dot(midpoint - center, n)) * n
        far_point = vor.vertices[i] + direction * ptp_bound.max()

        far_points.append(far_point)
        far_vertices.append(simplex)
        far_ridge_points.append(pointidx)

# loop through pointidx, simplex again; change any negative values by adding the far_point to vor.vertices, and reassigning the vertex in simplex (vor.ridge_vertices) to point to the new vertex

# vertices in points to give clipping region points, in order
clipV = [0, 1, 2, 5, 8, 7, 6, 3, 0]
clips = points[clipV]

for i in np.arange(1, np.shape(clips)[0]):
    print clips[[i-1, i]]
    # for j in np.arange(1, np.shape(clips)[0]):
