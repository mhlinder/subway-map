from pandas import read_csv
from pyproj import Proj, transform
import fiona
import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from geopandas import GeoDataFrame

# pops = read_csv('save/population')
# for i in range(len(pops)):
    # tract = pops.ix[i]
    # geoid = tract['GEOID']
    # geoid = geoid.split('US')[1]
#     pops['GEOID'].ix[i] = geoid
# pops = pops[ pops['POPULATION']!=0 ]

# load TIGER census tract geometries
tract_polygons = []
geoids = []
x=0
with fiona.open('indata/tiger/tl_2011_36_tract.shp','r') as source:
    p1 = Proj({'proj':'longlat', 'datum':'WGS84'})
    p2 = Proj({'proj':'aea', 'datum':'WGS84', 'lon_0':'-96'})
    for shape in source:
        # if shape['properties']['GEOID'] in pops['GEOID'].values:
        if shape['geometry']['type']=='MultiPolygon':
            tract = MultiPolygon([])
            for part in shape['geometry']['coordinates']:
                p1_points = np.array(subshape)
                p2_points = transform(p1,p2,p1_points[:,0],p1_points[:,1])
                p2_points = np.array(p2_points).T
                tract = tract.intersection(Polygon(p2_points))
        else:
            subshape = shape['geometry']['coordinates'][0]
            p1_points = np.array(subshape)
            p2_points = transform(p1,p2,p1_points[:,0],p1_points[:,1])
            p2_points = np.array(p2_points).T
            tract = Polygon(p2_points)

        tract_polygons.append(tract)
        geoids.append(shape['properties']['GEOID'])

tracts = GeoDataFrame(index=range(len(tract_polygons)))
tracts['region'] = tract_polygons
tracts['geoid'] = geoids
