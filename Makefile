data: nybb_13a google_transit ACS

datadir:
	mkdir data/
	mkdir data/indata/
	mkdir data/save/

# http://www.nyc.gov/html/dcp/html/bytes/dwndistricts.shtml
nybb_13a: datadir
	cd data/indata/
	curl -O http://www.nyc.gov/html/dcp/download/bytes/nybb_13a.zip
	unzip nybb_13a.zip
	rm nybb_13a.zip
	cd ../..

# http://www.mta.info/developers/download.html
google_transit: datadir
	cd data/indata/
	mkdir google_transit/
	cd google_transit/
	curl -O http://www.mta.info/developers/data/nyct/subway/google_transit.zip
	unzip google_transit.zip
	rm google_transit.zip
	cd ../../..

ACS: datadir
	cd data/indata/
	mkdir ACS/
	cd ACS/
	curl -O http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/20115ny0056000.zip
	unzip 20115ny0056000.zip
	curl -O http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/20115ny0002000.zip
	unzip 20115ny0002000.zip
	curl -O http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/20115ny0028000.zip
	unzip 20115ny0028000.zip
	curl -O http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/20115ny0113000.zip
	unzip 20115ny0113000.zip
	curl -O http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/20115ny0003000.zip
	unzip 20115ny0003000.zip
	curl -O http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/20115ny0099000.zip
	unzip 20115ny0099000.zip
	curl -O http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/20115ny0100000.zip
	unzip 20115ny0100000.zip
	curl -O http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/g20115ny.csv
	curl -O http://www2.census.gov/acs2011_5yr/summaryfile/2007-2011_ACSSF_By_State_By_Sequence_Table_Subset/NewYork/Tracts_Block_Groups_Only/g20115ny.txt
	curl -O http://www2.census.gov/acs2011_5yr/summaryfile/Sequence_Number_and_Table_Number_Lookup.txt
	rm *.zip
	cd ../..
