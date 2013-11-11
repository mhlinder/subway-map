from pandas import read_csv, DataFrame
import numpy as np
from shapely.geometry import MultiPolygon
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
                        already_in.append(add)

for transfer in transfer_stops:
    combine = np.any([stops['stop_id'] == stop_id for stop_id in transfer],axis=0)
    concat = stops[combine]
    omit = np.all([stops['stop_id'] != stop_id for stop_id in transfer],axis=0)
    stops = stops[omit]

    # u'stop_id', u'stop_code', u'stop_name', u'stop_desc', u'stop_lat', u'stop_lon', u'zone_id', u'stop_url', u'location_type', u'parent_station', u'x', u'y', u'region', u'v_area', u'v_larea', u'income', u'lincome'
    new = {column:np.nan for column in concat.columns}

    new['stop_id'] = ['+'.join(concat['stop_id'])]

    new_poly = MultiPolygon()
    for poly in concat['region']:
        new_poly = new_poly.union(poly)
    new['region'] = [new_poly]

    new['v_area'] = [new['region'][0].area]
    new['v_larea'] = np.log(new['v_area'][0])

    new = DataFrame(new)
    stops = stops.append(new)
