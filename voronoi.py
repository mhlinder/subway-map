import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d

city_aea = pd.read_csv('output/city_aea')
stops_aea = pd.read_csv('output/stops_aea')

vor = Voronoi(stops_aea[['lon','lat']])
# far points will provide extra vertices, 'far away,' connecting the vertices (one of which is -1 for infinity) in far_vertices
far_points = []
far_vertices = []
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


# # Run the following code to find which islands contain which stops. Minor modification will display all at the same time.
# for snum in pd.unique(city_aea['SID']):
    # plt.figure(snum)

    # s = city_aea[city_aea['SID']==snum]
    # plt.plot(s['X'],s['Y'])

    # plt.scatter(stops_aea['lon'],stops_aea['lat'])

    # plt.savefig('output/%d.png' % snum)
    # plt.close()

# By running the above, we identify the following islands that contain subway stations:
#      snum  borough            name
#   1.    2  staten island      staten island
#   2.   64  manhattan          manhattan
#   3.   22  manhattan          roosevelt island
#   4.   48  bronx              bronx
#   5.   52  brooklyn / queens  rockaways
#   6.   56  brooklyn / queens  jamaica bay wildlife refuge / broad channel
#   7.   58  brooklyn / queens  brooklyn / queens
islands = [2, 64, 22, 48, 52, 56, 58]
