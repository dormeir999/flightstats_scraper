"""
Functionality: create list of airports

Modul: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Airport data was taken from :https://ourairports.com/data/"
"""


import pandas as pd
import config_scraper as CFG


def get_airports():
    """takes a list of all airports and filters it to get only medium and large airports with following information:

    ['ident', 'type', 'name', 'elevation_ft', 'continent', 'iso_country', 'iso_region', 'municipality',
    'gps_code', 'iata_code', 'local_code', 'coordinates']
    """
    df = pd.read_csv(CFG.AIRPORTS_FILE_NAME,
                     na_values=['', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan',
                                '1.#IND', '1.#QNAN', '<NA>', 'N/A', 'NULL', 'NaN', 'n/a', 'nan',
                                'null'],
                     keep_default_na=False).dropna(axis=0,
                                                   how='any',
                                                   subset=['iata_code'])
    new = df[CFG.KEY_COORD].str.split(", ", n=1, expand=True)

    df['elevation_ft'].fillna(0, inplace=True)
    df[CFG.KEY_longitude] = new[CFG.FIRST_ITEM]
    df[CFG.KEY_latitude] = new[CFG.SECOND_ITEM]
    df = df.drop([CFG.KEY_COORD], axis=1)
    # df['iata_code'].dropna(inplace=True)
    df = df[df['type'] != 'closed']
    df = df[df['type'] != 'seaplane_base']
    df = df[df['type'] != 'heliport']

    df = df[df['iata_code'] != '0']

    return df


def get_iata_code():
    """
    Converts the airports data (ident, type, name, elevation, continent, iso country and region...) to csv,
    and removes rows with null values for iata_code.
    :return: a pandas DataFrame of airports data
    """
    return get_airports()[CFG.KEY_iata_code]


def main():

    df = get_airports()
    print(df)

if __name__ == "__main__":
    main()



