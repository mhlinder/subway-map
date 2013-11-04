import numpy as np
import pandas as pd
from scipy.spatial import Voronoi
from shapely.geometry import Polygon

import matplotlib.pyplot as plt
from scipy.spatial import voronoi_plot_2d

stops_aea = pd.read_csv('output/stops_aea')
city_aea = pd.read_csv('output/city_aea')

# # calculate voronoi diagram
# calculate a bounding box to restrict the voronoi diagram
min_lon = min(stops_aea['lon']) - 5000
max_lon = max(stops_aea['lon']) + 5000
min_lat = min(stops_aea['lat']) - 5000
max_lat = max(stops_aea['lat']) + 5000
bbox = np.array([[min_lon,min_lat], [max_lon,max_lat], [min_lon,max_lat], [max_lon,min_lat]])

# find the voronoi of the set of points (stops_aea, bbox)
coords = np.array(stops_aea[['lon','lat']])
coords = np.vstack([coords, bbox])
vor = Voronoi(coords)

# # find the intersections
islands = [2, 64, 22, 48, 52, 56, 58]
clipped = {island: [] for island in islands}

for i in islands:
    clip = Polygon(np.array(city_aea[city_aea['SID'] == i][['X','Y']]))
    for region in vor.regions:
        region = np.array(region)
        # the bounding box point regions will be the only ones extending to infinity; true only if no infinite boundaries
        if region.shape[0] and np.all(region >= 0):
            region_vertices = vor.vertices[region]
            region_polygon = Polygon(region_vertices)

            if clip.intersects(region_polygon):
                clipped[i].append(clip.intersection(region_polygon))
