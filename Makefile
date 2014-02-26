all: datadir data voronoi


data: nybb_13a google_transit ACS

datadir:
	mkdir -p data/indata/ data/save/

nybb_13a:
	src/indata/nybb_13a.sh

google_transit:
	src/indata/google_transit.sh

ACS:
	src/indata/ACS.sh


voronoi:
	python src/voronoi.py

choropleth:
	python src/choropleth.py

census:
	python src/census_request.py
