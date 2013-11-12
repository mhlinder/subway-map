# M. Henry Linder, November 2013
# Calculate a Voronoi tesselation of New York City's subway system
import fiona
import numpy as np
from pandas import read_csv, DataFrame
from pyproj import Proj, transform
from geopandas import GeoDataFrame, GeoSeries
from shapely.geometry import Polygon, MultiPolygon
from scipy.spatial import Voronoi, ConvexHull
from networkx import Graph, all_neighbors

import pickle

# #      Table of Contents
# 1.     Import NYC boundary data, structured as a Shapely MultiPolygon
# 2.     Import and manipulate subway stops data; filter Staten Island (not a subway)
# 2.1    Calculate Voronoi regions around subway stops
# 2.2    Collapse all transfers into single stops (currently optional; does not
#        play nicely with routes) 
# 2.3    Routes
# 2.3.1  Extract all unique routes
# 2.3.2  Collect connectedness of each stop
# 2.4    Incorporate income data

# # Notes
# All shapes are converted to Albers Equal Area

# # options flags
transfers_collapse_flag = 0


# # 1. NYC boundary data
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


# # 2. Subway stops data
stops = read_csv('indata/google_transit/stops.txt')
stops = stops[stops['location_type']==1]
# staten island is technically the staten island railroad, NOT part of the
# subway system
staten_island = ['St George','Tompkinsville','Stapleton','Clifton','Grasmere','Old Town','Dongan Hills','Jefferson Av','Grant City','New Dorp','Oakwood Heights','Bay Terrace','Great Kills','Eltingville','Annadale','Huguenot',"Prince's Bay",'Pleasant Plains','Richmond Valley','Nassau','Atlantic','Tottenville']
subway = [stop in staten_island for stop in stops['stop_name']]
si_ids = stops[subway]['stop_id'].tolist() # keep ids of SI for later filtering

# remove SI from data
subway = [stop not in staten_island for stop in stops['stop_name']]
stops = stops[subway]
stops.index = range(len(stops))

# this still results in 4 dupes; remove each by hand
dupes = ['718','A12','A32','N12']
# for dupe in dupes:
#     stops = stops[stops['stop_id']!=dupe]
# stops = stops[stops['stop_id']!='718']
# stops = stops[stops['stop_id']!='A12']
# stops = stops[stops['stop_id']!='A32']
# stops = stops[stops['stop_id']!='N12']

# project stop locations into Albers Equal Area
stops_pts = np.array(stops[['stop_lon','stop_lat']])
stops_pts = transform(p2, p3, stops_pts[:,0], stops_pts[:,1])
stops_pts = np.vstack([stops_pts[0], stops_pts[1]]).T
# save aea-projected location
stops['x'] = stops_pts[:,0]
stops['y'] = stops_pts[:,1]

stops = stops[['stop_id','stop_name','x','y']]

# # 2.1 calculate voronoi diagram:
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


# # 2.2 collapse all transfers into single stops
transfers = read_csv('indata/google_transit/transfers.txt')
# find all stations that involve transfers
already_in = []
transfer_stops = []
for i in range(len(transfers)):
    transfer = transfers.iloc[i]
    from_id = transfer['from_stop_id']
    to_id = transfer['to_stop_id']

    # if transfer is between two different stations
    if from_id != to_id and from_id not in dupes and to_id not in dupes:
        from_id_in = from_id in already_in
        to_id_in = to_id in already_in

        # if this exact pair has not occurred before (each is duplicated,
        # once each way)
        if not from_id_in or not to_id_in:
            # if neither has occurred, this is a new transfer
            if not from_id_in and not to_id_in:
                transfer_stops.append([from_id,to_id])
                already_in.append(from_id)
                already_in.append(to_id)
            # otherwise, find the one that already exists, and add the new
            # one to it
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

# map between old stop name and new stop name
transfer_map = {}
for stop in already_in:
    for transfer in transfer_stops:
            if stop in transfer:
                transfer_map[stop] = '+'.join(transfer)

# generate a new stop entry for each transfer hub
for transfer in transfer_stops:
    # find all to be combined
    combine = np.any([stops['stop_id'] == stop_id for stop_id in transfer],axis=0)
    concat = stops[combine]
    # remove all those that will be combined
    omit = np.all([stops['stop_id'] != stop_id for stop_id in transfer],axis=0)
    stops = stops[omit]

    # add a new data frame concatenating all of them
    new = {column:np.nan for column in concat.columns}

    for attr in ['stop_id','stop_name']:
        new[attr] = ['+'.join(concat[attr])]

    # Find convex hull for points; find mean of x and y values
    xy = np.vstack([concat['x'].values,concat['y']]).T
    vertices = xy
    if len(xy) > 2:
        hull = ConvexHull(xy)
        vertices = hull.points[hull.simplices]
        vertices = np.vstack([vertices[:,0],vertices[:,1]])
        vertices = DataFrame(vertices).drop_duplicates().values
    x = np.mean(vertices[:,0])
    new['x'] = x
    y = np.mean(vertices[:,1])
    new['y'] = y

    new_poly = MultiPolygon()
    for poly in concat['region']:
        new_poly = new_poly.union(poly)
    new['region'] = [new_poly]

    new['v_area'] = new['region'][0].area
    new['v_larea'] = np.log(new['v_area'])

    new = DataFrame(new)
    stops = stops.append(new)

# # 2.3 calculate connectedness
# # 2.3.1 generate unique routes
trips = read_csv('indata/google_transit/stop_times.txt')
ids = trips['trip_id'].unique()

# find weekday ('WKD') trips
starts = trips[trips['stop_sequence']==1]
wkd = ['WKD' in i for i in starts['trip_id']]
wkd_starts = starts[wkd]

# find midmorning (between 10am and 12pm) trips
times = []
for i in range(len(wkd_starts)):
    time = wkd_starts.iloc[i]['arrival_time'].split(':')
    time = [int(t) for t in time]
    times.append(time[0] + (time[1] + (time[2]/60.))/60.)
times = np.array(times)
midmorn = np.all([times > 10, times < 12], axis=0)
starts_midmorn = wkd_starts[midmorn]

# record all midmorning routes followed, as well as all terminal stops for a
# given starting stop
routes = {stop_id:[] for stop_id in starts_midmorn['stop_id']}
ends = {stop_id:[] for stop_id in starts_midmorn['stop_id']}
for i in range(len(starts_midmorn)):
    trip = starts_midmorn.iloc[i]
    events = trips[trips['trip_id']==trip['trip_id']]
    start = events['stop_id'].iloc[0]
    routes[start].append(events['stop_id'])
    end = events['stop_id'].iloc[-1]
    if end not in ends[start]:
        ends[start].append(events['stop_id'].iloc[-1])

# record all pairs of (start,end)
start_end = []
for start in ends.keys():
    for end in ends[start]:
        start_end.append((start,end))

# record all unique trips for each (start,end) pair
unique_routes = {pair:[] for pair in start_end}
for start in routes.keys():
    for route in routes[start]:
        route = route.values.tolist()
        end = route[-1]
        pair = (start,end)
        if route not in unique_routes[pair]:
            unique_routes[pair].append(route)

# remove north/south distinction; just use first three letters in stop names;
# use transfer hub id, not original id
unique_routes_new = {}
for pair in unique_routes.keys():
    start = pair[0][:3]
    if start in already_in:
        start = transfer_map[start]
    end = pair[1][:3]
    if end in already_in:
        end = transfer_map[end]
    pair_new = (start,end)

    unique_routes_new[pair_new] = []
    for route in unique_routes[pair]:
        route_new = []
        for stop in route:
            stop = stop[:3]
            if stop in already_in:
                stop = transfer_map[stop]
            route_new.append(stop)
        unique_routes_new[pair_new].append(route_new)
unique_routes = unique_routes_new

# # 2.3.2 collect connectedness of each stop
system = Graph()
for pair in unique_routes.keys():
    # filter out staten island routes
    if pair[0] not in si_ids and pair[1] not in si_ids:
        for route in unique_routes[pair]:
            route = np.array(route)
            edges = np.vstack([route[:-1], route[1:]]).T
            system.add_nodes_from(route)
            system.add_edges_from(edges)

# find location of each node as subway stop
locs = {node:None for node in system.nodes()}
stop_id = stops['stop_id'].tolist()
for node in system.nodes():
    stop = stops[stops['stop_id']==node].iloc[0]
    locs[node] = stop[['x','y']].values

# rudimentary incorporation of transfers--just another edge
transfers = read_csv('indata/google_transit/transfers.txt')
for i in range(len(transfers)):
    transfer = transfers.iloc[i]
    if transfer['from_stop_id'] != transfer['to_stop_id']:
        system.add_edge(transfer['from_stop_id'], transfer['to_stop_id'])


# alex rolle's connectedness
def f(layers, n):
    if n in layers.keys():
        return len(layers[n])
    else:
        return -1
def s(layers,n):
    if n < len(layers.keys()):
        i = n
        total = 0
        while i >= 0:
            total = total + f(layers,i)
            i = i-1
        return total
    else:
        return -1
def m(layers):
    n = len(layers.keys())
    total = 0
    i = n-1
    while i >= 0:
        total = total + (s(layers,i) - (i+1))
        i = i-1
    return total

connectedness = []
for i in range(len(stops)):
    stop = stops.iloc[i]
    start = stop['stop_id']

    if start in system.nodes():
        start = node
        visited = [start]
        layers = {0: [start]}
        i = 0
        while len(visited) < len(system.nodes()):
            i = i+1
            layers[i] = []
            j = 0
            while j < len(layers[i-1]):
                node = layers[i-1][j]
                neighbors = all_neighbors(system,node)
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.append(neighbor)
                        layers[i].append(neighbor)
                j = j+1
        connectedness.append(m(layers))
    else:
        connectedness.append(np.nan)
stops['connectedness'] = connectedness

# # 2.4 income data
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

stops.index = range(len(stops))

# # save for later use
pickle.dump(stops,open('save/stops.p','wb'))
pickle.dump(nyc,open('save/nyc.p','wb'))
