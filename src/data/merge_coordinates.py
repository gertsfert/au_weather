import logging
import pandas as pd

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

logger = logging.getLogger(__name__)

STATIONS_PARSED = r'data/interim/stations.csv'
WEATHER_RAW = r'data/raw/weatherAus.csv'
OUTPUT_DEFAULT = r'data/processed/weather.csv'

HIGH_SIMILARITY_SCORE = 90


def avg_coords_most_common_district(df: pd.DataFrame):
    """ averages lat and long for the district with the most 
    entries in the input dataframe, returns as (lat, long) tuple"""
    logger.info('taking average coords of most frequent district')
    most_popular_district = df['Dist'].value_counts().index[0]
    averaged = df.loc[df['Dist'] ==
                      most_popular_district, ['Lat', 'Lon']].mean()

    return (averaged['Lat'], averaged['Lon'])


def merge_coordinates(output=OUTPUT_DEFAULT):
    # reading
    logger.info('reading input files')
    logger.info(f'\t {STATIONS_PARSED}')
    logger.info(f'\t {WEATHER_RAW}')
    stations = pd.read_csv(STATIONS_PARSED)
    weather = pd.read_csv(WEATHER_RAW)

    # fixing locations (let be kind on our fuzzy matcher eh?)
    weather['Location'] = weather['Location'].str.upper()
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

    # getting only current stations
    stations['End'] = stations['End'].replace({'..': '9999'})
    stations['End'] = stations['End'].astype(int)

    logger.info('filtered to current stations')
    current_stations = stations.loc[stations['End'] > 2018]

    # creating lookup table
    logger.info('building lookup table')
    lookup = pd.DataFrame({
        'Location': [],
        'is_matched': [],
        'match_type': [],
        'station_name': [],
        'lat': [],
        'lng': []})
    lookup['Location'] = list(weather['Location'].unique())

    for i, row in lookup.iterrows():
        location = row['Location']

        # make copy of stations for calc
        calc = current_stations.copy()

        exact_matches = calc.loc[calc['Site name'] == location]

        # fuzzy matches!
        calc['similarity'] = calc['Site name'].apply(
            lambda x: fuzz.token_set_ratio(x, location))

        matches = calc.loc[calc['similarity'] > HIGH_SIMILARITY_SCORE]

        # exact matches
        if len(exact_matches) == 1:
            # only one match - lock it in eddie
            row['is_matched'] = True
            row['match_type'] = 'exact'
            row['station_name'] = location
            row['lat'] = exact_matches.iloc[0]['Lat']
            row['lng'] = exact_matches.iloc[0]['Lon']

        elif len(exact_matches > 1):
            # found multiple exact matches
            lat, lng = avg_coords_most_common_district(exact_matches)

            row['is_matched'] = True
            row['match_type'] = 'avg_exact_match'
            row['station_name'] = location
            row['lat'] = lat
            row['lng'] = lng

        elif len(matches == 1):
            # found one high token match
            row['is_matched'] = True
            row['match_type'] = 'token_match'
            row['station_name'] = matches.iloc[0]['Site name']
            row['lat'] = matches.iloc[0]['Lat']
            row['lng'] = matches.iloc[0]['Lon']

        elif len(matches > 1):
            # found multiple high token matches
            lat, lng = avg_coords_most_common_district(matches)

            row['is_matched'] = True
            row['match_type'] = 'avg_token_match'
            row['station_name'] = matches.iloc[0]['Site name']
            row['lat'] = lat
            row['lng'] = lng

        # set row with values
        lookup.iloc[i] = row

    no_matches = lookup.loc[pd.isna(lookup['match_type'])]
    if len(no_matches) != 0:
        logger.warning('Some locations were not matched')
        logger.warning(no_matches)
    else:
        logger.info('All locations matched')
        logger.info(lookup['match_type'].value_counts())

    logger.info('joining to weather observations')
    weather = weather.merge(
        lookup[['Location', 'lat', 'lng']],
        on='Location',
        how='left')

    logger.info(f'outputting to {output}')
    weather.to_csv(output)
    logger.info(f'saved to file')
    logger.info(weather.head())


if __name__ == '__main__':
    merge_coordinates()
