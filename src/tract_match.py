import fiona
from pandas import read_csv
from pyproj import Proj, transform
from numpy import array, nan, tile, log
from shapely.geometry import Polygon
from geopandas import GeoDataFrame
from utils import nyc_boundary

acs_geoids = read_csv('data/save/tiger_match.csv')

tract_polygons = []
geoids = []
with fiona.open('data/indata/tiger/tl_2011_36_tract.shp', 'r') as source:
    p1 = Proj({'proj': 'longlat', 'datum': 'WGS84'})
    p2 = Proj({'proj': 'aea', 'datum': 'WGS84', 'lon_0': '-96'})

    for shape in source:
        if int(shape['properties']['GEOID']) in acs_geoids['geoid'].values:
            if shape['geometry']['type']=='MultiPolygon':
                continue

            subshape = shape['geometry']['coordinates'][0]

            p1_points = array(subshape)
            p2_points = transform(p1, p2, p1_points[:,0], p1_points[:,1])
            p2_points = array(p2_points).T

            tract_polygons.append(Polygon(p2_points))
            geoids.append(shape['properties']['GEOID'])

tracts = GeoDataFrame(index=range(len(tract_polygons)))

tracts['region'] = tract_polygons
tracts['geoid'] = geoids
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
