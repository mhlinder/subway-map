#!/bin/bash

# http://www.mta.info/developers/download.html
mkdir data/indata/google_transit/
cd data/indata/google_transit/
curl -O http://www.mta.info/developers/data/nyct/subway/google_transit.zip
unzip google_transit.zip
rm google_transit.zip
cd -
