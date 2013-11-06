# format data for json
import json
from shapely.geometry import mapping

import pickle
stops = pickle.load(open('save/stops.p','rb'))
nyc = pickle.load(open('save/nyc.p','rb'))

def FeatureCollection():
    return {'type':'FeatureCollection','features':[]}
def Feature():
    return {'type':'Feature','geometry':[]}

stops_json = FeatureCollection()

for stop in stops.iterrows():
    stop = stop[1]

    stop_json = Feature()
    properties = {'lon' : stop['stop_lon'],
                  'lat' : stop['stop_lat'],
                  'name': stop['stop_name']}
    stop_json['properties'] = properties

    region = stop['region']
    stop_json['geometry'] = mapping(region)

    stops_json['features'].append(stop_json)

with open('html/save/stops.json','w') as outfile:
    json.dump(stops_json, outfile)
