import fiona
import numpy as np
from pyproj import Proj, transform
from shapely.geometry import Polygon, MultiPolygon, Point

boroughs = {}
# maps BoroCode to categorical
borough_names = {5:'SI',4:'Q',3:'BK',1:'M',2:'BX'}
with fiona.open('indata/nybb_13a/nybb.shp','r') as source:
    p1 = Proj(source.crs,preserve_units=True)
    p2 = Proj({'proj':'longlat', 'datum':'WGS84'})
    p3 = Proj({'proj':'aea', 'datum':'WGS84', 'lon_0':'-96'})
    for borough in source:
        borough_shapes = MultiPolygon()
        borocode = borough['properties']['BoroCode']
        for shape in borough['geometry']['coordinates']:
            p1_points = np.array(shape[0])

            p2_points = transform(p1, p2, p1_points[:,0], p1_points[:,1])
            p3_points = transform(p2, p3, p2_points[0], p2_points[1])
            p3_points = np.vstack([p3_points[0], p3_points[1]]).T

            new = Polygon(p3_points)
            borough_shapes = borough_shapes.union(new)
        boroughs[borocode] = borough_shapes

import pickle
stops = pickle.load(open('save/stops_pop.p','rb'))

stops['borough'] = np.tile(np.nan,len(stops))
stops['borough'] = stops['borough'].astype('string')
for i in range(len(stops)):
    stop = stops.iloc[i]
    loc = Point(stop[['x','y']].values)
    for key, value in boroughs.iteritems():
        if value.contains(loc):
            stops['borough'].iloc[i] = borough_names[key]
