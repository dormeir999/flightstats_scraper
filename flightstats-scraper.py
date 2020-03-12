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
    soup = BeautifulSoup(page.content, HTML_PARSER_STR)  # The html Parser

    # Get all the html's links, including the detailed websites on flights links
    links = []
    for link in list(soup.children)[1].find_all(HTML_LINKS_STR1):
            links.append(str(link.get(HTML_LINKS_STR2)))

    # filter links for only the details about the flights links:
    flight_links = []
    for link in links:
        if re.findall(SPECIFIC_FLIGHT_IDENTIFIER, link):
            details_link = re.sub(FLIGHT_TRACK_TAG, FLIGHT_INFO_TAG, link)
            flight_links.append(str(SITE_BASIC_PATH) + str(details_link))
    print(flight_links)
    return flight_links

def get_flights_details(flight_links):
    """
    Recieves a list of hyperlinks for full details about flights (times, date, flight events),
    and return a two lists of the details
    :param flight_links: a list of hyperlinks for the details of the departing flights
    :return: flight_details: details about flight name, status, travel info, operating airline
             flight_events: flights events details: day, hour in the day an message title.
    """
    flight_details = []
    flight_events = []

    # Scrape for regular flight details (flight_details)
    for link in flight_links:
        page = requests.get(link)  # HTML request
        soup = BeautifulSoup(page.content, HTML_PARSER_STR)
        flight_name = soup.find(FLIGHT_NAME_STR).string
        flight_status = soup.find(FLIGHT_STAT_STR).string
        departure_airport = soup.find_all(AIRPORT_DEPT_STR)[1].string
        arrival_airport = soup.find_all(AIRPORT_DEPT_STR)[3].string
        departure_date = soup.find_all(FLIGHT_STAT_STR)[3].string
        arrival_date = soup.find_all(FLIGHT_STAT_STR)[26].string
        operating_airline = soup.find_all(FLIGHT_STAT_STR)[48].string
        flight_details.append([flight_name, flight_status, departure_airport, arrival_airport, departure_date, arrival_date, operating_airline])

        # Scrape for flight events (flight_events)
        a = soup.find_all(FLIGHT_STAT_STR, class_=FLIGHTS_EVENTS_STR)
        string_before=""
        time_iter = -1
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

    return flight_details, flight_events


def combine_flights_data(flight_details, flight_events):
    """
    Recieves the two lists of scraped flights data and return a nested list, each line representing one flight
    :return: flights_data: all scraped data on flights
    """
    flights_data = []

    number_of_flights = len(flight_details)
    for i in range(number_of_flights):
        flights_data.append([flight_details[i], flight_events[i]])
        print(flights_data[i])
    return flights_data


def test_get_flights_links():
    """
    Testing the primary functionality of the code - the first reach for the departures page in flightstats.
    We'll use the busiest airport in the world as of 2019 - Hartsfield–Jackson Atlanta International Airport - ATL.
    :return: If flight_links is not empty, 'The flightstats scraper is ready.'). else - fail.
    """
    airport = 'ATL'
    flight_links = get_flights_links(airport)
    assert len(flight_links)>0
    print('The flightstats Scraper is ready.')

def scrape_flights(filename):
    list_of_airports = get_iata_code(create_list_of_airports(filename))
    print("Scraping the airports in the " + str(filename) + ":")
    print(list_of_airports)
    for airport in list_of_airports:
        print("Scraping recent flights from " + str(airport) + " airport:")
        flight_links = get_flights_links(airport)
        flight_details, flight_events = get_flights_details(flight_links)
        flights_data = combine_flights_data(flight_details, flight_events)
    return flights_data


def main():
    test_get_flights_links()
    filename = sys.argv[1]
    flights_data = scrape_flights(filename)
    return flights_data


if __name__ == '__main__':
    main()
