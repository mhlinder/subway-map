import geojson
import pickle
from shapely.geometry import mapping

tracts = pickle.load(open('data/save/tracts.p', 'rb'))

with open('src/web/v_larea.json', 'w') as f:
    for i in range(len(tracts)):
        if i == 0:
            f.write('{"type": "FeatureCollection", "features": [\n')
        if i > 0:
            f.write(',\n')

        tract = tracts.iloc[i]
        region = tract['region']

        s = '{"type": "Feature", "properties" : {"v_larea": %s}, "geometry": %s}' % (tract['v_larea'], geojson.dumps(region))
        f.write(str(s))

        if i == len(tracts)-1:
            f.write(']}')

