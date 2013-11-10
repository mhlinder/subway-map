# identify all midmorning, weekday trips of the subway; this is the benchmark
# for what trips are available.
import pickle
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

pickle.dump(unique_routes,open('save/unique_routes.p','wb'))
