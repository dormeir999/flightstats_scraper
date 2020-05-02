"""
This scraper program has utils function for scrape_flightstats.py

Exercise: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 2.5.2020
"""

# Pre-requisites
import sys
import requests
from bs4 import BeautifulSoup
import re
from scrape_next_page import collect_flight_links
import os
import argparse
import pandas as pd
from db_feed_flights import db_feed_flights_data
import config_scraper as CFG


def create_list_of_airports(filename, type=None, max_feet=None, min_feet=None, country=None, continent=None):
    """
    Creates a list of airports from airports file and filters
    :param filename: airports.csv file of airports and their infos
    :param type: filter type (small, helicopter, etc...)
    :param max_feet: The highest elevation level of the airports, in feet
    :param min_feet: The lowest elevation level of the airports, in feet
    :param country: countries to filter
    :param continent: continents to filter
    :return: list of airports to scrape
    """
    if os.path.exists(filename):
        airports = drop_nan_rows(pd.read_csv(filename,
                     na_values=['', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan',
                                '1.#IND', '1.#QNAN', '<NA>', 'N/A', 'NULL', 'NaN', 'n/a', 'nan',
                                'null'],
                     keep_default_na=False).dropna(axis=0,
                                                   how='any',
                                                   subset=['iata_code']), CFG.IATA_STR)

        try:
            airports_iata = filter_airports_iata(airports, type, max_feet, min_feet, country, continent)
            return airports_iata.values  # Return a list of filtered airports
        except UnicodeError:
            print("The list of airports file " + str(filename) + " is not in the write csv form - exiting the program")
            sys.exit()
    else:
        print(f"The {filename} doesn't exist, exiting the program...")
        sys.exit()


def filter_airports_iata(airports, type=None, max_feet=None, min_feet=None, country=None, continent=None):
    """
    filter the list of all airports using airports data, and the filters below :
    :param airports: df of all airports details
    :param type: type of airport (small, helicopter, etc...)
    :param max_feet: The highest elevation level of the airports, in feet
    :param min_feet: The lowest elevation level of the airports, in feet
    :param country: countries to filter
    :param continent: continents to filter
    :return: a list of airports iata codes, filtered, and the filtered airports df
    """
    print("You are filtering airports with those parameters:")
    print("type: {}, maxfeet: {}, minfeet: {}, country: {}, continent: {}"
          .format(type, max_feet, min_feet, country, continent))
    airports_iata = airports[CFG.IATA_STR]  # get all codes
    # For each argument, if it has value - filter according to the value (drop the nans before the filter)

    for arg, aux_str in zip([type, country, continent], [CFG.TYPE_STR, CFG.COUNTR_STR, CFG.CONTIN_STR]):
        if arg:
            airports_iata = drop_nan_rows(airports, aux_str)[CFG.IATA_STR][airports[aux_str].isin(arg)]
            airports = airports[airports[CFG.IATA_STR].isin(airports_iata)]

    for i, arg in enumerate([max_feet, min_feet]):
        if arg:
            if i % 2 != 0:
                airports_iata = drop_nan_rows(airports, CFG.FEET_STR)[CFG.IATA_STR][airports[CFG.FEET_STR] >= arg]
            else:
                airports_iata = drop_nan_rows(airports, CFG.FEET_STR)[CFG.IATA_STR][airports[CFG.FEET_STR] <= arg]
            airports = airports[airports[CFG.IATA_STR].isin(airports_iata)]

    if len(airports_iata) == CFG.EMPTY_AIRPORTS_INT:
        print(CFG.NO_AIRPORTS_MSG)

    return airports_iata


def drop_nan_rows(df, column):
    """
    drop the nan's rows of a target column
    :param df: the df
    :param column: the target column of the df
    :return: the df without the rows that contain nan in the target column
    """
    return df.dropna(subset=[column])


def get_html_links(soup, only_one_page):
    """
    Recives the html page's soup, returns a list of the links in the html page
    :param soup: BeautifulSoup parsing input of the html page
    :param only_one_page: True if there's only one page of flights
    :return: the list of links in the html page (both flight and non flight links
    """

    # Get all the html's links, including the detailed websites on flights links
    unparsed_list_of_links = list(soup.children)[only_one_page].find_all(CFG.HTML_LINKS_STR1)

    return [str(link.get(CFG.HTML_LINKS_STR2)) for link in unparsed_list_of_links]


def get_flights_links(airport):
    """
    Recieves the airport three letters name and returns the hyperlinks to the websites with full details
    on all departing flights from the airport in the flights stats website's first page (recent flights).
    :param airport: the airport three letters name, e.g. TLV
    :return: flight_links: a list of proper links to the flights departing from the airport in this moment.
    """
    # Variables for the links scrape and http request for data:

    url = os.path.join(CFG.URL_FLIGHT_DEPT, airport)
    site_basic_path = url.split(CFG.URL_SPLIT_STR)[0]
    page = requests.get(url)
    html_list, num_of_pages = collect_flight_links(url)

    # Get all the html's links, including the detailed websites on flights links
    if not html_list:
        only_one_page = True
        links = get_html_links(BeautifulSoup(page.content, CFG.HTML_PARSER_STR), only_one_page)
        flight_links = filter_flights_links(links, site_basic_path)
        return flight_links, only_one_page

    only_one_page = False
    links = [get_html_links(BeautifulSoup(html, CFG.HTML_PARSER_STR), only_one_page) for html in html_list]
    flat_links = [item for sublist in links for item in sublist]

    # filter links for only the details about the flights links:
    flight_links = filter_flights_links(flat_links, site_basic_path)

    return flight_links, only_one_page


def filter_flights_links(links, site_basic_path):
    """
    Recives an html page's links and the flights stats home url path, and return the list of flights links
    :param links: a list of html pages' links, both flights and non-flights
    :param site_basic_path: the home URL of the flights stats website
    :return: a list of the only flights links in the html page.
    """
    #  This is a list comprehension that finds the flight track tag on all links with specific flight_identifier, and
    #  returns the proper address of the flight link

    out = [str(site_basic_path) + str(re.sub(CFG.FLIGHT_TRACK_TAG, CFG.FLIGHT_INFO_TAG, link))
           for link in links
           if re.findall(CFG.SPECIFIC_FLIGHT_IDENTIFIER, link)]

    return out


def test_get_flights_links():
    """
    Testing the primary functionality of the code - the first reach for the departures page in flightstats.
    We'll use the busiest airport in the world as of 2019 - Hartsfield–Jackson Atlanta International Airport - ATL.
    :return: If flight_links is not empty, 'The flightstats scraper is ready.'). else - fail.
    """
    airport = CFG.TESTING_AIRPORT
    print("TESTING: Getting all flights links from Atlanta airport:")
    flight_links = get_flights_links(airport)
    assert len(flight_links) > 0
    print('The flightstats Scraper is ready.')
    print('_________________________________')
