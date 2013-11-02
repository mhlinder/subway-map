import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi

city_aea = pd.read_csv('output/city_aea')
stops_aea = pd.read_csv('output/stops_aea')

stops_voronoi = Voronoi(stops_aea[['lon','lat']])

# # Run the following code to find which islands contain which stops. Minor modification will display all at the same time.
# for snum in pd.unique(city_aea['SID']):
    # plt.figure(snum)

    # s = city_aea[city_aea['SID']==snum]
    # plt.plot(s['X'],s['Y'])

    # plt.scatter(stops_aea['lon'],stops_aea['lat'])

    # plt.savefig('output/%d.png' % snum)
    # plt.close()

# By running the above, we identify the following islands that contain subway stations:
#      snum  borough            name
#   1.    2  staten island      staten island
#   2.   64  manhattan          manhattan
#   3.   22  manhattan          roosevelt island
#   4.   48  bronx              bronx
#   5.   52  brooklyn / queens  rockaways
#   6.   56  brooklyn / queens  jamaica bay wildlife refuge / broad channel
#   7.   58  brooklyn / queens  brooklyn / queens
islands = [2, 64, 22, 48, 52, 56, 58]
