# M. Henry Linder, November 2013
# Calculate a Voronoi tesselation of New York City's subway system
import fiona
import numpy as np
from pandas import read_csv
from geopandas import GeoDataFrame, GeoSeries
from pyproj import Proj, transform
from shapely.geometry import Polygon, MultiPolygon
from scipy.spatial import Voronoi

import pickle


# # NYC boundary data
with fiona.open('indata/nybb_13a/nybb.shp') as source:
    # set up three projection types: boundary data start; google-standard
    # lat/lon, using WGS84; Albers Equal Area
    p1 = Proj(source.crs,preserve_units=True)
    p2 = Proj({'proj':'longlat', 'datum':'WGS84'})
    p3 = Proj({'proj':'aea', 'datum':'WGS84', 'lon_0':'-96'})

    # for each shape, convert its coordinates to AEA
    nyc = MultiPolygon()
    for shape in source:
        for subshape in shape['geometry']['coordinates']:
            p1_points = np.array(subshape[0])

            p2_points = transform(p1, p2, p1_points[:,0], p1_points[:,1])
            p3_points = transform(p2, p3, p2_points[0], p2_points[1])
            p3_points = np.vstack([p3_points[0], p3_points[1]]).T

            new = Polygon(p3_points)
            nyc = nyc.union(new)

# i = 0
# for shape in nyc:
    # x,y = shape.exterior.xy
    # plt.plot(x,y)

    # bounds = np.array(shape.bounds)
    # bounds = bounds.reshape([2,2])
    # cx = np.mean(bounds[:,0])
    # cy = np.mean(bounds[:,1])

    # plt.text(cx,cy,str(i))
    # i = i+1
# By running the above, we identify the following islands that contain subway stations:
#        i  borough            name
#   1.   3  staten island      staten island
#   2.  39  manhattan          manhattan
#   3.  36  manhattan          roosevelt island
#   4.  40  bronx              bronx
#   5.  10  brooklyn / queens  rockaways
#   6.  14  brooklyn / queens  jamaica bay wildlife refuge / broad channel
#   7.  15  brooklyn / queens  brooklyn / queens
indices = [3, 39, 36, 40, 10, 14, 15]
boundary = []
for i in indices:
    boundary.append(nyc[i])
nyc = MultiPolygon(boundary)


# # Subway stops data
stops = read_csv('indata/google_transit/stops.txt')
stops = stops[stops['location_type']==1]

# this still results in 4 dupes; remove each by hand
stops = stops[stops['stop_id']!='718']
stops = stops[stops['stop_id']!='A12']
stops = stops[stops['stop_id']!='A32']
stops = stops[stops['stop_id']!='N12']

stops_pts = np.array(stops[['stop_lon','stop_lat']])
stops_pts = transform(p2, p3, stops_pts[:,0], stops_pts[:,1])
stops_pts = np.vstack([stops_pts[0], stops_pts[1]]).T
# save aea-projected location
stops['x'] = stops_pts[:,0]
stops['y'] = stops_pts[:,1]

# calculate voronoi diagram:

# first, calculate a bounding box to restrict the diagram
min_x = min(stops_pts[:,0]) - 5000
max_x = max(stops_pts[:,0]) + 5000
min_y = min(stops_pts[:,1]) - 5000
max_y = max(stops_pts[:,1]) + 5000
bbox = np.array([[min_x,min_y], [max_x,max_y], [min_x,max_y], [max_x,min_y]])

# find the voronoi
coords = np.vstack([stops_pts, bbox])
vor = Voronoi(coords)

# rearrange, so that regions are in the same order as their corresponding
# points, so the last four are the bbox dummy observations, and remove them
regions = np.array(vor.regions)[vor.point_region]
regions = regions[:-4]
clipped = []
for region in regions:
    region_vertices = vor.vertices[region]
    region_polygon = Polygon(region_vertices)

    if nyc.intersects(region_polygon):
        clipped.append(nyc.intersection(region_polygon))

clipped = GeoSeries(clipped)
stops = GeoDataFrame(stops)
stops.index = np.arange(stops.shape[0])
stops['region'] = clipped

pickle.dump(stops,open('save/stops.p','wb'))
pickle.dump(nyc,open('save/nyc.p','wb'))
