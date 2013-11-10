#!/bin/bash
# for data documentation, see http://www2.census.gov/acs2011_5yr/summaryfile/ACS_2007_2011_SF_Tech_Doc.pdf
geo_file='indata/ACS/g20115ny.csv'

# extract LOGRECNOs corresponding to census tracts (SUMLEVEL 140)
awk -F, '$3 ~ 140 {print $5}' $geo_file
