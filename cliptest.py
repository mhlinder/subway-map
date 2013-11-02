import numpy as np
from scipy.spatial import Voronoi

# points will be both the points for which we calculate a Voronoi diagram, and the basis of our clipping region
points = np.array([[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]])
vor = Voronoi(points)

clipV = [0, 1, 2, 5, 8, 7, 6, 3, 0]
