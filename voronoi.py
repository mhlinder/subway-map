# M. Henry Linder, November 2013
# Calculate a Voronoi tesselation of New York City's subway system
import fiona
import numpy as np
from pandas import read_csv, DataFrame
from pyproj import Proj, transform
from geopandas import GeoDataFrame, GeoSeries
from shapely.geometry import Polygon, MultiPolygon
from scipy.spatial import Voronoi

import pickle

# # NYC boundary data
with fiona.open('indata/nybb_13a/nybb.shp','r') as source:
    # set up three projection types: boundary data start; google-standard
    # lat/lon, using WGS84; Albers Equal Area
    p1 = Proj(source.crs,preserve_units=True)
    p2 = Proj({'proj':'longlat', 'datum':'WGS84'})
    p3 = Proj({'proj':'aea', 'datum':'WGS84', 'lon_0':'-96'})

    # for each shape, convert its coordinates to AEA
    nyc = MultiPolygon()
    for shape in source:
        for subshape in shape['geometry']['coordinates']:
            p1_points = np.array(subshape[0])

            p2_points = transform(p1, p2, p1_points[:,0], p1_points[:,1])
            p3_points = transform(p2, p3, p2_points[0], p2_points[1])
            p3_points = np.vstack([p3_points[0], p3_points[1]]).T

            new = Polygon(p3_points)
            nyc = nyc.union(new)

# i = 0
# for shape in nyc:
    # x,y = shape.exterior.xy
    # plt.plot(x,y)

    # bounds = np.array(shape.bounds)
    # bounds = bounds.reshape([2,2])
    # cx = np.mean(bounds[:,0])
    # cy = np.mean(bounds[:,1])

    # plt.text(cx,cy,str(i))
    # i = i+1
# By running the above, we identify the following islands that contain subway stations:
#        i  borough            name
#   1.   3  staten island      staten island
#   2.  39  manhattan          manhattan
#   3.  36  manhattan          roosevelt island
#   4.  40  bronx              bronx
#   5.  10  brooklyn / queens  rockaways
#   6.  14  brooklyn / queens  jamaica bay wildlife refuge / broad channel
#   7.  15  brooklyn / queens  brooklyn / queens
# indices = [3, 39, 36, 40, 10, 14, 15]
indices = [39, 36, 40, 10, 14, 15]
boundary = []
for i in indices:
    boundary.append(nyc[i])
nyc = MultiPolygon(boundary)


# # Subway stops data
stops = read_csv('indata/google_transit/stops.txt')
stops = stops[stops['location_type']==1]
# staten island is technically the staten island railroad, NOT part of the
# subway system
staten_island = ['St George','Tompkinsville','Stapleton','Clifton','Grasmere','Old Town','Dongan Hills','Jefferson Av','Grant City','New Dorp','Oakwood Heights','Bay Terrace','Great Kills','Eltingville','Annadale','Huguenot',"Prince's Bay",'Pleasant Plains','Richmond Valley','Nassau','Atlantic','Tottenville']
subway = [stop not in staten_island for stop in stops['stop_name']]
stops = stops[subway]
stops.index = range(len(stops))

# this still results in 4 dupes; remove each by hand
stops = stops[stops['stop_id']!='718']
stops = stops[stops['stop_id']!='A12']
stops = stops[stops['stop_id']!='A32']
stops = stops[stops['stop_id']!='N12']

# project stop locations into Albers Equal Area
stops_pts = np.array(stops[['stop_lon','stop_lat']])
stops_pts = transform(p2, p3, stops_pts[:,0], stops_pts[:,1])
stops_pts = np.vstack([stops_pts[0], stops_pts[1]]).T
# save aea-projected location
stops['x'] = stops_pts[:,0]
stops['y'] = stops_pts[:,1]

# # calculate voronoi diagram:
# first, calculate a bounding box to restrict the diagram
min_x = min(stops_pts[:,0]) - 5000
max_x = max(stops_pts[:,0]) + 5000
min_y = min(stops_pts[:,1]) - 5000
max_y = max(stops_pts[:,1]) + 5000
bbox = np.array([[min_x,min_y], [max_x,max_y], [min_x,max_y], [max_x,min_y]])

# find the voronoi
coords = np.vstack([stops_pts, bbox])
vor = Voronoi(coords)

# rearrange, so that regions are in the same order as their corresponding
# points, so the last four are the bbox dummy observations, and remove them
regions = np.array(vor.regions)[vor.point_region]
regions = regions[:-4]
clipped = []
for region in regions:
    region_vertices = vor.vertices[region]
    region_polygon = Polygon(region_vertices)

    if nyc.intersects(region_polygon):
        clipped.append(nyc.intersection(region_polygon))

# add clipped regions to dataframe
clipped = GeoSeries(clipped)
stops = GeoDataFrame(stops)
stops.index = np.arange(stops.shape[0])
stops['region'] = clipped

# calculate area of each region
stops['v_area'] = GeoSeries(index=np.arange(stops.shape[0]))
stops['v_larea'] = GeoSeries(index=np.arange(stops.shape[0]))
for i in np.arange(stops.shape[0]):
    stops['v_area'].ix[i] = stops.ix[i]['region'].area
    stops['v_larea'].ix[i] = np.log(stops.ix[i]['v_area'])


# # collapse all transfers into single stops
transfers = read_csv('indata/google_transit/transfers.txt')

# find all stations that involve transfers
already_in = []
transfer_stops = []
for i in range(len(transfers)):
    transfer = transfers.iloc[i]
    from_id = transfer['from_stop_id']
    to_id = transfer['to_stop_id']

    if from_id != to_id:
        from_id_in = from_id in already_in
        to_id_in = to_id in already_in

        if not from_id_in or not to_id_in:
            if not from_id_in and not to_id_in:
                transfer_stops.append([from_id,to_id])
                already_in.append(from_id)
                already_in.append(to_id)
            else:
                if from_id_in:
                    find = from_id
                    add = to_id
                else:
                    find = to_id
                    add = from_id
                for transfer_stop in transfer_stops:
                    if find in transfer_stop:
                        transfer_stop.append(add)
                        already_in.append(add)

# generate a new stop entry for each transfer hub
for transfer in transfer_stops:
    combine = np.any([stops['stop_id'] == stop_id for stop_id in transfer],axis=0)
    concat = stops[combine]
    omit = np.all([stops['stop_id'] != stop_id for stop_id in transfer],axis=0)
    stops = stops[omit]

    new = {column:np.nan for column in concat.columns}

    new['stop_id'] = ['+'.join(concat['stop_id'])]

    new_poly = MultiPolygon()
    for poly in concat['region']:
        new_poly = new_poly.union(poly)
    new['region'] = [new_poly]

    new['v_area'] = [new['region'][0].area]
    new['v_larea'] = np.log(new['v_area'][0])

    new = DataFrame(new)
    stops = stops.append(new)


# # income data
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
            contains.append((intersection.area,tracts.iloc[j]['income']))
    tract_sets.append(contains)

# set income for each subway stop to be average median household income,
# weighted by proportion of total area represented by each tract
stops['income'] = np.tile(np.nan, len(stops))
for i in range(len(stops)):
    stop = stops.iloc[i]
    tract_set = np.array(tract_sets[i])

    total = np.sum(tract_set[:,0])
    weights = tract_set[:,0] / total
    weighted_incomes = tract_set[:,1]*weights
    income = np.sum(weighted_incomes)

    stops['income'].iloc[i] = income

# log income
stops['lincome'] = np.log(stops['income'])

# # save for later use
pickle.dump(stops,open('save/stops.p','wb'))
pickle.dump(nyc,open('save/nyc.p','wb'))
