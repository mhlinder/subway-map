import pickle
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyproj import Proj, transform

p1 = Proj({'proj':'longlat', 'datum':'WGS84'})
p2 = Proj({'proj':'aea', 'datum':'WGS84', 'lon_0':'-96'})

unique_routes = pickle.load(open('save/unique_routes.p','rb'))
stops = pd.read_csv('indata/google_transit/stops.txt')
stops = stops[stops['location_type']==1]

staten_island = ['St George','Tompkinsville','Stapleton','Clifton','Grasmere','Old Town','Dongan Hills','Jefferson Av','Grant City','New Dorp','Oakwood Heights','Bay Terrace','Great Kills','Eltingville','Annadale','Huguenot',"Prince's Bay",'Pleasant Plains','Richmond Valley','Nassau','Atlantic','Tottenville']
subway = [stop in staten_island for stop in stops['stop_name']]
si_ids = stops[subway]['stop_id'].tolist() # keep ids of SI for later filtering
subway = [stop not in staten_island for stop in stops['stop_name']]
stops = stops[subway]
stops.index = range(len(stops))

x = stops['stop_lon']
y = stops['stop_lat']
aea = transform(p1,p2,x,y)
x,y = aea
stops['x'] = x
stops['y'] = y

system = nx.Graph()
for pair in unique_routes.keys():
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


nyc = pickle.load(open('save/nyc.p','rb'))

for clip in nyc:
    x,y = clip.exterior.xy
    plt.plot(x,y,'k-')

for node in system.nodes():
    x,y = locs[node]
    plt.scatter(x,y,marker='.',c='r')

for edge in system.edges():
    a,b = edge
    x1,y1 = locs[a]
    x2,y2 = locs[b]
    plt.plot((x1,x2),(y1,y2),'r-')
