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

mkdir mta
cd mta/
wget http://www.mta.info/developers/data/nyct/subway/StationEntrances.csv
wget http://www.mta.info/developers/resources/nyct/subway/StationEntranceDefinitions.csv
cd ..

mkdir ACS
cd ACS/
# wget http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_All_Tables/NewYork_Tracts_Block_Groups_Only.zip
# unzip NewYork_Tracts_Block_Groups_Only.zip
http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/20115ny0056000.zip
unzip 20115ny0056000.zip
wget http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/g20115ny.csv
wget http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/g20115ny.txt
wget http://www2.census.gov/acs2011_5yr/summaryfile/Sequence_Number_and_Table_Number_Lookup.txt
cd ..

cd ..
