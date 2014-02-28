import geojson
import pickle
from shapely.geometry import mapping

stops = pickle.load(open('data/save/stops.p', 'rb'))

xy = stops[['x', 'y']]
with open('src/web/stops.csv', 'w') as f:
    for i in range(len(stops)):
        coords = xy.iloc[i]
        f.write("%s,%s" % (coords[0], coords[1]))
f.close()
