# match median income data with subway stop region data
import pickle
import numpy as np
import matplotlib.pyplot as plt
from descartes import PolygonPatch

stops = pickle.load(open('save/stops.p','rb'))
tracts = pickle.load(open('save/tracts.p','rb'))
nyc = pickle.load(open('save/nyc.p','rb'))

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

stops['lincome'] = np.log(stops['income'])
