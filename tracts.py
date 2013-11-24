import pickle
import rtree
import numpy as np
import pandas as pd
from shapely.geometry import box

import matplotlib.pyplot as plt

# load previously-generated data
nyc = pickle.load(open('save/nyc.p','rb'))
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

# # 
idx = rtree.index.Index()
for i in range(len(stops)):
    stop = stops.iloc[i]
    region = stop['region']

    l,b,r,t = region.bounds
    idx.insert(i,(l,b,r,t))
    
    # x,y = box(l,b,r,t).exterior.xy
    # plt.plot(x,y)

tracts['v_area'] = np.tile(np.nan,len(tracts))
tracts['v_larea'] = np.tile(np.nan,len(tracts))
tracts['rolle_connectedness'] = np.tile(np.nan,len(tracts))
tracts['graph_connectedness'] = np.tile(np.nan,len(tracts))
tracts['borough'] = np.tile('',len(tracts))

# match with closest stops
n = 1
for i in range(len(tracts)):
    tract = tracts.iloc[i]

    left,bottom,right,top = tract['region'].bounds
    neighbors = list(idx.nearest((left,bottom,right,top),n))
    tract_stops = stops.iloc[neighbors]

    tracts['v_area'].iloc[i] = np.mean(tract_stops['v_area'])
    tracts['v_larea'].iloc[i] = np.mean(tract_stops['v_larea'])
    tracts['rolle_connectedness'].iloc[i] = np.mean(tract_stops['rolle_connectedness'])
    tracts['graph_connectedness'].iloc[i] = np.mean(tract_stops['graph_connectedness'])
    tracts['borough'].iloc[i] = tract_stops['borough'].iloc[0]
    same = tract_stops['borough']==tract_stops.iloc[0]['borough']
    if sum(same) < len(tract_stops):
        print tract_stops

tracts['borough'] = pd.Categorical(tracts['borough'])
tracts.index = np.arange(len(tracts))
pickle.dump(tracts,open('save/tracts.p','wb'))
