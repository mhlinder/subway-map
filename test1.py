import numpy as np
import pandas as pd
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, MultiPolygon

import matplotlib.pyplot as plt

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
clips = []
clipped = []

# Create a collection of polygons for the boundary of New York City
for i in islands:
    clip = Polygon(np.array(city_aea[city_aea['SID'] == i][['X','Y']]))
    clips.append(clip)
clips = MultiPolygon(clips)
# create a list of clipped polygons---only non-infinite regions,
for region in vor.regions:
    region = np.array(region)
    # the bounding box point regions will be the only ones extending to infinity
    if region.shape[0] and np.all(region >= 0):
        region_vertices = vor.vertices[region]
        region_polygon = Polygon(region_vertices)

        if clips.intersects(region_polygon):
            clipped.append(clips.intersection(region_polygon))


# # Plotting
GRAY = '#999999'
BLACK = '#000000'
def plot_border(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, color=BLACK, linewidth=3, solid_capstyle='round', zorder=2)

def plot_line(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, color=GRAY, linewidth=3, solid_capstyle='round', zorder=1)

fig = plt.figure(1)
ax = fig.add_subplot(111)

for polygon in clipped:
    if polygon.geom_type == 'Polygon':
        plot_line(ax, polygon.exterior)
    elif polygon.geom_type == 'MultiPolygon':
        for subpolygon in polygon:
            plot_line(ax, subpolygon.exterior)

for clip in clips:
    plot_border(ax,clip.exterior)
