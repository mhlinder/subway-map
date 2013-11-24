import pickle
import numpy as np
import scipy.stats as stats

import matplotlib.pyplot as plt

# load previously-generated data
nyc = pickle.load(open('save/nyc.p','rb'))
tracts = pickle.load(open('save/tracts.p','rb'))
stops = pickle.load(open('save/stops.p','rb'))

def corr(x,y,k):
    print 'lag: %i' % k

    if k > 0:
        x = x[:-k]
        y = y[k:]
    elif k < 0:
        k = np.abs(k)
        x = x[k:]
        y = y[:-k]

    xbar = np.mean(x)
    ybar = np.mean(y)
    r = np.sum( (x-xbar)*(y-ybar) ) / np.sqrt(sum( (x-xbar)**2 ) * sum(
        (y-ybar)**2 ))
    print r
    # return r

x = tracts['larea']
y = tracts['lpop_dens']

slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
