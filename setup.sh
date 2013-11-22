#!/bin/bash
# Initialize directory structure for SubwayMap project

# # Get data
mkdir indata
cd indata

# http://www.nyc.gov/html/dcp/html/bytes/dwndistricts.shtml
wget http://www.nyc.gov/html/dcp/download/bytes/nybb_13a.zip
unzip nybb_13a.zip
rm nybb_13a.zip

# http://www.mta.info/developers/download.html
mkdir google_transit
cd google_transit
wget http://www.mta.info/developers/data/nyct/subway/google_transit.zip
unzip google_transit.zip
rm google_transit.zip
cd ..

mkdir ACS
cd ACS/
# wget http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_All_Tables/NewYork_Tracts_Block_Groups_Only.zip
# unzip NewYork_Tracts_Block_Groups_Only.zip
wget http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/20115ny0056000.zip
unzip 20115ny0056000.zip
wget http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/20115ny0002000.zip
unzip 20115ny0002000.zip
wget http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/g20115ny.csv
wget http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/g20115ny.txt
wget http://www2.census.gov/acs2011_5yr/summaryfile/Sequence_Number_and_Table_Number_Lookup.txt
cd ..

cd ..

# # Format data
# extract data from American Community Survey census estimates, 2007--2011 5yr
# estimates. for data documentation, see http://www2.census.gov/acs2011_5yr/summaryfile/ACS_2007_2011_SF_Tech_Doc.pdf

# median household income (table b19013)
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

# total population (table b01003)
est_file=$data_dir'e20115ny0002000.txt'
save='save/population'

echo 'GEOID,POPULATION' > $save
awk -F, 'FNR==NR{
            if ($3 ~ 140 && $51 ~ /(Bronx|Kings|New York|Queens) County/)
                {locs[$5]=$49}}
            {if ($6 in locs && $130 !~ /\./)
                {print locs[$6] "," $7}}' $geo_file $est_file >> $save
