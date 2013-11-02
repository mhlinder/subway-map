import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d

city_aea = pd.read_csv('output/city_aea')
stops_aea = pd.read_csv('output/stops_aea')

stops_voronoi = Voronoi(stops_aea[['lon','lat']])

for snum in pd.unique(city_aea['SID']):
    plt.figure(snum)
    s = city_aea[city_aea['SID']==snum]
    plt.plot(s['X'],s['Y'])
    plt.scatter(stops_aea['lon'],stops_aea['lat'])
    plt.savefig('output/%d.png' % snum)
    plt.close()
