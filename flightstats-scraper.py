"""
This scraper program recives a csv file of airports, scrape their recent departure flights data on flightstats.com,
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

# Constants
SPECIFIC_FLIGHT_IDENTIFIER = "flightId"
FLIGHT_INFO_TAG = "flight-details"
FLIGHT_TRACK_TAG = "flight-tracker"
URL_SPLIT_STR = "/v2"
URL_FLIGHT_DEPT = 'https://www.flightstats.com/v2/flight-tracker/departures/'
HTML_PARSER_STR = 'html.parser'
FLIGHT_TRACKER_STR = 'h2'
FLIGHT_NAME_STR = "h1"
FLIGHT_STAT_STR = "p"
AIRPORT_DEPT_STR = "h2"  # In a different context, it's also the flight tracker string (see above)
FLIGHTS_EVENTS_STR = 'rowData'
LARGE_AIRPORT_STR = 'large_airport'
MEDIUM_AIRPORT_STR = 'medium_airport'
HTML_LINKS_STR1 = 'a'
HTML_LINKS_STR2 = 'href'
IATA_FIELD_NO = 9
NO_FLIGHTS_MSG = 'No recent flights!'


def create_list_of_airports(filename):
    """takes a list of all airports and filters it to get only medium and large airports with following information:
    ['ident', 'type', 'name', 'elevation_ft', 'continent', 'iso_country', 'iso_region', 'municipality',
    'gps_code', 'iata_code', 'local_code', 'coordinates']
    """
    try:
        with open(filename, 'r', encoding="utf-8") as d:
            data = csv.reader(d)
            airports = [row for row in data]
        return [airport for airport in airports if airport[1] == LARGE_AIRPORT_STR or airport[1] == MEDIUM_AIRPORT_STR]
    except FileNotFoundError:
        print("The list of airports file " + str(filename) + " is not there - exiting the program")
        sys.exit()
    except UnicodeError:
        print("The list of airports file " + str(filename) + " is not in the write csv form - exiting the program")
        sys.exit()


def get_iata_code(airports):
    """creates an array with iata-codes and deletes airports without a code"""
    return [airport[IATA_FIELD_NO] for airport in airports if airport[IATA_FIELD_NO] != '']

def get_html_links(soup, only_one_page):
    """
    Recives the html page's soup, returns a list of the links in the html page
    :param soup: BeautifulSoup parsing input of the html page
    :return: the list of links in the html page (both flight and non flight links
    """
    # Get all the html's links, including the detailed websites on flights links
    if only_one_page:     # if only one page, the soup structure is different...
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
    url = str(URL_FLIGHT_DEPT) + str(airport)
    SITE_BASIC_PATH = url.split(URL_SPLIT_STR)[0]
    page = requests.get(url)
    html_list, num_of_pages = collect_flight_links(url)


    # Get all the html's links, including the detailed websites on flights links
    if not html_list:
        only_one_page = True
        links = get_html_links(BeautifulSoup(page.content, HTML_PARSER_STR), only_one_page)
        flight_links = filter_flights_links(links, SITE_BASIC_PATH)
        return flight_links , only_one_page

    only_one_page = False
    links = [get_html_links(BeautifulSoup(html, HTML_PARSER_STR), only_one_page) for html in html_list]
    flat_links = [item for sublist in links for item in sublist]

    # filter links for only the details about the flights links:
    flight_links = filter_flights_links(flat_links, SITE_BASIC_PATH)
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
    return [str(SITE_BASIC_PATH) + str(re.sub(FLIGHT_TRACK_TAG, FLIGHT_INFO_TAG, link)) for link in links if re.findall(SPECIFIC_FLIGHT_IDENTIFIER, link)]

def get_flight_details(soup):
    """
    Receives the soup of an html page of a flight link, and returns the flights details:
    [flight_name, flight_status, departure_airport, arrival_airport, departure_date, arrival_date, operating_airline]
    """
    flight_name = soup.find(FLIGHT_NAME_STR).string
    flight_status = soup.find(FLIGHT_STAT_STR).string
    departure_airport = soup.find_all(AIRPORT_DEPT_STR)[1].string
    arrival_airport = soup.find_all(AIRPORT_DEPT_STR)[3].string
    departure_date = soup.find_all(FLIGHT_STAT_STR)[3].string
    arrival_date = soup.find_all(FLIGHT_STAT_STR)[26].string
    operating_airline = soup.find_all(FLIGHT_STAT_STR)[48].string
    return [flight_name, flight_status, departure_airport, arrival_airport, departure_date, arrival_date, operating_airline]

def get_flight_events(soup):
    """
    Receives the soup of an html page of a flight link, and returns the flights events: [date, time, event]
    """
    a = soup.find_all(FLIGHT_STAT_STR, class_=FLIGHTS_EVENTS_STR)
    string_before = ""
    time_iter = -1
    flight_events = []
    for i, b in enumerate(a):
        if b.string is None:  # empty cell
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
        flight_details.append(get_flight_details(soup))   # Scrape for regular flight's details (name, destination, gate)
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


def scrape_flights(filename):
    """
    Receives a flie of airports, returns a list of datas about departing flights from those airports.
    """
    list_of_airports = get_iata_code(create_list_of_airports(filename))
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
    Tests the scraper, get's the airports file and performs the scraping, return the flights_data
    :return:
    """
    test_get_flights_links()
    filename = sys.argv[1]
    flights_data = scrape_flights(filename)
    return flights_data


if __name__ == '__main__':
    main()
