import geojson
import pickle
from shapely.geometry import Point, LineString
from src.utils import nyc_boundary
from numpy import where

nyc = nyc_boundary()[0]
bbox = nyc.bounds

tracts = pickle.load(open('data/save/tracts.p', 'rb'))
stops = pickle.load(open('data/save/stops.p', 'rb'))
system = pickle.load(open('data/save/system.p'))

with open('src/web/tracts.json', 'w') as f:
    f.write('{"type": "FeatureCollection", "bbox": %s, "features": [\n' % str(list(bbox)))
    for i in range(len(tracts)):
        if i > 0:
            f.write(',\n')

        tract = tracts.iloc[i]
        region = tract['region']

        # s = '{"type": "Feature", "properties" : {"area": %s}, "geometry": %s}' % (tract['v_larea'], geojson.dumps(region))
        # s = '{"type": "Feature", "properties" : {"area": %s}, "geometry": %s}' % (tract['car'], geojson.dumps(region))
        s = '{"type": "Feature", "properties" : {"area": %s}, "geometry": %s}' % (tract['graph_connectedness'], geojson.dumps(region))
        f.write(str(s))
    f.write(']}')

with open('src/web/stops.json', 'w') as f:
    f.write('{"type": "FeatureCollection", "bbox": %s, "features": [\n' % str(list(bbox)))
    xy = stops[['x', 'y']]
    for i in range(len(stops)):
        if i > 0:
            f.write(',\n')

        coords = xy.iloc[i]
        p = Point(coords.values)

        s = '{"type": "Feature",  "geometry": %s}' % geojson.dumps(p)
        f.write(str(s))

    f.write(']}')

with open('src/web/system.json', 'w') as f:
    f.write('{"type": "FeatureCollection", "bbox": %s, "features": [\n' % str(list(bbox)))
    for i in range(len(system.edges())):
        edge = system.edges()[i]
        if i > 0:
            f.write(',\n')

        i1 = where(stops['stop_id']==edge[0])[0][0]
        i2 = where(stops['stop_id']==edge[1])[0][0]

        p1 = stops[['x', 'y']].iloc[i1].values
        p2 = stops[['x', 'y']].iloc[i2].values

        l = LineString([ p1, p2 ])

        s = '{"type": "Feature", "geometry": %s}' % geojson.dumps(l)
        f.write(str(s))

    f.write(']}')
