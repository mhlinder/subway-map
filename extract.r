# # Extract NYC, subway data from shapefile
library(maptools)
library(rgdal)

# # Load NYC shapefile
# proj4 found by:
# 	library('rgdal')
# 	shape<-readOGR('nybb.shp',layer='nybb')
# 	proj4string(shape)
# returning:
# 	+proj=lcc +lat_1=40.66666666666666 +lat_2=41.03333333333333 +lat_0=40.16666666666666 +lon_0=-74 +x_0=300000 +y_0=0 +datum=NAD83 +units=us-ft +no_defs +ellps=GRS80 +towgs84=0,0,0
nyc.shp <- readShapePoly('indata/nybb_13a/nybb',proj4string=CRS('+proj=lcc +lat_1=40.66666666666666 +lat_2=41.03333333333333 +lat_0=40.16666666666666 +lon_0=-74 +x_0=300000 +y_0=0 +datum=NAD83 +units=us-ft +no_defs +ellps=GRS80 +towgs84=0,0,0'))
city <- spTransform(nyc.shp,CRS('+proj=longlat +datum=WGS84')) # convert to WGS84 a la MTA data

# # Read subway stations
stops <- read.csv('indata/google_transit/stops.txt')
stops_parents <- stops[stops$location_type==1,]
stops_parents <- SpatialPointsDataFrame(cbind(stops_parents$stop_lon,stops_parents$stop_lat),as.data.frame(stops_parents$stop_name),proj4str=CRS("+proj=longlat +datum=WGS84"))

# # Project into Albers Equal Area
# City
city_aea <- spTransform(city,CRS('+proj=aea +datum=WGS84 +lon_0=-96'))
# Dissolve into single shape--see http://www.nceas.ucsb.edu/scicomp/usecases/PolygonDissolveOperationsR
lps <- getSpPPolygonsLabptSlots(city_aea)
onebin <- cut(lps[,1], range(lps[,1]), include.lowest=TRUE)
city_aea <- unionSpatialPolygons(city_aea, onebin)
city_aea <- SpatialPolygons2PolySet(city_aea)

# Stops
stops_aea <- spTransform(stops_parents,CRS('+proj=aea +datum=WGS84 +lon_0=-96'))
stops_aea <- as.data.frame(stops_aea)
colnames(stops_aea) <- c("stop_name","lon","lat")

# plotPolys(city_aea_ps, proj=TRUE)

# # Export
write.table(city_aea, 'output/city_aea', sep=',')
write.table(stops_aea, 'output/stops_aea', sep=',')
