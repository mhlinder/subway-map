#!/bin/bash
# Initialize directory structure for SubwayMap project

mkdir indata
cd indata

# http://www.nyc.gov/html/dcp/html/bytes/dwndistricts.shtml
wget http://www.nyc.gov/html/dcp/download/bytes/nybb_13a.zip
unzip nybb_13a.zip
rm nybb_13a.zip

# http://www.mta.info/developers/download.html
wget http://www.mta.info/developers/data/nyct/subway/google_transit.zip
unzip google_transit.zip
rm google_transit.zip

cd ..
