import pandas as pd
import numpy as np

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
