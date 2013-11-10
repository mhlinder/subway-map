#!/bin/bash
# for data documentation, see http://www2.census.gov/acs2011_5yr/summaryfile/ACS_2007_2011_SF_Tech_Doc.pdf
data_dir='indata/ACS/'
geo_file=$data_dir'g20115ny.csv'
est_file=$data_dir'e20115ny0056000.txt'
save='save/median'

# extract LOGRECNOs corresponding to census tracts (SUMLEVEL 140) and only in
# the four counties of interest (excludes staten island); GEOID for connection
# with TIGER GIS data; and estimate of median household income
echo 'GEOID,MEDIAN_INCOME' > $save
awk -F, 'FNR==NR{
            if ($3 ~ 140 && $51 ~ / (Bronx|Kings|New York|Queens) County/)
                {locs[$5]=$49}}
            {if ($6 in locs && $177 !~ /\./)
                {print locs[$6] "," $177}}' $geo_file $est_file >> $save
