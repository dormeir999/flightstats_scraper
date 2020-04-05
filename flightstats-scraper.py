"""
This scraper program receives a csv file of airports, scrape their recent departure flights data on flightstats.com,
and returns available basic flight info (name, source and destination, time) and the flights registered events.

Authors: Itamar Bergfreund & Dor Meir
"""

# Pre-requisites
import csv
import sys
import requests
from bs4 import BeautifulSoup
import re
from next_page import collect_flight_links
import os
import argparse
import pandas as pd


# constants for flights web urls
SPECIFIC_FLIGHT_IDENTIFIER = "flightId"
FLIGHT_INFO_TAG = "flight-details"
FLIGHT_TRACK_TAG = "flight-tracker"
URL_SPLIT_STR = "/v2"
URL_FLIGHT_DEPT = 'https://www.flightstats.com/v2/flight-tracker/departures/'

# constants used for html parsing
HTML_PARSER_STR = 'html.parser'
FLIGHT_TRACKER_STR = 'h2'
FLIGHT_NAME_STR = "h1"
FLIGHT_STAT_STR = "p"
AIRPORT_DEPT_STR = "h2"  # In a different context, it's also the flight tracker string (see above)
FLIGHTS_EVENTS_STR = 'rowData'
HTML_LINKS_STR1 = 'a'
HTML_LINKS_STR2 = 'href'
NO_FLIGHTS_MSG = 'No recent flights!'

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
    try:
        airports = drop_nan_rows(pd.read_csv(filename), IATA_STR)  # Read airports file, drop airports without  \
        # iata code (since we can't scrape them from flightstats)
        airports_iata = filter_airports_iata(airports, type, max_feet, min_feet, country, continent)
        return airports_iata.values  # Return a list of filtered airports
    except FileNotFoundError:
        print("The list of airports file " + str(filename) + " is not there - exiting the program")
        sys.exit()
    except UnicodeError:
        print("The list of airports file " + str(filename) + " is not in the write csv form - exiting the program")
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
    if only_one_page:  # if only one page, the soup structure is different...
        unparsed_list_of_links = list(soup.children)[1].find_all(HTML_LINKS_STR1)
    else:  # use the soup structure of multiple pages
        unparsed_list_of_links = list(soup.children)[0].find_all(HTML_LINKS_STR1)

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

    return flight_links


def filter_flights_links(links, SITE_BASIC_PATH):
    """
    Recives an html page's links and the flights stats home url path, and return the list of flights links
    :param links: a list of html pages' links, both flights and non-flights
    :param SITE_BASIC_PATH: the home URL of the flights stats website
    :return: a list of the only flights links in the html page.
    """
    #  This is a list comprehension that finds the flight track tag on all links with specific flight_identifier, and
    #  returns the proper address of the flight link
    return [str(SITE_BASIC_PATH) + str(re.sub(FLIGHT_TRACK_TAG, FLIGHT_INFO_TAG, link)) for link in links if
            re.findall(SPECIFIC_FLIGHT_IDENTIFIER, link)]


def get_flight_details(soup):
    """
    Receives the soup of an html page of a flight link, and returns the flights details:
    [flight_name, flight_status, departure_airport, arrival_airport, departure_date, arrival_date, operating_airline]
    """
    flight_details_dict = {'flight_name': soup.find(FLIGHT_NAME_STR).string,
                           'flight_status': soup.find(FLIGHT_STAT_STR).string,
                           'departure_airport': soup.find_all(AIRPORT_DEPT_STR)[1].string,
                           'arrival_airport': soup.find_all(AIRPORT_DEPT_STR)[3].string,
                           'departure_date': soup.find_all(FLIGHT_STAT_STR)[3].string,
                           'arrival_date': soup.find_all(FLIGHT_STAT_STR)[26].string,
                           'operating_airline': soup.find_all(FLIGHT_STAT_STR)[48].string}

    return flight_details_dict


def get_flight_events(soup):
    """
    Receives the soup of an html page of a flight link, and returns the flights events: [date, time, event]
    """
    a = soup.find_all(FLIGHT_STAT_STR, class_=FLIGHTS_EVENTS_STR)
    string_before = ""
    time_iter = -1
    flight_events = []
    for i, b in enumerate(a):
        if not b.string:  # empty cell
            continue
        elif ":" in b.string:  # is time
            string_before = b.string
            time_iter += 1
            if time_iter % 3 == 0:  # is UTC time
                flight_events.append(b.string)
            else:
                continue
        elif ":" in string_before:  # is event message
            string_before = b.string
            flight_events.append(b.string)
        elif len(b.string.split(" ")[1]) == 3:  # is date (len 3 is month short name)
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

    if not flight_links[0]:
        return print(NO_FLIGHTS_MSG)
    flight_details, flight_events = [], []

    for flight_link in flight_links[0]:
        page = requests.get(flight_link)  # HTML request
        soup = BeautifulSoup(page.content, HTML_PARSER_STR)
        flight_details.append(get_flight_details(soup))  # Scrape for regular flight's details (name, destination, gate)
        flight_events.append(get_flight_events(soup))  # Scrapte for before and during the flight

    flights_data = list(zip(flight_details, flight_events))  # zip the two data lists together
    print(flights_data)
    return flights_data


def test_get_flights_links():
    """
    Testing the primary functionality of the code - the first reach for the departures page in flightstats.
    We'll use the busiest airport in the world as of 2019 - Hartsfield–Jackson Atlanta International Airport - ATL.
    :return: If flight_links is not empty, 'The flightstats scraper is ready.'). else - fail.
    """
    airport = 'ATL'
    flight_links = get_flights_links(airport)
    print("TESTING: Getting all flights links from Atlanta airport:")
    assert len(flight_links) > 0
    print('The flightstats Scraper is ready.')
    print('_________________________________')


def scrape_flights(filename, type, max_feet, min_feet, country, continent):
    """
    Receives a flie of airports, returns a list of datas about departing flights from those airports.
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
    Handls filter arguments of airports and run the scraper
    :return:
    """

    # arguments parsing
    parser = argparse.ArgumentParser(description="Insert the filename of airport details."
                                                 "and other optional filters. If you want to add filters, add the"
                                                 " filter flag and than each parameter with space:"
                                                 "flightstats-scraper.py airport-codes.csv "
                                                 "{-type TYPE -country COUNTRY1 COUNTRY2"
                                                 "-max-feet NUM -min-feet NUM}")
    parser.add_argument("filename", type=str)
    parser.add_argument("-type", type=str,  nargs='+', choices=['heliport', 'small_airport', 'closed', 'seaplane_base',
                                                     'balloonport', 'medium_airport', 'large_airport'])
    parser.add_argument("-country", type=str, nargs='+', choices=ISO_COUNTRIES_CODES)
    parser.add_argument("-continent", type=str, nargs='+', choices=CONTINENTS_2DIGITS)
    parser.add_argument("-maxfeet", type=int)
    parser.add_argument("-minfeet", type=int)
    args = parser.parse_args()

    # running the scraper
    flights_data = scrape_flights(args.filename, args.type, args.maxfeet, args.minfeet, args.country, args.continent)

    return flights_data


if __name__ == '__main__':
    main()
