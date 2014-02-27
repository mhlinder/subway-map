# 0.
import numpy as np
import fiona
from shapely.geometry import MultiPolygon, Polygon
from pyproj import transform, Proj
import pickle
import matplotlib.pyplot as plt
from geopandas import GeoDataFrame, GeoSeries
from descartes import PolygonPatch

def choropleth(df, measure, stops):
    # Plotting
    # # This is a choropleth according to area
    fig = plt.figure(1,dpi=540,frameon=False)
    # plt.title(measure)
    ax = fig.add_subplot(111)
    
    fig.set_size_inches(24,24)
    ax.axis('off')
    
    # calculate percentiles for binning area
    # q = float(100)/6
    # qs = q*np.arange(7)
    q = float(100)/4
    qs = q*np.arange(5)
    qs = np.percentile(df[measure], qs.tolist())
    qs = np.vstack([qs[:-1], qs[1:]]).T
    
    # 'Blues' colorscheme from colorbrewer2.org; ascending from white to blue
    # colors = ['#EFF3FF', '#C6DBEF', '#9ECAE1', '#6BAED6', '#3182BD', '#08519C']
    colors = ['#EFF3FF', '#C6DBEF', '#3182BD', '#08519C']
    for row in df.iterrows():
        row = row[1]
        if not np.isnan(row[measure]):
            polygon = row['region']
    
            # plot region
            # find index of bin for coloring
            comparison = row[measure] <= qs
            if np.all(comparison) or not np.any(comparison):
                color_index = 0
            else:
                color_index = np.where(np.logical_xor(comparison[:,0],comparison[:,1]))[0][0]
            c = colors[color_index]
    
            if polygon.geom_type == 'Polygon':
                ax.add_patch(PolygonPatch(polygon,facecolor=c,edgecolor="#000000"))
            elif polygon.geom_type == 'MultiPolygon':
                for subpolygon in polygon:
                    ax.add_patch(PolygonPatch(subpolygon,facecolor=c,edgecolor="#000000"))
    
    
    nyc = pickle.load(open('data/save/nyc.p','rb'))
    for clip in nyc:
        x, y = clip.exterior.xy
        ax.plot(x, y, color="#000000", linewidth=1, zorder=2)
    
    for i in range(len(stops)):
        stop = stops.iloc[i]
        ax.plot(stop['x'], stop['y'], 'ro')

    
    outname = 'data/plots/choropleth_' + measure + '.png'
    plt.savefig(outname)
    plt.close()

def corr(x,y,k=0):
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
    
    return r

def nyc_boundary():
    boroughs = {}
    # maps BoroCode to categorical
    borough_names = {5:'SI',4:'Q',3:'BK',1:'M',2:'BX'}
    
    with fiona.open('data/indata/nybb_13a/nybb.shp','r') as source:
        # set up three projection types: boundary data start; google-standard
        # lat/lon, using WGS84; Albers Equal Area
        p1 = Proj(source.crs,preserve_units=True)
        p2 = Proj({'proj':'longlat', 'datum':'WGS84'})
        p3 = Proj({'proj':'aea', 'datum':'WGS84', 'lon_0':'-96'})
    
        # for each shape, convert its coordinates to AEA
        nyc = MultiPolygon()
        for borough in source:
            borough_shapes = MultiPolygon()
            borocode = borough['properties']['BoroCode']
            for shape in borough['geometry']['coordinates']:
                p1_points = np.array(shape[0])
    
                p2_points = transform(p1, p2, p1_points[:,0], p1_points[:,1])
                p3_points = transform(p2, p3, p2_points[0], p2_points[1])
                p3_points = np.vstack([p3_points[0], p3_points[1]]).T
    
                new = Polygon(p3_points)
                nyc = nyc.union(new)
                borough_shapes = borough_shapes.union(new)
            boroughs[borocode] = borough_shapes
    
    # i = 0
    # for shape in nyc:
        # x,y = shape.exterior.xy
        # plt.plot(x,y)
    
        # bounds = np.array(shape.bounds)
        # bounds = bounds.reshape([2,2])
        # cx = np.mean(bounds[:,0])
        # cy = np.mean(bounds[:,1])
    
        # plt.text(cx,cy,str(i))
        # i = i+1
    # By running the above, we identify the following islands that contain subway stations:
    #        i  borough            name
    #   1.   3  staten island      staten island
    #   2.  39  manhattan          manhattan
    #   3.  36  manhattan          roosevelt island
    #   4.  40  bronx              bronx
    #   5.  10  brooklyn / queens  rockaways
    #   6.  14  brooklyn / queens  jamaica bay wildlife refuge / broad channel
    #   7.  15  brooklyn / queens  brooklyn / queens
    # indices = [3, 39, 36, 40, 10, 14, 15]
    indices = [39, 36, 40, 10, 14, 15]
    boundary = []
    for i in indices:
        boundary.append(nyc[i])
    nyc = MultiPolygon(boundary)

    return nyc, boroughs, borough_names
