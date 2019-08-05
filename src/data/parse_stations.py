import logging
import pandas as pd

logger = logging.getLogger(__name__)

STATIONS_RAW_FILE = r'data/raw/stations.txt'
DEFAULT_OUTPUT = r'data/interim/stations.csv'


def parse_stations(output_file=DEFAULT_OUTPUT):
    logger.info(f'Opening {STATIONS_RAW_FILE} for reading')
    f = open(STATIONS_RAW_FILE, 'r')
    stations = f.readlines()
    f.close()
    logger.info(f'Closed {STATIONS_RAW_FILE}')

    # splitting file into component parts
    column_names = stations[2]
    header_ruler = stations[3]
    data = stations[4:19377]

    # get location of all spaces in ruler
    # this indicates a character index to delimit at
    column_delims = [i for i, char in enumerate(header_ruler) if char == ' ']

    # add start and end
    column_delims = [0] + column_delims + [len(header_ruler) - 1]

    field_names = [
        column_names[column_delims[i]: column_delims[i+1]].strip()
        for i in range(len(column_delims) - 1)
    ]

    logger.info(f'parsed column names:\n\t {field_names}')

    # use delims and field names to build parsed dataset
    parsed_data = {}
    for i, field in enumerate(field_names):
        parsed_data[field] = []
        for row in data:
            parsed_data[field].append(
                row[column_delims[i]: column_delims[i+1]].strip())

    df = pd.DataFrame(parsed_data)

    logger.info('parsed dataset')
    logger.info(f'\n{df.head()}')

    df.to_csv(output_file, index=False)
    logger.info(f'saving parsed dataset to: {output_file}')


if __name__ == '__main__':
    parse_stations()
