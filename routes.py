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

x = stops['stop_lon']
y = stops['stop_lat']
aea = transform(p1,p2,x,y)
x,y = aea
stops['x'] = x
stops['y'] = y

# need to remove staten island
system = nx.Graph()
for pair in unique_routes.keys():
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

nx.draw(system,locs)
