import pickle
import matplotlib.pyplot as plt
from geopandas import GeoDataFrame, GeoSeries
from descartes import PolygonPatch
import numpy as np

# stops = pickle.load(open('save/stops_pop.p','rb'))
tracts = pickle.load(open('save/tracts.p','rb'))

measure = 'lpop_dens'
outname = 'save/plots/choropleth_' + measure + '.png'

# Plotting
# # This is a choropleth according to area
fig = plt.figure(1,dpi=540,frameon=False)
plt.title(measure)
ax = fig.add_subplot(111)

fig.set_size_inches(24,24)
ax.axis('off')

# calculate percentiles for binning area
q = float(100)/6
qs = q*np.arange(7)
qs = np.percentile(tracts[measure], qs.tolist())
qs = np.vstack([qs[:-1], qs[1:]]).T

# 'Blues' colorscheme from colorbrewer2.org; ascending from white to blue
colors = ['#EFF3FF', '#C6DBEF', '#9ECAE1', '#6BAED6', '#3182BD', '#08519C']
for row in tracts.iterrows():
    row = row[1]
    if not np.isnan(row[measure]):
        polygon = row['region']

        # plot region
        # find index of bin for coloring
        comparison = row[measure] <= qs
        if np.all(comparison):
            color_index = 0
        else:
            color_index = np.where(np.logical_xor(comparison[:,0],comparison[:,1]))[0][0]
        c = colors[color_index]

        if polygon.geom_type == 'Polygon':
            ax.add_patch(PolygonPatch(polygon,facecolor=c,edgecolor="#000000"))
        elif polygon.geom_type == 'MultiPolygon':
            for subpolygon in polygon:
                ax.add_patch(PolygonPatch(subpolygon,facecolor=c,edgecolor="#000000"))


nyc = pickle.load(open('save/nyc.p','rb'))
for clip in nyc:
    x, y = clip.exterior.xy
    ax.plot(x, y, color="#000000", linewidth=1, zorder=2)

plt.savefig(outname)
plt.close()