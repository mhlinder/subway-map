import pickle
import matplotlib.pyplot as plt

nyc = pickle.load(open('save/nyc.p','rb'))
tracts = pickle.load(open('save/tracts.p','rb'))
stops = pickle.load(open('save/stops.p','rb'))

# plot
for i in range(len(tracts)):
    tract = tracts.iloc[i]
    region = tract['region']
    if region.type=='MultiPolygon':
        for subshape in region:
            x,y = subshape.exterior.xy
            plt.plot(x,y,'k-')
    else:
        x,y = tract['region'].exterior.xy
        plt.plot(x,y,'k-')
