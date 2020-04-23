"""
This utils program contains util functions for the scrape_flightstats.py file.

Exercise: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 23.04.2020
"""

import config_scraper as CFG
import pandas as pd
import re
from scrape_next_page import collect_flight_links
import os
import sys
import requests
from bs4 import BeautifulSoup


def create_list_of_airports(filename, airport_type, max_feet, min_feet, country, continent):
    """
    Creates a list of airports from airports file and filters
    :param filename: airports.csv file of airports and their infos
    :param airport_type: filter airport_type (small, helicopter, etc...)
    :param max_feet: The highest elevation level of the airports, in feet
    :param min_feet: The lowest elevation level of the airports, in feet
    :param country: countries to filter
    :param continent: continents to filter
    :return: list of airports to scrape
    """
    if os.path.exists(filename):
        airports = drop_nan_rows(pd.read_csv(filename), CFG.IATA_STR)  # Read airports file, drop airports without  \
        # iata code (since we can't scrape them from flightstats)
        try:
            airports_iata = filter_airports_iata(airports, airport_type, max_feet, min_feet, country, continent)
            return airports_iata.values  # Return a list of filtered airports
        except UnicodeError:
            print("The list of airports file " + str(filename) + " is not in the write csv form - exiting the program")
            sys.exit()
    else:
        print(f"The {filename} doesn't exist, exiting the program...")
        sys.exit()


def filter_airports_iata(airports, airport_type, max_feet, min_feet, country, continent):
    """
    filter the list of all airports using airports data, and the filters below :
    :param airports: df of all airports details
    :param airport_type: airport_type of airport (small, helicopter, etc...)
    :param max_feet: The highest elevation level of the airports, in feet
    :param min_feet: The lowest elevation level of the airports, in feet
    :param country: countries to filter
    :param continent: continents to filter
    :return: a list of airports iata codes, filtered, and the filtered airports df
    """
    print("You are filtering airports with those parameters:")
    print("airport_type: {}, maxfeet: {}, minfeet: {}, country: {}".format(airport_type, max_feet, min_feet, country))
    airports_iata = airports[CFG.IATA_STR]  # get all codes
    # For each argument, if it has value - filter according to the value (drop the nans before the filter)
    if airport_type:
        airports_iata = drop_nan_rows(airports, CFG.TYPE_STR)[CFG.IATA_STR][airports[CFG.TYPE_STR].isin(airport_type)]
        airports = airports[airports[CFG.IATA_STR].isin(airports_iata)]
    if max_feet:
        airports_iata = drop_nan_rows(airports, CFG.FEET_STR)[CFG.IATA_STR][airports[CFG.FEET_STR] <= max_feet]
        airports = airports[airports[CFG.IATA_STR].isin(airports_iata)]
    if min_feet:
        airports_iata = drop_nan_rows(airports, CFG.FEET_STR)[CFG.IATA_STR][airports[CFG.FEET_STR] >= min_feet]
        airports = airports[airports[CFG.IATA_STR].isin(airports_iata)]
    if country:
        airports_iata = drop_nan_rows(airports, CFG.COUNTR_STR)[CFG.IATA_STR][airports[CFG.COUNTR_STR].isin(country)]
        airports = airports[airports[CFG.IATA_STR].isin(airports_iata)]
    if continent:
        airports_iata = drop_nan_rows(airports, CFG.CONTIN_STR)[CFG.IATA_STR][airports[CFG.CONTIN_STR].isin(continent)]
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
    :param soup: BeautifulSoup parsing input of the html page,
    :param only_one_page: True if no need to use scraper_next_page
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
    site_basic_path = url.split(CFG.URL_SPLIT_STR)[CFG.FIRST_ITEM]
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
    print(flight_links)

    return flight_links


def filter_flights_links(links, site_basic_path):
    """
    Recives an html page's links and the flights stats home url path, and return the list of flights links
    :param site_basic_path:
    :param links: a list of html pages' links, both flights and non-flights
    :param URL_BASE: the home URL of the flights stats website
    :return: a list of the only flights links in the html page.
    """
    #  This is a list comprehension that finds the flight track tag on all links with specific flight_identifier, and
    #  returns the proper address of the flight link

    out = [str(site_basic_path) + str(re.sub(CFG.FLIGHT_TRACK_TAG, CFG.FLIGHT_INFO_TAG, link))
           for link in links
           if re.findall(CFG.SPECIFIC_FLIGHT_IDENTIFIER, link)]

    return out
