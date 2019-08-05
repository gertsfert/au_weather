# %% [markdown]
# # Stations and Measurements
# Aim is to see if the `stations` dataset can be combined with the `weatherAus` dataset
# Will allow for location analysis among other lovely things

import pandas as pd

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

stations = pd.read_csv(r'data/interim/stations.csv')
weather = pd.read_csv(r'data/raw/weatherAus.csv')
weather['Location'] = weather['Location'].str.upper()

# %% adding spaces where it makes sense
weather['Location'] = weather['Location'].replace({
    'BADGERYSCREEK': 'BADGERYS CREEK',
    'COFFSHARBOUR': 'COFFS HARBOUR',
    'NORAHHEAD': 'NORAH HEAD',
    'NORFOLKISLAND': 'NORFOLK ISLAND',
    'SYDNEYAIRPORT': 'SYDNEY AIRPORT',
    'WAGGAWAGGA': 'WAGGA WAGGA',
    'MOUNTGININI': 'MOUNT GININI',
    'MELBOURNEAIRPORT': 'MELBOURNE AIRPORT',
    'GOLDCOAST': 'GOLD COAST',
    'MOUNTGAMBIER': 'MOUNT GAMBIER',
    'PERTHAIRPORT': 'PERTH AIRPORT',
    'SALMONGUMS': 'SALMON GUMS',
    'ALICESPRINGS': 'ALICE SPRINGS',
    'NHIL': 'NHILL',
    'WATSONIA': 'MELBOURNE'  # suburb in melbourne
})

# %% fixing years
stations['Start'] = stations['Start'].astype(int)

stations['End'] = stations['End'].replace({'..': '9999'})
stations['End'] = stations['End'].astype(int)

current_stations = stations.loc[stations['End'] > 2018]

# %%
locations = [name.upper() for name in weather['Location'].unique()]
station_names = list(current_stations['Site name'].unique())

# %% [markdown]
# # Matching Strategy
# 1. Check for exact matches
# 2. Check for 100 fuzz.token_set_ratio match
# 3. Check for high (> 90) fuzz.token_set_ratio matches
#    - If multiple matches: group by similar coordinates - and choose mean of
# most similar points

# creating lookup table
lookup = pd.DataFrame({
    'location': [],
    'is_matched': [],
    'match_type': [],
    'station_name': [],
    'lat': [],
    'lng': []})

lookup['location'] = locations

for i, row in lookup.iterrows():
    location = row[0]

    exact_matches = current_stations.loc[
        current_stations['Site name'] == location]

    if len(exact_matches) == 1:
        # found exact match
        row['is_matched'] = True
        row['match_type'] = 'exact'  # match type
        row['station_name'] = location
        row['lat'] = exact_matches['Lat']
        row['lng'] = exact_matches['Lon']

        lookup.iloc[i] = row

    elif len(exact_matches) > 1:
        # found more than one exact match!
        print('duplicates found!')
        duplicates = exact_matches.copy()
        break

    else:
        # check for 100 points in token similarity
        calc = current_stations.copy()
        calc['similarity'] = calc['Site name'].apply(
            lambda x: fuzz.token_set_ratio(x, location))

        matches = calc.loc[calc['similarity'] > 90]

        if len(matches) == 1:
            # found exact match
            row['is_matched'] = True
            row['match_type'] = 'token_match'
            row['station_name'] = matches.iloc[0]['Site name']
            row['lat'] = matches['Lat']
            row['lng'] = matches['Lon']
            lookup.iloc[i] = row
        elif len(matches) > 1:
            # found more than 1 perfect match!

            # find most popular district
            most_popular_district = matches['Dist'].value_counts().index[0]
            averaged = matches.loc[matches['Dist'] ==
                                   most_popular_district, ['Lat', 'Lon']].mean()

            row['is_matched'] = True
            row['match_type'] = 'avg_token_match'
            row['station_name'] = location
            row['lat'] = averaged['Lat']
            row['lng'] = averaged['Lon']

            lookup.iloc[i] = row


lookup['match_type'].value_counts(dropna=False)


# %% Add coordinates back in
weather = weather.merge(
    lookup[['location', 'lat', 'lng']], left_on='Location', right_on='location')
