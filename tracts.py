import pickle
import rtree
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from shapely.geometry import Point

import matplotlib.pyplot as plt

from utils import nyc_boundary

# load previously-generated data
# nyc = pickle.load(open('save/nyc.p','rb'))
nyc, boroughs, borough_names = nyc_boundary()
tracts = pickle.load(open('save/tracts.p','rb'))
stops = pickle.load(open('save/stops.p','rb'))

tracts.index = np.arange(len(tracts))

# match incomes
incomes = {}
#read incomes
f = open('save/median','r')
f.readline()
for line in f:
    line = line.rstrip().split(',')
    line[0] = line[0].split('US')[1]
    incomes[line[0]] = float(line[1])
f.close()
# match income to population by tract, using geoid
income = []
present = []
for i in range(len(tracts.geoid)):
    tract = tracts['geoid'].iloc[i]
    if tract in incomes.keys():
        present.append(i)
        income.append(incomes[tract])
tracts = tracts.iloc[present]
tracts['income'] = income
tracts['lincome'] = np.log(tracts['income'])

# find center of bounding box
tracts['x'] = np.tile(np.nan,len(tracts))
tracts['y'] = np.tile(np.nan,len(tracts))
for i in range(len(tracts)):
    tract = tracts.iloc[i]
    region = tract['region']
    # set x,y = center of bbox
    r,b,l,t = region.bounds
    tracts['x'].iloc[i] = (r+l)/2
    tracts['y'].iloc[i] = (b+t)/2

# match with closest stops
tracts['v_area'] = np.tile(np.nan,len(tracts))
tracts['v_larea'] = np.tile(np.nan,len(tracts))
tracts['rolle_connectedness'] = np.tile(np.nan,len(tracts))
tracts['graph_connectedness'] = np.tile(np.nan,len(tracts))
# calculate nearest neighbors
n = 2
nbrs = NearestNeighbors(n_neighbors=n,
        algorithm='ball_tree').fit(stops[['x','y']].values)
for i in range(len(tracts)):
    tract = tracts.iloc[i]

    left,bottom,right,top = tract['region'].bounds
    distances, indices = nbrs.kneighbors(tract[['x','y']].values)
    tract_stops = stops.iloc[indices[0]]

    tracts['v_area'].iloc[i] = np.mean(tract_stops['v_area'])
    tracts['v_larea'].iloc[i] = np.mean(tract_stops['v_larea'])
    tracts['rolle_connectedness'].iloc[i] = np.mean(tract_stops['rolle_connectedness'])
    tracts['graph_connectedness'].iloc[i] = np.mean(tract_stops['graph_connectedness'])
    
# find which borough
tracts['borough'] = np.tile(np.nan,len(tracts))
tracts['borough'] = tracts['borough'].astype('string')
for i in range(len(tracts)):
    tract = tracts.iloc[i]
    loc = Point(tract[['x','y']].values)
    for key, value in boroughs.iteritems():
        if value.contains(loc):
            tracts['borough'].iloc[i] = borough_names[key]

tracts['borough'] = pd.Categorical(tracts['borough'])
tracts.index = np.arange(len(tracts))

pickle.dump(tracts,open('save/tracts.p','wb'))
