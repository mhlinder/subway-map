NYC Subway Station Voronoi
==========================

## Currently in-progress
![v_larea](https://raw2.github.com/mhlinder/subway-map/master/data/plots/choropleth_v_larea.png)
Incorporating data from MTA's
[developer](http://web.mta.info/developers/download.html) website and
the Census.

Required Python libraries:
* **fiona** (read OGR)
* **geopandas** (extend `pandas` for `shapely` data)
* **matplotlib** (plotting)
* **numpy** (arrays)
* **pandas** (dataframes)
* **pyproj** (transform map projections)
* **scipy** (Voronoi)
* **shapely** (geometric objects)
* **pickle** (saving and loading data)
