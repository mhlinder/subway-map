#!/bin/bash

# http://www.nyc.gov/html/dcp/html/bytes/dwndistricts.shtml
cd data/indata/
curl -O http://www.nyc.gov/html/dcp/download/bytes/nybb_13a.zip
unzip nybb_13a.zip
rm nybb_13a.zip
cd -
