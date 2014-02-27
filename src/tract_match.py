import fiona
import pickle
from pandas import read_csv
from pyproj import Proj, transform
from numpy import array, nan, tile, log
from scipy import nanmean
from shapely.geometry import Polygon, MultiPolygon
from geopandas import GeoDataFrame
from utils import nyc_boundary

acs_geoids = read_csv('data/save/tiger_match.csv')
tiger = read_csv('data/save/tiger_match.csv')

tract_polygons = {}
with fiona.open('data/indata/tiger/tl_2011_36_tract.shp', 'r') as source:
    p1 = Proj({'proj': 'longlat', 'datum': 'WGS84'})
    p2 = Proj({'proj': 'aea', 'datum': 'WGS84', 'lon_0': '-96'})

    for shape in source:
        geoid = int(shape['properties']['GEOID'])
        if int(geoid) in acs_geoids['geoid'].values:
            if shape['geometry']['type']=='MultiPolygon':
                continue

            subshape = shape['geometry']['coordinates'][0]

            p1_points = array(subshape)
            p2_points = transform(p1, p2, p1_points[:,0], p1_points[:,1])
            p2_points = array(p2_points).T

            tract_id = tiger[ tiger['geoid'] == geoid ].iloc[0]['id']
            tract_id = str(tract_id).zfill(6)

            if tract_id not in tract_polygons.keys():
                tract_polygons[tract_id] = Polygon(p2_points)
            else:
                tract_polygons[tract_id] = tract_polygons[tract_id].union(Polygon(p2_points))

tract_ids = []
polygons = []
for key in tract_polygons.keys():
    tract_ids.append(key)
    polygons.append(tract_polygons[key])
tracts = GeoDataFrame(index=range(len(tract_polygons)))

tracts['region'] = polygons
tracts['id'] = tract_ids
tracts['area'] = tile(nan, len(tracts))
tracts.index = range(len(tracts))

# trim tracks
nyc = nyc_boundary()[0]

areas = []
print 'Trimming tracts...'
for i in range(len(tracts)):
    if i % 100 == 0:
        print i 
    # trim to nyc boundaries, no water (nybb_13a)
    tract = tracts.iloc[i]
    region = tract['region']
    if nyc.intersects(region):
        tracts['region'].iloc[i] = nyc.intersection(region)

    # find area
    area = tract['region'].area / 1000000 # in sq km
    areas.append(area)
tracts['area'] = areas
tracts['larea'] = log(tracts['area'])

census = pickle.load(open('data/save/census.p', 'rb'))

for col in census.columns:
    if col != 'tract':
        tracts[col] = tile(nan, len(tracts))

for i in range(len(tracts)):
    tract = tracts.iloc[i]

    tract = census[census['tract'] == tract['id']]

    for col in tract.columns:
        if col != 'tract':
            if len(tract) == 0:
                print 'y'
            tracts[col].iloc[i] = nanmean(tract[col])

pickle.dump(tracts, open('data/save/tracts.p', 'wb'))
