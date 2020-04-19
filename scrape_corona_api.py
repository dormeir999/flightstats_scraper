"""
This scraper program loads a csv file of airports, scrapes the recent corona data on https://www.trackcorona.live/api,
and returns 4 dataframes of Covid-19 data:
* iso_countries - latitude, longitude, confirmed cases, dead, recovered
* iso_regions - latitude, longitude, confirmed cases, dead, recovered
* cities -latitude, longitude, confirmed cases, dead, recovered
* iso_countries travel - travel limitation of iso_countries

Module: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""

import requests
import pandas as pd
import pycountry
from hdx.location.country import Country
import sys
import config_scraper as CFG
from list_airport_codes import get_airports

#
# AIRPORTS_FILE_NAME = "airport-codes.csv"
# FIRST_ITEM = 0
#
# # constants for scraping
# CITIES_URL = "https://www.trackcorona.live/api/cities"
# TRAVEL_URL = "https://www.trackcorona.live/api/travel"
# PROVINCE_URL = "https://www.trackcorona.live/api/provinces"
# COUNTRIES_URL = "https://www.trackcorona.live/api/countries"
# COUNTRIES_NO_AIRPORTS = ['VA', 'SM', 'AX', 'NA', 'LI']
# DATA_COLUMN_NAME = 'data'


def get_covid_data_countries(airports):
    """
    Scrapes trackcorona.live/api for covid-19 data on countries, and pre-process it to match the iso codes in airports
    :param airports: a pandas DataFrame of airports data (ident, type, name, elevation, continent, iso country...)
    :return: a pandas DataFrame of countries Covid-19 data (latitude, longitude, confirmed cases, dead, recovered)
    """
    try:
        countries = pd.DataFrame(requests.get(CFG.COUNTRIES_URL).json()[CFG.DATA_COLUMN_NAME])  # scrape the api
    except requests.exceptions.RequestException as e:
        print(f"{e} , exiting the program...")
        sys.exit()

    countries = countries.rename(columns={'country_code': 'iso_country'})
    countries['iso_country'] = countries.iso_country.transform(lambda x: str.upper(x))  # Capitalize country codes
    # Drop numeric county codes (numerics are stange places, and anyways airports country codes are only alphabet)
    countries = countries[countries.iso_country.str.isalpha()]
    # Drop countries without airports (Vatican City, San Marino, Liechtenstein), \
    # and countries that their airports are not in airports-codes.csv (Åland Islands, Namibia)
    countries = countries[~countries.iso_country.isin(CFG.COUNTRIES_NO_AIRPORTS)].drop(columns='location')
    # Make sure all countries are in airport-codes.csv file:
    # assert (countries.iso_country.isin(airports.iso_country)).all()

    return countries


def get_covid_data_regions(airports):
    """
    Scrapes trackcorona.live/api for covid-19 data on provinces, and pre-process it to match the iso_regions in airports
    :param airports: a pandas DataFrame of airports data (ident, type, name, elevation, continent, iso country...)
    :return: a pandas DataFrame of iso_regions Covid-19 data (latitude, longitude, confirmed cases, dead, recovered)
    """
    try:
        provinces = pd.DataFrame(requests.get(CFG.PROVINCE_URL).json()[CFG.DATA_COLUMN_NAME])
    except requests.exceptions.RequestException as e:
        print(f"{e} , exiting the program...")
        sys.exit()

    # Creating a provinces column in airports for later conversion of provinces.location to iso_region
    airports['provinces'] = [
        pycountry.subdivisions.get(code=x).name if pycountry.subdivisions.get(code=x) is not None else
        '' for x in airports.iso_region]
    # Setting manually iso_regions codes that had trouble being converted to region name
    regions_to_convert = {'DE-BR': 'Brandenburg', 'FR-E': 'Bretagne', 'FR-F': 'Centre-Val de Loire', 'CA-YT': 'Yukon',
                          'FR-B': 'Nouvelle-Aquitaine', 'FR-D': 'Bourgogne-Franche-Comté', 'VI-U-A': 'Virgin Islands',
                          'GU-U-A': 'Guam', 'PR-U-A': 'Puerto Rico', 'IN-MM': 'Maharashtra', 'IN-TG': 'Telengana',
                          'FR-R': 'Pays de la Loire', 'FR-P': 'Normandie', 'IN-UL': 'Uttarakhand',
                          'CH-GE': 'Auvergne-Rhône-Alpes', 'FR-O': 'Hauts-de-France', 'FR-J': 'Île-de-France',
                          'IN-NL': 'Nagaland', 'FR-N': 'Occitanie', 'BR-RR': 'Roraima', 'FR-H': 'Corsica',
                          'MP-U-A': 'Northern Mariana Islands', 'IN-TN': 'Tamil Nadu', 'IN-HR': 'Haryana',
                          'FR-M': 'Grand Est', 'US-AK': 'Alaska', 'IN-JK': 'Jammu and Kashmir'}
    for iso_code_region, region in regions_to_convert.items():
        airports.loc[airports.iso_region == iso_code_region, 'provinces'] = region
    # Drop duplicate location with typo(?), it also has no covid-19 cases
    provinces = provinces[provinces.location != 'Nagaland#']
    # Drop small location that in the same region as large location (but with same airport)
    provinces = provinces[provinces.location != 'Puducherry']
    provinces = provinces[provinces.location != 'Ladakh']
    # Drop not found region
    provinces = provinces[provinces.location != "Provence-Alpes-Côte d'Azur"]
    # Check that all provinces location are indeed in airports DataFrame
    # assert provinces.location.isin(airports['provinces']).all()
    # Resetting index before iterating on in
    provinces = provinces.reset_index(drop=True)
    # Convert every province to iso_region using airports['province']
    for i in range(len(provinces)):
        provinces['location'].replace(provinces['location'][i],
                                      airports.iso_region[airports['provinces'] == provinces.location[i]].min(),
                                      inplace=True)
    provinces = provinces.rename(columns={'location': 'iso_region'})

    return provinces


def get_covid_data_cities(airports):
    """
    Scrapes trackcorona.live/api for covid-19 data on cities
    :param airports: a pandas DataFrame of airports data (ident, type, name, elevation, continent, iso country...)
    :return: a pandas DataFrame of iso_regions Covid-19 data (latitude, longitude, confirmed cases, dead, recovered)
    """

    try:
        cities = pd.DataFrame(requests.get(CFG.CITIES_URL).json()[CFG.DATA_COLUMN_NAME])
    except requests.exceptions.RequestException as e:
        print(f"{e} , exiting the program...")
        sys.exit()

    return cities


def get_travel_restrictions(airports):
    """
    Scrapes trackcorona.live/api for covid-19 data on cities
    :param airports: a pandas DataFrame of airports data (ident, type, name, elevation, continent, iso country...)
    :return: a pandas DataFrame of iso_regions Covid-19 data (latitude, longitude, confirmed cases, dead, recovered)
    """
    travel = pd.DataFrame(requests.get(CFG.TRAVEL_URL).json()[CFG.DATA_COLUMN_NAME])

    iso_countries_codes = \
        [Country.get_iso2_from_iso3(Country.get_iso3_country_code_fuzzy(x)[CFG.FIRST_ITEM]) if
         Country.get_iso3_country_code_fuzzy(x)[CFG.FIRST_ITEM] else '' for x in travel['location']]

    travel['location'] = iso_countries_codes
    travel = travel.rename(columns={'location': 'iso_country'})

    return travel


def main():
    """
    Loads the airports data and uses it for scraping by iso_country, iso_region, cities and iso_country travel data
    :return: 4 dataframes of data about Covid-19: iso_country, iso_region, cities, and travel data of iso_country
    """
    airports = get_airports()

    # return get_covid_data_countries(airports), get_covid_data_regions(airports), get_covid_data_cities(airports), \
    #        get_travel_restrictions(airports)

    print(get_covid_data_countries(airports))
    print(get_covid_data_regions(airports).columns)
    print(get_covid_data_cities(airports).columns)
    print(get_travel_restrictions(airports).columns)

if __name__ == '__main__':
    main()
