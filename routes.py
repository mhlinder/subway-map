import pandas as pd
import numpy as np

trips = pd.read_csv('indata/google_transit/stop_times.txt')
ids = trips['trip_id'].unique()

starts = trips[trips['stop_sequence']==1]
wkd = ['WKD' in i for i in starts['trip_id']]
wkd_starts = starts[wkd]

times = []
for i in range(len(wkd_starts)):
    time = wkd_starts.iloc[i]['arrival_time'].split(':')
    time = [int(t) for t in time]
    times.append(time[0] + (time[1] + (time[2]/60.))/60.)
times = np.array(times)
midmorn = np.all([times > 10, times < 12], axis=0)
starts_midmorn = wkd_starts[midmorn]

routes = {}
for i in range(len(starts_midmorn)):
    trip = starts_midmorn.iloc[i]
    events = trips[trips['trip_id']==trip['trip_id']]
    start = events['stop_id'].iloc[0]
    if not routes[start]:
        routes[start] = []
    routes[start].append() = events['stop_id']
