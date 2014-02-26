awk -F, '
    BEGIN { print "logrecno,geoid" }
    $3 ~ /140/ && $51 ~ /(Kings County|Queens County|New York County|Bronx County)/ {
        print $5","$49
    }
    ' data/indata/ACS/g20115ny.csv |
sed -e 's/14000US//' > data/save/tiger_match.csv
