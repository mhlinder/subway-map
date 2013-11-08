from csv import DictReader
from pandas import DataFrame, Series
from pyproj import Proj, transform
from collections import Counter
import pickle
import matplotlib.pyplot as plt
import numpy as np

def csv_read(path):
    f = open(path,'r')
    d = DictReader(f)
    data = [row for row in d]
    f.close()
    return data

p1 = Proj({'proj':'longlat', 'datum':'WGS84'})
p2 = Proj({'proj':'aea', 'datum':'WGS84', 'lon_0':'-96'})

# # a station is an entrance to the subway; it corresponds to a full subway
# station. a stop is merely that full subway station.

# read and format stations
stations = DataFrame(csv_read('indata/mta/StationEntrances.csv'))

stations['Longitude'] = stations['Longitude'].values.astype('float32')
stations['Latitude'] = stations['Latitude'].values.astype('float32')
stations['Station_Longitude'] = stations['Station_Longitude'].values.astype('float32')
stations['Station_Latitude'] = stations['Station_Latitude'].values.astype('float32')

x = stations['Longitude']
y = stations['Latitude']
aea = transform(p1,p2,x,y)
x,y = aea
stations['X'] = x
stations['Y'] = y

x = stations['Station_Longitude']
y = stations['Station_Latitude']
aea = transform(p1,p2,x,y)
x,y = aea
stations['Station_X'] = x
stations['Station_Y'] = y


# read and format stops
stops = DataFrame(csv_read('indata/google_transit/stops.txt',))
stops = stops[stops['location_type']=='1']
stops['stop_lon'] = stops['stop_lon'].values.astype('float32')
stops['stop_lat'] = stops['stop_lat'].values.astype('float32')

staten_island = ['St George','Tompkinsville','Stapleton','Clifton','Grasmere','Old Town','Dongan Hills','Jefferson Av','Grant City','New Dorp','Oakwood Heights','Bay Terrace','Great Kills','Eltingville','Annadale','Huguenot',"Prince's Bay",'Pleasant Plains','Richmond Valley','Nassau','Atlantic','Tottenville']
subway = [stop not in staten_island for stop in stops['stop_name']]
stops = stops[subway]
stops.index = range(len(stops))

x = stops['stop_lon']
y = stops['stop_lat']
aea = transform(p1,p2,x,y)
x,y = aea
stops['x'] = x
stops['y'] = y

# find "nearest" station using Euclidean norm
x1 = stops[['stop_lon','stop_lat']].values
x2 = stations[['Station_Longitude','Station_Latitude']].values
nearest = {}
for i in range(len(x1)):
    stop = x1[i]
    # find distance between this point and all others
    distances = np.sum((np.resize(np.tile(stop,len(x2)), [len(x2), 2]) - x2)**2, axis=-1)**(1./2)
    # choose closest one
    nearest[i] = np.argmin(distances)

routes = ['Route_1','Route_2','Route_3','Route_4','Route_5','Route_6','Route_7',
          'Route_8','Route_9','Route_10','Route_11']

stops['routes'] = Series(np.repeat('',len(stops)))
for i in nearest.keys():
    j = nearest[i]
    for route in routes:
        stops['routes'].ix[i] = stops.ix[i]['routes'] + stations.ix[j][route] + " "

# # duplicate values---ie, stations that are "closest" to two separate stops
# dupes = [item for item, count in Counter(nearest.values()).iteritems() if count > 1]

# # maps station index to multiple stop indices
# dupe_lookup = {dupe:[] for dupe in dupes}
# for key in nearest.keys():
    # if nearest[key] in dupes:
        # dupe_lookup[nearest[key]].append(key)

# for dupe in dupe_lookup.keys():
    # print stations.iloc[dupe]['Station_Name']
    # for stop in dupe_lookup[dupe]:
        # print stops.iloc[stop]['stop_name']
#     print
