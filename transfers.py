from pandas import read_csv
import numpy as np
import networkx as nx
import pickle

stops = pickle.load(open('save/stops.p','rb'))
transfers = read_csv('indata/google_transit/transfers.txt')

already_in = []
transfer_stops = []
for i in range(len(transfers)):
    transfer = transfers.iloc[i]
    from_id = transfer['from_stop_id']
    to_id = transfer['to_stop_id']
    if from_id != to_id:
        from_id_in = from_id in already_in
        to_id_in = to_id in already_in
        if not from_id_in or not to_id_in:
            if not from_id_in and not to_id_in:
                transfer_stops.append([from_id,to_id])
                already_in.append(from_id)
                already_in.append(to_id)
            else:
                if from_id_in:
                    find = from_id
                    add = to_id
                else:
                    find = to_id
                    add = from_id
                for transfer_stop in transfer_stops:
                    if find in transfer_stop:
                        transfer_stop.append(add)

# for transfer in transfer_stops:
  #   combine = np.any([stops['stop_id'] == stop_id for stop_id in transfer],axis=0)
  #   concat = stops[combine]
#     omit = np.all([stops['stop_id'] != stop_id for stop_id in transfer],axis=0)
#     stops = stops[omit]
