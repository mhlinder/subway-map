import fiona
from pyproj import Proj, transform
from shapely.geometry import Polygon, Point, MultiPolygon, MultiPoint
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

shapes = []
with fiona.open('indata/nybb_13a/nybb.shp') as source:
    p1 = Proj(source.crs)
    p2 = Proj({'proj':'longlat', 'datum':'WGS84'})
    p3 = Proj({'proj':'aea', 'datum':'WGS84', 'lon_0':'-96'})
    for shape in source:
        new_coords = []
        for subshape in shape['geometry']['coordinates']:
            # print np.array(subshape[0]).shape
            p1_points = np.array(subshape[0])
            p2_points = transform(p1, p2, p1_points[:,0], p1_points[:,1])
            p3_points = transform(p2, p3, p2_points[0], p2_points[1])
            p3_points = np.vstack([p3_points[0], p3_points[1]]).T
            shapes.append(Polygon(p3_points))
shapes = MultiPolygon(shapes)

points = pd.read_csv('indata/google_transit/stops.txt')
points = points[points['
