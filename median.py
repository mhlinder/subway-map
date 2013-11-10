# match median household income to census tract
import fiona
import numpy as np
from pandas import read_csv
from pyproj import Proj, transform
from shapely.geometry import Polygon
from geopandas import GeoDataFrame

# read in census income data
incomes = read_csv('save/median')
for i in range(len(incomes)):
    tract = incomes.ix[i]
    geoid = tract['GEOID']
    geoid = geoid.split('US')[1]
    incomes['GEOID'].ix[i] = geoid

# load TIGER census tract geometries
tract_polygons = []
geoids = []
with fiona.open('indata/tiger/tl_2011_36_tract.shp','r') as source:
    p1 = Proj({'proj':'longlat', 'datum':'WGS84'})
    p2 = Proj({'proj':'aea', 'datum':'WGS84', 'lon_0':'-96'})
    for shape in source:
        if shape['properties']['GEOID'] in incomes['GEOID'].values:
            subshape = shape['geometry']['coordinates'][0]
            p1_points = np.array(subshape)
            p2_points = transform(p1,p2,p1_points[:,0],p1_points[:,1])
            p2_points = np.array(p2_points).T

            tract_polygons.append(Polygon(p2_points))
            geoids.append(shape['properties']['GEOID'])

tracts = GeoDataFrame(index=range(len(tract_polygons)))
tracts['region'] = tract_polygons
tracts['geoid'] = geoids
tracts['income'] = np.tile(np.nan, len(tracts))

# match census tract geometry with income data
for i in range(len(tracts)):
    tract = tracts.iloc[i]
    income = incomes[incomes['GEOID'] == tract['geoid']].iloc[0]['MEDIAN_INCOME']
    tracts['income'].iloc[i] = income
