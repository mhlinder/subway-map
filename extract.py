import fiona
from pyproj import Proj, transform
from shapely.geometry import Polygon, MultiPolygon
import numpy as np

import matplotlib.pyplot as plt

shapes = []
with fiona.open('indata/nybb_13a/nybb.shp') as source:
    # set up three projection types: boundary data start; google-standard
    # lat/lon, using WGS84; Albers Equal Area
    p1 = Proj(source.crs,preserve_units=True)
    p2 = Proj({'proj':'longlat', 'datum':'WGS84'})
    p3 = Proj({'proj':'aea', 'datum':'WGS84', 'lon_0':'-96')

    # for each shape, convert its coordinates to AEA
    for shape in source:
        for subshape in shape['geometry']['coordinates']:
            p1_points = np.array(subshape[0])

            p2_points = transform(p1, p2, p1_points[:,0], p1_points[:,1])
            p3_points = transform(p2, p3, p2_points[0], p2_points[1])
            p3_points = np.vstack([p3_points[0], p3_points[1]]).T

            shapes.append(Polygon(p3_points))

shapes = MultiPolygon(shapes)
