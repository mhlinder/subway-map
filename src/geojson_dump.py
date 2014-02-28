import geojson
import pickle
from shapely.geometry import Point
from src.utils import nyc_boundary

nyc = nyc_boundary()[0]
bbox = nyc.bounds

tracts = pickle.load(open('data/save/tracts.p', 'rb'))
stops = pickle.load(open('data/save/stops.p', 'rb'))

with open('src/web/tracts.json', 'w') as f:
    f.write('{"type": "FeatureCollection", "bbox": %s, "features": [\n' %str(list(bbox)))
    for i in range(len(tracts)):
        if i > 0:
            f.write(',\n')

        tract = tracts.iloc[i]
        region = tract['region']

        s = '{"type": "Feature", "properties" : {"area": %s}, "geometry": %s}' % (tract['v_larea'], geojson.dumps(region))
        f.write(str(s))
    f.write(']}')

with open('src/web/stops.json', 'w') as f:
    f.write('{"type": "FeatureCollection", "bbox": %s, "features": [\n' %str(list(bbox)))
    xy = stops[['x', 'y']]
    for i in range(len(stops)):
        if i > 0:
            f.write(',\n')

        coords = xy.iloc[i]
        p = Point(coords.values)

        s = '{"type": "Feature",  "properties" : {"area": 0}, "geometry": %s}' % geojson.dumps(p)
        f.write(str(s))

    f.write(']}')
