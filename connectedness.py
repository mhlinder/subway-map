import pickle
import numpy as np

system = pickle.load(open('save/system.p','rb'))
sigma = pickle.load(open('save/sigma.p','rb'))
stops = pickle.load(open('save/stops.p','rb'))

sigma = np.mean(sigma,axis=1)
stops['connectedness'] = stops['connectedness'].astype('float32')

nodes = system.nodes()
for i in range(len(nodes)):
    node = nodes[i]
    index = np.where(stops['stop_id']==node)[0][0]
    stops['connectedness'].ix[index] = sigma[i]
