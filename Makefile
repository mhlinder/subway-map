all: data voronoi


data: nybb_13a google_transit ACS

datadir:
	mkdir -p data/indata/ data/save/

nybb_13a: datadir
	src/indata/nybb_13a.sh

google_transit: datadir
	src/indata/google_transit.sh

ACS: datadir
	src/indata/ACS.sh


voronoi: data
	python src/voronoi.py
