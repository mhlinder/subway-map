from pandas import read_csv
from pyproj import Proj, transform
import fiona
import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from geopandas import GeoDataFrame

import pickle

stops = pickle.load(open('save/stops.p','rb'))

# # 2.5 population data
# read in census populatio data
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
            p1_points = np.array(subshape)
            p2_points = transform(p1,p2,p1_points[:,0],p1_points[:,1])
            p2_points = np.array(p2_points).T

            tract_polygons.append(Polygon(p2_points))
            geoids.append(shape['properties']['GEOID'])

tracts = GeoDataFrame(index=range(len(tract_polygons)))
tracts['region'] = tract_polygons
tracts['geoid'] = geoids
tracts['population'] = np.tile(np.nan, len(tracts))
tracts['pop_density'] = np.tile(np.nan, len(tracts))

# match census tract geometry with population data
for i in range(len(tracts)):
    tract = pops.iloc[i]
    pop = pops[pops['GEOID'] == tract['GEOID']].iloc[0]['POPULATION']
    tracts['population'].iloc[i] = pop

stops_list = stops['region'].tolist()
tracts_list = tracts['region'].tolist()
tract_sets = []
for i in range(len(stops_list)):
    stop = stops_list[i]
    contains = []
    for j in range(len(tracts_list)):
        tract = tracts_list[j]
        if stop.intersects(tract):
            intersection = (stop.intersection(tract))
            contains.append((intersection.area,tracts.iloc[j]['population']/(tract.area/1000000)))
    tract_sets.append(contains)

# set income for each subway stop to be average median household income,
# weighted by proportion of total area represented by each tract
stops['population'] = np.tile(np.nan, len(stops))
for i in range(len(stops)):
    stop = stops.iloc[i]
    tract_set = np.array(tract_sets[i])

    total = np.sum(tract_set[:,0])
    weights = tract_set[:,0] / total
    weighted_pops = tract_set[:,1]*weights
    pop = np.sum(weighted_pops)

    stops['population'].iloc[i] = pop

# convert to people per kilometer
stops['pop_dens'] = stops['population'] #/ (stops['v_area']/1000000)
stops['lpop_dens'] = np.log(stops['pop_dens'])

pickle.dump(stops,open('save/stops_pop.p','wb'))
