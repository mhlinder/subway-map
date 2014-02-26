from pandas import read_csv
from pyproj import Proj, transform
import fiona
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, box
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt

import pickle

from utils import nyc_boundary

# # population data
# read in census population data
pops = read_csv('save/population')
for i in range(len(pops)):
    tract = pops.ix[i]
    geoid = tract['GEOID']
    geoid = geoid.split('US')[1]
    pops['GEOID'].ix[i] = geoid

# load TIGER census tract geometries
tract_polygons = []
geoids = []
with fiona.open('indata/tiger/tl_2011_36_tract.shp','r') as source:
    p1 = Proj({'proj':'longlat', 'datum':'WGS84'})
    p2 = Proj({'proj':'aea', 'datum':'WGS84', 'lon_0':'-96'})
    for shape in source:
        if shape['properties']['GEOID'] in pops['GEOID'].values:
            if shape['geometry']['type']=='MultiPolygon':
                continue
            subshape = shape['geometry']['coordinates'][0]
            # project from latitude to longitude
            p1_points = np.array(subshape)
            p2_points = transform(p1,p2,p1_points[:,0],p1_points[:,1])
            p2_points = np.array(p2_points).T

            # create polygon
            tract_polygons.append(Polygon(p2_points))
            geoids.append(shape['properties']['GEOID'])

tracts = GeoDataFrame(index=range(len(tract_polygons)))
# initialize data
tracts['region'] = tract_polygons
tracts['geoid'] = geoids
tracts['population'] = np.tile(np.nan, len(tracts))
tracts['area'] = np.tile(np.nan, len(tracts))
tracts.index = range(len(tracts))

# # trim tracts to nyc
# read in nyc boundary
nyc = nyc_boundary()

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
tracts['larea'] = np.log(tracts['area'])

# match census tract geometry with population data
for i in range(len(tracts)):
    tract = pops.iloc[i]
    pop = pops[pops['GEOID'] == tract['GEOID']].iloc[0]['POPULATION']
    tracts['population'].iloc[i] = pop

# calculate population density
tracts['pop_dens'] = tracts['population'] / tracts['area']
tracts['lpop_dens'] = np.log(tracts['pop_dens'])

# only tracts with a population
tracts = tracts[ tracts['population']!=0 ]

pickle.dump(tracts,open('save/tracts.p','wb'))
