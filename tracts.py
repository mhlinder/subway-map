mport pickle
import numpy as np
import scipy.stats as stats

import matplotlib.pyplot as plt

# load previously-generated data
nyc = pickle.load(open('save/nyc.p','rb'))
tracts = pickle.load(open('save/tracts.p','rb'))
stops = pickle.load(open('save/stops.p','rb'))

x = tracts['larea']
y = tracts['lpop_dens']
