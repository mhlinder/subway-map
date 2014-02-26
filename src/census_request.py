key = '7d931307fc4b79ea45022d7b729e3b25b90787b2'
import requests
import numpy as np
from pandas import DataFrame, Series, concat
from numpy import array, dtype

base = 'http://api.census.gov/data/2011/acs5?key=%s' % key
state = '36' # FIPS code: New York
counties = {'kings': '047',
            'queens': '081',
            # 'richmond': '085',
            'new york': '061',
            'bronx': '005'}
county_cat = {'kings': 0,
              'queens': 1,
              # 'richmond': 2,
              'new york': 3,
              'bronx': 4}

tables = {}
tables['means_transp'] = { # means of transp. to work
        'total':   'B08301_001',
        'car':     'B08301_002',
        'bus':     'B08301_011', 
        'subway':  'B08301_013',
        }
tables['travel_time'] = { # travel time to work
        'total': 'B08303_001',
        '-5':    'B08303_002',
        '5-9':   'B08303_003',
        '10-14': 'B08303_004',
        '15-19': 'B08303_005',
        '20-24': 'B08303_006',
        '25-29': 'B08303_007',
        '30-34': 'B08303_006',
        '35-39': 'B08303_007',
        '40-44': 'B08303_006',
        '45-59': 'B08303_007',
        '60-89': 'B08303_006',
        '90-':   'B08303_007'
        }
tables['income'] = {
        'median': 'B19013_001'
        }
tables['pop'] = {
        'total': 'B01003_001'
        }
tables['poverty'] = { # below or above poverty level
        'total': 'B17001_001',
        'below': 'B17001_002',
        'above': 'B17001_031'
        }
tables['units'] = { # units in structure
        'total':      'B25024_001',
        '1,detached': 'B25024_002',
        '1,attached': 'B25024_003',
        '2':          'B25024_004',
        '3/4':        'B25024_005',
        '5/9':        'B25024_006',
        '10/19':      'B25024_007',
        '20/49':      'B25024_008',
        '50-':        'B25024_009'
        }
tables['tenure'] = { # owned or rented
        'total':  'B25003_001',
        'owned':  'B25003_002',
        'rented': 'B25003_003'
        }
tables['rent'] = { # median gross rent
        'median': 'B25064_001'
        }


# df will collect all dataframes
df = {}
# each borough is separately requested
for c in counties.keys():
    county = counties[c]
    cdf = {}

    # request each table
    for t in tables.keys():
        table = tables[t]
        tdf = {}

        # request each table's columns
        for col in table.keys():
            column = table[col]

            # api request: all tracts, for a given table column, state, and
            # county
            r = base + '&get=%sE&for=tract:*&in=state:%s+county:%s' % (column, state, county)
            json = array(requests.get(r).json())
            data = json[1:,0].astype('float64')
            tdf[col] = Series(data)

        # convert to dataframe, record for each county
        tdf = DataFrame(tdf)
        tdf['tract'] = json[1:,3]
        tdf['borough'] = county_cat[c]
        cdf[t] = tdf
    # record each county
    df[c] = cdf

# combine all boroughs into one
dff = {}
for table in tables.keys():
    dff[table] = concat([df[county][table] for county in counties.keys()])
    dff[table].index = range(len(dff[table]))
dfs = dff
del dff
del df


# # set up main data frame
df = DataFrame(dfs['income']['tract'])

df['income'] = dfs['income']['median']
df['rent'] = dfs['rent']['median']
df['pop'] = dfs['pop']['total']
# proportion of homes that are occupied by owner
df['home_owned'] = dfs['tenure']['owned'] / dfs['tenure']['total']
# number of units in housing structure
df['<10_units'] = np.sum(dfs['units'][['1,detached','1,attached','2','3/4','5/9']].values,1) / dfs['units']['total']
df['10-50_units'] = np.sum(dfs['units'][['10/19','20/49']].values,1) / dfs['units']['total']
df['>50_units'] = dfs['units']['50-'] / dfs['units']['total']
# proportion of citizens below poverty level
df['poverty'] = dfs['poverty']['below'] / dfs['poverty']['total']
# proportion of commuters for bus, subway, car
df['car'] = dfs['means_transp']['car'] / dfs['means_transp']['total']
df['bus'] = dfs['means_transp']['bus'] / dfs['means_transp']['total']
df['subway'] = dfs['means_transp']['subway'] / dfs['means_transp']['total']
# commute times
df['<30_commute'] = np.sum(dfs['travel_time'][['-5','5-9','10-14','15-19','20-24','25-29']].values,1) / dfs['travel_time']['total']
df['30-60_commute'] = np.sum(dfs['travel_time'][['30-34','35-39','40-44','45-59']].values,1) / dfs['travel_time']['total']
df['60-90_commute'] = dfs['travel_time']['60-89'] / dfs['travel_time']['total']
df['>90_commute'] = dfs['travel_time']['90-'] / dfs['travel_time']['total']


df.pickle(open('data/save/census.p','wb'), df)
