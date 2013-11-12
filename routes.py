# identify all midmorning, weekday trips of the subway; this is the benchmark
# for what trips are available; generate a network of subway stops
import pickle
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyproj import Proj, transform

# # generate unique routes
trips = pd.read_csv('indata/google_transit/stop_times.txt')
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

# remove north/south distinction; just use first three letters in stop names
unique_routes_new = {}
for pair in unique_routes.keys():
    start = pair[0][:3]
    end = pair[1][:3]
    pair_new = (start,end)
    unique_routes_new[pair_new] = []
    for route in unique_routes[pair]:
        route_new = []
        for stop in route:
            stop = stop[:3]
            route_new.append(stop)
        unique_routes_new[pair_new].append(route_new)
unique_routes = unique_routes_new


# # collect connectedness of each stop
p1 = Proj({'proj':'longlat', 'datum':'WGS84'})
p2 = Proj({'proj':'aea', 'datum':'WGS84', 'lon_0':'-96'})

unique_routes = pickle.load(open('save/unique_routes.p','rb'))
stops = pd.read_csv('indata/google_transit/stops.txt')
stops = stops[stops['location_type']==1]

staten_island = ['St George','Tompkinsville','Stapleton','Clifton','Grasmere','Old Town','Dongan Hills','Jefferson Av','Grant City','New Dorp','Oakwood Heights','Bay Terrace','Great Kills','Eltingville','Annadale','Huguenot',"Prince's Bay",'Pleasant Plains','Richmond Valley','Nassau','Atlantic','Tottenville']
subway = [stop in staten_island for stop in stops['stop_name']]
si_ids = stops[subway]['stop_id'].tolist() # keep ids of SI for later filtering
subway = [stop not in staten_island for stop in stops['stop_name']]
# stops = stops[subway]
stops.index = range(len(stops))

x = stops['stop_lon']
y = stops['stop_lat']
aea = transform(p1,p2,x,y)
x,y = aea
stops['x'] = x
stops['y'] = y

system = nx.Graph()
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
transfers = pd.read_csv('indata/google_transit/transfers.txt')
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
                neighbors = nx.all_neighbors(system,node)
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.append(neighbor)
                        layers[i].append(neighbor)
                j = j+1
        connectedness.append(m(layers))
    else:
        connectedness.append(np.nan)
stops['connectedness'] = connectedness

# # Plot
# nyc = pickle.load(open('save/nyc.p','rb'))

# for clip in nyc:
    # x,y = clip.exterior.xy
    # plt.plot(x,y,'k-')

# for node in system.nodes():
    # x,y = locs[node]
    # plt.scatter(x,y,marker='.',c='r')

# for edge in system.edges():
    # a,b = edge
    # x1,y1 = locs[a]
    # x2,y2 = locs[b]
    # plt.plot((x1,x2),(y1,y2),'r-')
