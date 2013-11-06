import pickle
stops = pickle.load(open('save/stops.p','rb'))
nyc = pickle.load(open('save/nyc.p','rb'))

import numpy as np
import matplotlib.pyplot as plt

dupes = {}
for stop in stops.iterrows():
    stop = stop[1]
    name = stop['stop_name']
    dupe = stops['stop_name'] == name
    if np.sum(dupe) > 1:
        dupes[name] = stops[dupe]
keys = dupes.keys()

i = 1
for key in dupes:
    fig = plt.figure(i,dpi=540)
    fig.set_size_inches(24,24)
    for clip in nyc:
        x,y = clip.exterior.xy
        plt.plot(x,y)
    dupe = dupes[key]
    title = ''
    for d in dupe.iterrows():
        j = d[0]
        title = title + str(j) + ' '
        d = d[1]
        x = d['x']
        y = d['y']
        plt.scatter(x,y)
        plt.text(x,y,str(j))
    fig.suptitle(title)
    plt.savefig('save/dupes/' + key + '.png')
    plt.close()
