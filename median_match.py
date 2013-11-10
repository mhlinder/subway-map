# match median income data with subway stop region data
import pickle
import numpy as np

stops = pickle.load(open('save/stops.p','rb'))
tracts = pickle.load(open('save/tracts.p','rb'))

stops['xmin'] = np.tile(np.nan, len(stops))
stops['xmax'] = np.tile(np.nan, len(stops))
stops['ymin'] = np.tile(np.nan, len(stops))
stops['ymax'] = np.tile(np.nan, len(stops))
for i in range(len(stops)):
    stop = stops.iloc[i]
    bounds = stop['region'].bounds
    stops['xmin'].iloc[i] = bounds[0]
    stops['xmax'].iloc[i] = bounds[2]
    stops['ymin'].iloc[i] = bounds[1]
    stops['ymax'].iloc[i] = bounds[3]

tracts['xmin'] = np.tile(np.nan, len(tracts))
tracts['xmax'] = np.tile(np.nan, len(tracts))
tracts['ymin'] = np.tile(np.nan, len(tracts))
tracts['ymax'] = np.tile(np.nan, len(tracts))
for i in range(len(tracts)):
    tract = tracts.iloc[i]
    bounds = tract['region'].bounds
    tracts['xmin'].iloc[i] = bounds[0]
    tracts['xmax'].iloc[i] = bounds[2]
    tracts['ymin'].iloc[i] = bounds[1]
    tracts['ymax'].iloc[i] = bounds[3]
