all: datadir data voronoi


data: nybb_13a google_transit ACS acs_geoids

datadir:
	mkdir -p data/indata/ data/save/


nybb_13a:
	src/indata/nybb_13a.sh

google_transit:
	src/indata/google_transit.sh

voronoi:
	python src/voronoi.py


ACS:
	src/indata/ACS.sh

acs_geoids:
	src/indata/acs_geoids.sh

census:
	python src/census_request.py

tract_match:
	python src/tract_match.py

tracts_stops:
	python src/tracts_stops.py

geojson_dump:
	python src/geojson_dump.py

topojson:
	topojson --width 800 --height 750 --margin 20 -s .25 -o src/web/data.topojson -p -- src/web/tracts.json src/web/stops.json src/web/system.json
