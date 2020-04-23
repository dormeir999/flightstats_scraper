"""
This scraper program receives a csv file of airports, scrape their recent departure flights data on flightstats.com,
and returns available basic flight info (name, source and destination, time) and the flights registered events.

Exercise: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
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
import mysql.connector
from list_airport_codes import get_airports
import config_scraper as CFG

# constant for testing
TESTING_AIRPORT = 'ATL'

# constants for flights web urls
SPECIFIC_FLIGHT_IDENTIFIER = "flightId"
FLIGHT_INFO_TAG = "flight-details"
FLIGHT_TRACK_TAG = "flight-tracker"
URL_SPLIT_STR = "/v2"
URL_FLIGHT_DEPT = 'https://www.flightstats.com/v2/flight-tracker/departures/'

# constants used for html parsing
HTML_PARSER_STR = 'html.parser'
FLIGHT_TRACKER_STR = 'h2'
FLIGHT_NUMBER_STR = "h1"
FLIGHT_STAT_STR = "p"
AIRPORT_DEPT_STR = "h2"  # In a different context, it's also the flight tracker string (see above)
FLIGHTS_EVENTS_STR = 'rowData'
HTML_LINKS_STR1 = 'a'
HTML_LINKS_STR2 = 'href'
NO_FLIGHTS_MSG = 'No recent flights!'
AIRPORT_CODE_CLASS = "airportCodeTitle"
DATE_CLASS = "date"
FLIGHT_CARRIER_STRING = "h1"
FLIGHT_CARRIER_CLASS = "carrier-text-style"
FLIGHT_CARRIER_SPACE_STR = " "
FIRST_ITEM = 0
SECOND_ITEM = 1
THIRD_ITEM = 2
FOURTH_ITEM = 3
FLIGHT_NOT_IN_SYSTEM_STR = "h6"


# constants used for filtering iata codes
IATA_STR = 'iata_code'
TYPE_STR = 'type'
FEET_STR = 'elevation_ft'
COUNTR_STR = 'iso_country'
CONTIN_STR = 'continent'
EMPTY_AIRPORTS_INT = 0
NO_AIRPORTS_MSG = "No airports were found..."

# constants used for main()
CONTINENTS_2DIGITS = ['OC', 'AF', 'EU', 'AS', 'SA', 'AN']
ISO_COUNTRIES_CODES = ['US', 'PR', 'MH', 'MP', 'GU', 'SO', 'AQ', 'GB', 'PG', 'AD', 'SD',
       'SA', 'AE', 'SS', 'ES', 'CN', 'AF', 'LK', 'SB', 'CO', 'AU', 'MG',
       'TD', 'AL', 'AM', 'MX', 'MZ', 'PW', 'NR', 'AO', 'AR', 'AS', 'AT',
       'GA', 'AZ', 'BA', 'BE', 'DE', 'BF', 'BG', 'GL', 'BH', 'BI', 'IS',
       'BJ', 'OM', 'XK', 'BM', 'KE', 'PH', 'BO', 'BR', 'BS', 'CV', 'BW',
       'FJ', 'BY', 'UA', 'LR', 'BZ', 'CA', 'CD', 'CF', 'CG', 'MR', 'CH',
       'CL', 'CM', 'CR', 'CU', 'CY', 'CZ', 'SK', 'PA', 'DZ', 'ID', 'GH',
       'RU', 'CI', 'DK', 'NG', 'DO', 'NE', 'HR', 'TN', 'TG', 'EC', 'EE',
       'FI', 'EG', 'GG', 'JE', 'IM', 'FK', 'EH', 'NL', 'IE', 'FO', 'LU',
       'NO', 'PL', 'ER', 'MN', 'PT', 'SE', 'ET', 'LV', 'LT', 'ZA', 'SZ',
       'GQ', 'SH', 'MU', 'IO', 'ZM', 'FM', 'KM', 'YT', 'RE', 'TF', 'ST',
       'FR', 'SC', 'ZW', 'MW', 'LS', 'ML', 'GM', 'GE', 'GF', 'SL', 'NF',
       'GW', 'MA', 'GN', 'SN', 'GR', 'GT', 'TZ', 'GY', 'SR', 'DJ', 'HK',
       'LY', 'HN', 'VN', 'KZ', 'RW', 'HT', 'HU', 'UG', 'TL', 'IL', 'IN',
       'IQ', 'IR', 'JP', 'IT', 'JM', 'JO', 'KG', 'BD', 'KI', 'KH', 'KP',
       'KR', 'KW', 'LA', 'MY', 'PM', 'SI', 'PS', 'MT', 'MC', 'RO', 'LI',
       'TR', 'MD', 'MK', 'GI', 'RS', 'ME', 'TC', 'GD', 'MM', 'NI', 'SV',
       'MF', 'MV', 'KY', 'NC', 'CK', 'TO', 'TV', 'NU', 'WF', 'NP', 'WS',
       'PF', 'VU', 'NZ', 'LB', 'PK', 'SY', 'QA', 'YE', 'UM', 'PE', 'TH',
       'PY', 'TW', 'SG', 'VI', 'SM', 'UY', 'VE', 'AG', 'BB', 'DM', 'GP',
       'MQ', 'BL', 'TJ', 'KN', 'LC', 'TM', 'AW', 'BQ', 'CW', 'SX', 'AI',
       'MS', 'TT', 'VG', 'VC', 'UZ', 'VA', 'MO', 'BT', 'BN', 'CC', 'CX']
PARSER_DESCRIB = """Insert the filename of airport details.
                    and other optional filters. If you want to add filters, add the
                    filter flag and than each parameter with space:
                    scrape_flightstats.py airport-codes.csv {-type TYPE -country COUNTRY1 COUNTRY2 "-max-feet NUM -min-feet NUM}"""


def create_list_of_airports(filename, type, max_feet, min_feet, country, continent):
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
        airports = drop_nan_rows(pd.read_csv(filename), IATA_STR)  # Read airports file, drop airports without  \
        # iata code (since we can't scrape them from flightstats)
        try:
            airports_iata = filter_airports_iata(airports, type, max_feet, min_feet, country, continent)
            return airports_iata.values  # Return a list of filtered airports
        except UnicodeError:
            print("The list of airports file " + str(filename) + " is not in the write csv form - exiting the program")
            sys.exit()
    else:
        print(f"The {filename} doesn't exist, exiting the program...")
        sys.exit()

def filter_airports_iata(airports, type, max_feet, min_feet, country, continent):
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
    print("type: {}, maxfeet: {}, minfeet: {}, country: {}".format(type, max_feet, min_feet, country))
    airports_iata = airports[IATA_STR]  # get all codes
    # For each argument, if it has value - filter according to the value (drop the nans before the filter)
    if type:
        airports_iata = drop_nan_rows(airports, TYPE_STR)[IATA_STR][airports[TYPE_STR].isin(type)]
        airports = airports[airports[IATA_STR].isin(airports_iata)]
    if max_feet:
        airports_iata = drop_nan_rows(airports, FEET_STR)[IATA_STR][airports[FEET_STR] <= max_feet]
        airports = airports[airports[IATA_STR].isin(airports_iata)]
    if min_feet:
        airports_iata = drop_nan_rows(airports, FEET_STR)[IATA_STR][airports[FEET_STR] >= min_feet]
        airports = airports[airports[IATA_STR].isin(airports_iata)]
    if country:
        airports_iata = drop_nan_rows(airports, COUNTR_STR)[IATA_STR][airports[COUNTR_STR].isin(country)]
        airports = airports[airports[IATA_STR].isin(airports_iata)]
    if continent:
        airports_iata = drop_nan_rows(airports, CONTIN_STR)[IATA_STR][airports[CONTIN_STR].isin(continent)]
    if len(airports_iata) == EMPTY_AIRPORTS_INT:
        print(NO_AIRPORTS_MSG)
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
    :return: the list of links in the html page (both flight and non flight links
    """
    
    # Get all the html's links, including the detailed websites on flights links
    unparsed_list_of_links = list(soup.children)[only_one_page].find_all(HTML_LINKS_STR1)

    return [str(link.get(HTML_LINKS_STR2)) for link in unparsed_list_of_links]


def get_flights_links(airport):
    """
    Recieves the airport three letters name and returns the hyperlinks to the websites with full details
    on all departing flights from the airport in the flights stats website's first page (recent flights).
    :param airport: the airport three letters name, e.g. TLV
    :return: flight_links: a list of proper links to the flights departing from the airport in this moment.
    """
    # Variables for the links scrape and http request for data:

    url = os.path.join(URL_FLIGHT_DEPT, airport)
    site_basic_path = url.split(URL_SPLIT_STR)[0]
    page = requests.get(url)
    html_list, num_of_pages = collect_flight_links(url)

    # Get all the html's links, including the detailed websites on flights links
    if not html_list:
        only_one_page = True
        links = get_html_links(BeautifulSoup(page.content, HTML_PARSER_STR), only_one_page)
        flight_links = filter_flights_links(links, site_basic_path)
        return flight_links, only_one_page

    only_one_page = False
    links = [get_html_links(BeautifulSoup(html, HTML_PARSER_STR), only_one_page) for html in html_list]
    flat_links = [item for sublist in links for item in sublist]

    # filter links for only the details about the flights links:
    flight_links = filter_flights_links(flat_links, site_basic_path)
    print(flight_links)

    return flight_links, only_one_page


def filter_flights_links(links, URL_BASE):
    """
    Recives an html page's links and the flights stats home url path, and return the list of flights links
    :param links: a list of html pages' links, both flights and non-flights
    :param URL_BASE: the home URL of the flights stats website
    :return: a list of the only flights links in the html page.
    """
    #  This is a list comprehension that finds the flight track tag on all links with specific flight_identifier, and
    #  returns the proper address of the flight link

    out = [str(URL_BASE) + str(re.sub(FLIGHT_TRACK_TAG, FLIGHT_INFO_TAG, link))
           for link in links
           if re.findall(SPECIFIC_FLIGHT_IDENTIFIER, link)]

    return out


def get_flight_details(soup):
    """
    Receives the soup of an html page of a flight link, and returns the flights details.
    :param soup: html page of a flight link
    :return: list of data: [flight_number, flight_status, departure_airport, arrival_airport, departure_date,
                            arrival_date, operating_airline]
    """

    flight_details_dict = {'flight_number': soup.find(FLIGHT_CARRIER_STRING,
                                    class_=FLIGHT_CARRIER_CLASS).string.split(FLIGHT_CARRIER_SPACE_STR)[-FOURTH_ITEM],
                           'flight_status': soup.find(FLIGHT_STAT_STR).string,
                           'departure_airport': soup.find_all(AIRPORT_DEPT_STR,
                                                              class_=AIRPORT_CODE_CLASS)[FIRST_ITEM].string,
                           'arrival_airport': soup.find_all(AIRPORT_DEPT_STR,
                                                              class_=AIRPORT_CODE_CLASS)[SECOND_ITEM].string,
                           'departure_date': soup.find_all(FLIGHT_STAT_STR, class_=DATE_CLASS)[FIRST_ITEM].string,
                           'arrival_date': soup.find_all(FLIGHT_STAT_STR, class_=DATE_CLASS)[THIRD_ITEM].string,
                           'operating_airline': FLIGHT_CARRIER_SPACE_STR.join(soup.find(FLIGHT_CARRIER_STRING,
                                    class_=FLIGHT_CARRIER_CLASS).string.split(FLIGHT_CARRIER_SPACE_STR)[:-FOURTH_ITEM])}

    return flight_details_dict


def get_flight_events(soup):
    """
    Receives the soup of an html page of a flight link, and returns the flights events: [date, time, event]
    :param soup:
    :return: flight_events [date, time, event]
    """

    a = soup.find_all(FLIGHT_STAT_STR, class_=FLIGHTS_EVENTS_STR)
    string_before = ""
    time_iter = -1
    flight_events = []
    DIVISOR_UTC = 3
    MONTH_STRING_LENGTH = 3

    for i, b in enumerate(a):
        if not b.string:  # empty cell
            continue
        elif ":" in b.string:  # is time
            string_before = b.string
            time_iter += 1
            if time_iter % DIVISOR_UTC == 0:  # is UTC time
                flight_events.append(b.string)
            else:
                continue
        elif ":" in string_before:  # is event message
            string_before = b.string
            flight_events.append(b.string)
        elif len(b.string.split(" ")[SECOND_ITEM]) == MONTH_STRING_LENGTH:  # is date (len 3 is month short name)
            string_before = b.string
            flight_events.append(b.string)
    return flight_events


def get_flights_data(flight_links):
    """
    Receives a list of hyperlinks for full details of flights (times, date, flight events),
    and return (and print) a list of tuples, each tuple combines both flights details and flights events
    :param flight_links: a list of hyperlinks for the details of the departing flights
    :return: flights_data: a list of tuples, each tuple combines both flights details and flights events
    """

    if not flight_links[FIRST_ITEM]:
        return print(NO_FLIGHTS_MSG)
    flight_details, flight_events = [], []

    for flight_link in flight_links[FIRST_ITEM]: #[FIRST_ITEM]
        page = requests.get(flight_link)  # HTML request
        soup = BeautifulSoup(page.content, HTML_PARSER_STR)
        if soup.find(FLIGHT_NOT_IN_SYSTEM_STR):  # 'THIS FLIGHT COULD NOT BE LOCATED IN OUR SYSTEM'
            continue
        flight_detail_temp = get_flight_details(soup)
        flight_details.append(flight_detail_temp)  # Scrape for regular flight's details (name, destination, gate)

        flight_event_temp = get_flight_events(soup)
        flight_events.append(flight_event_temp)  # Scrape for before and during the flight

    flights_data = list(zip(flight_details, flight_events))  # zip the two data lists together
    print(flights_data)

    # FEED to DATABASE
    db_feed_flights_data(flights_data)
    print("data added to database")

    return flights_data


def test_get_flights_links():
    """
    Testing the primary functionality of the code - the first reach for the departures page in flightstats.
    We'll use the busiest airport in the world as of 2019 - Hartsfield–Jackson Atlanta International Airport - ATL.
    :return: If flight_links is not empty, 'The flightstats scraper is ready.'). else - fail.
    """
    airport = TESTING_AIRPORT
    print("TESTING: Getting all flights links from Atlanta airport:")
    flight_links = get_flights_links(airport)
    assert len(flight_links) > 0
    print('The flightstats Scraper is ready.')
    print('_________________________________')


def scrape_flights(filename, type, max_feet, min_feet, country, continent):
    """
    Receives a csv file (list of airports), returns a list of data about departing flights from those airports.
    :param filename:
    :return: flights_data for each airport in the list
    """
    list_of_airports = create_list_of_airports(filename, type, max_feet, min_feet, country, continent)
    print("Scraping the airports in the " + str(filename) + ":")
    print(list_of_airports)
    flights_data = []
    for airport in list_of_airports:
        print("_________________________________________")
        print("Scraping recent flights from " + str(airport) + " airport:")
        flights_data.append(get_flights_data(get_flights_links(airport)))

    return flights_data


def main():
    """
    Tests the scraper, handles filter arguments of airports and run the scraper
    :return:
    """
    # test scraper
    #test_get_flights_links()
    flight_links = ['https://www.flightstats.com/v2/flight-details/AC/9160?year=2020&month=4&date=23&flightId=1036465081',
     'https://www.flightstats.com/v2/flight-details/LH/8?year=2020&month=4&date=23&flightId=1036465081',
     'https://www.flightstats.com/v2/flight-details/NH/6071?year=2020&month=4&date=23&flightId=1036465081',
     'https://www.flightstats.com/v2/flight-details/LH/1212?year=2020&month=4&date=23&flightId=1036465104',
     'https://www.flightstats.com/v2/flight-details/AC/9279?year=2020&month=4&date=23&flightId=1036465104',
     'https://www.flightstats.com/v2/flight-details/LX/3661?year=2020&month=4&date=23&flightId=1036465104',
     'https://www.flightstats.com/v2/flight-details/NH/6179?year=2020&month=4&date=23&flightId=1036465104',
     'https://www.flightstats.com/v2/flight-details/LH/1008?year=2020&month=4&date=23&flightId=1036465087',
     'https://www.flightstats.com/v2/flight-details/AC/9318?year=2020&month=4&date=23&flightId=1036465087',
     'https://www.flightstats.com/v2/flight-details/NH/6169?year=2020&month=4&date=23&flightId=1036465087',
     'https://www.flightstats.com/v2/flight-details/SN/7002?year=2020&month=4&date=23&flightId=1036465087',
     'https://www.flightstats.com/v2/flight-details/LH/8402?year=2020&month=4&date=23&flightId=1036465216',
     'https://www.flightstats.com/v2/flight-details/LH/98?year=2020&month=4&date=23&flightId=1036465193',
     'https://www.flightstats.com/v2/flight-details/NH/6215?year=2020&month=4&date=23&flightId=1036465193',
     'https://www.flightstats.com/v2/flight-details/AC/9006?year=2020&month=4&date=23&flightId=1036465193',
     'https://www.flightstats.com/v2/flight-details/AC/9024?year=2020&month=4&date=23&flightId=1036465173',
     'https://www.flightstats.com/v2/flight-details/NH/6249?year=2020&month=4&date=23&flightId=1036465173',
     'https://www.flightstats.com/v2/flight-details/LH/1186?year=2020&month=4&date=23&flightId=1036465173',
     'https://www.flightstats.com/v2/flight-details/LX/3603?year=2020&month=4&date=23&flightId=1036465173',
     'https://www.flightstats.com/v2/flight-details/AA/9426?year=2020&month=4&date=23&flightId=1036522551',
     'https://www.flightstats.com/v2/flight-details/WY/116?year=2020&month=4&date=23&flightId=1036478907',
     'https://www.flightstats.com/v2/flight-details/LH/9596?year=2020&month=4&date=23&flightId=1036478907',
     'https://www.flightstats.com/v2/flight-details/LH/1506?year=2020&month=4&date=23&flightId=1036465170',
     'https://www.flightstats.com/v2/flight-details/DL/3341?year=2020&month=4&date=23&flightId=1036485495',
     'https://www.flightstats.com/v2/flight-details/DE/1502?year=2020&month=4&date=23&flightId=1036456323',
     'https://www.flightstats.com/v2/flight-details/UA/2789?year=2020&month=4&date=23&flightId=1036473863',
     'https://www.flightstats.com/v2/flight-details/UA/961?year=2020&month=4&date=23&flightId=1036474896',
     'https://www.flightstats.com/v2/flight-details/AC/5685?year=2020&month=4&date=23&flightId=1036474896',
     'https://www.flightstats.com/v2/flight-details/LH/7603?year=2020&month=4&date=23&flightId=1036474896',
     'https://www.flightstats.com/v2/flight-details/CI/62?year=2020&month=4&date=23&flightId=1036454869',
     'https://www.flightstats.com/v2/flight-details/GF/16?year=2020&month=4&date=23&flightId=1036460115',
     'https://www.flightstats.com/v2/flight-details/DL/3343?year=2020&month=4&date=23&flightId=1036523660',
     'https://www.flightstats.com/v2/flight-details/CX/14?year=2020&month=4&date=23&flightId=1036455053',
     'https://www.flightstats.com/v2/flight-details/KL/1766?year=2020&month=4&date=23&flightId=1036464676',
     'https://www.flightstats.com/v2/flight-details/AM/6218?year=2020&month=4&date=23&flightId=1036464676',
     'https://www.flightstats.com/v2/flight-details/CZ/7776?year=2020&month=4&date=23&flightId=1036464676',
     'https://www.flightstats.com/v2/flight-details/DL/9537?year=2020&month=4&date=23&flightId=1036464676',
     'https://www.flightstats.com/v2/flight-details/GA/9233?year=2020&month=4&date=23&flightId=1036464676',
     'https://www.flightstats.com/v2/flight-details/MF/9368?year=2020&month=4&date=23&flightId=1036464676',
     'https://www.flightstats.com/v2/flight-details/RU/418?year=2020&month=4&date=23&flightId=1036470781',
     'https://www.flightstats.com/v2/flight-details/UA/2777?year=2020&month=4&date=23&flightId=1036473790',
     'https://www.flightstats.com/v2/flight-details/UA/2789?year=2020&month=4&date=23&flightId=1036473863',
     'https://www.flightstats.com/v2/flight-details/UA/961?year=2020&month=4&date=23&flightId=1036474896',
     'https://www.flightstats.com/v2/flight-details/AC/5685?year=2020&month=4&date=23&flightId=1036474896',
     'https://www.flightstats.com/v2/flight-details/LH/7603?year=2020&month=4&date=23&flightId=1036474896',
     'https://www.flightstats.com/v2/flight-details/CI/62?year=2020&month=4&date=23&flightId=1036454869',
     'https://www.flightstats.com/v2/flight-details/GF/16?year=2020&month=4&date=23&flightId=1036460115',
     'https://www.flightstats.com/v2/flight-details/DL/3343?year=2020&month=4&date=23&flightId=1036523660',
     'https://www.flightstats.com/v2/flight-details/CX/14?year=2020&month=4&date=23&flightId=1036455053',
     'https://www.flightstats.com/v2/flight-details/KL/1766?year=2020&month=4&date=23&flightId=1036464676',
     'https://www.flightstats.com/v2/flight-details/AM/6218?year=2020&month=4&date=23&flightId=1036464676',
     'https://www.flightstats.com/v2/flight-details/CZ/7776?year=2020&month=4&date=23&flightId=1036464676',
     'https://www.flightstats.com/v2/flight-details/DL/9537?year=2020&month=4&date=23&flightId=1036464676',
     'https://www.flightstats.com/v2/flight-details/GA/9233?year=2020&month=4&date=23&flightId=1036464676',
     'https://www.flightstats.com/v2/flight-details/MF/9368?year=2020&month=4&date=23&flightId=1036464676',
     'https://www.flightstats.com/v2/flight-details/RU/418?year=2020&month=4&date=23&flightId=1036470781',
     'https://www.flightstats.com/v2/flight-details/UA/2777?year=2020&month=4&date=23&flightId=1036473790']
    scrape_flights('airport-codes.csv', ['large_airport'], 1000, 0, ['DE'], CONTINENTS_2DIGITS)
    # get_flights_data(flight_links)
    #
    # # arguments parsing
    # parser = argparse.ArgumentParser(description=PARSER_DESCRIB)
    # parser.add_argument("filename", type=str)
    # parser.add_argument("-type", type=str,  nargs='+', choices=['heliport', 'small_airport', 'closed', 'seaplane_base',
    #                                                   'balloonport', 'medium_airport', 'large_airport'])
    # parser.add_argument("-country", type=str, nargs='+', choices=ISO_COUNTRIES_CODES)
    # parser.add_argument("-continent", type=str, nargs='+', choices=CONTINENTS_2DIGITS)
    # parser.add_argument("-maxfeet", type=int)
    # parser.add_argument("-minfeet", type=int)
    # args = parser.parse_args()
    #
    # # running the scraper
    # flights_data = scrape_flights(args.filename, args.type, args.maxfeet, args.minfeet, args.country, args.continent)
    #
    # return flights_data


if __name__ == '__main__':
    main()
