from csv import DictReader
import pickle
from pandas import DataFrame

def csv_read(path):
    f = open(path,'r')
    d = DictReader(f)
    data = [row for row in d]
    f.close()
    return data

stations = DataFrame(csv_read('indata/mta/StationEntrances.csv'))
stops = DataFrame(csv_read('indata/google_transit/stops.txt',))

i = 0
for stop in stops.iterrows():
    stop = stop[1]
    if stop['stop_lon'] not in stations['Station_Longitude'] and stop['stop_lon'] not in stations['Longitude']:
        i = i + 1
