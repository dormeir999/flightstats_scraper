"""
This scraper program receives a csv file of airports, scrape their recent departure flights data on flightstats.com,
and returns available basic flight info (name, source and destination, time) and the flights registered events.

Exercise: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""

# Pre-requisites
import requests
from bs4 import BeautifulSoup
import argparse
from db_feed_flights import db_feed_flights_data
import config_scraper as CFG
from utils import get_flights_links, create_list_of_airports


def get_flight_details(soup):
    """
    Receives the soup of an html page of a flight link, and returns the flights details.
    :param soup: html page of a flight link
    :return: list of data: [flight_number, flight_status, departure_airport, arrival_airport, departure_date,
                            arrival_date, operating_airline]
    """

    flight_details_dict = {'flight_number': soup.find(CFG.FLIGHT_CARRIER_STRING,
                        class_=CFG.FLIGHT_CARRIER_CLASS).string.split(CFG.FLIGHT_CARRIER_SPACE_STR)[-CFG.FOURTH_ITEM],
                           'flight_status': soup.find(CFG.FLIGHT_STAT_STR).string,
                           'departure_airport': soup.find_all(CFG.AIRPORT_DEPT_STR,
                                                              class_=CFG.AIRPORT_CODE_CLASS)[CFG.FIRST_ITEM].string,
                           'arrival_airport': soup.find_all(CFG.AIRPORT_DEPT_STR,
                                                              class_=CFG.AIRPORT_CODE_CLASS)[CFG.SECOND_ITEM].string,
                           'departure_date': soup.find_all(CFG.FLIGHT_STAT_STR,
                                                           class_=CFG.DATE_CLASS)[CFG.FIRST_ITEM].string,
                           'arrival_date': soup.find_all(CFG.FLIGHT_STAT_STR,
                                                         class_=CFG.DATE_CLASS)[CFG.THIRD_ITEM].string,
                           'operating_airline': CFG.FLIGHT_CARRIER_SPACE_STR.join(soup.find(CFG.FLIGHT_CARRIER_STRING,
                        class_=CFG.FLIGHT_CARRIER_CLASS).string.split(CFG.FLIGHT_CARRIER_SPACE_STR)[:-CFG.FOURTH_ITEM])}

    return flight_details_dict


def get_flight_events(soup):
    """
    Receives the soup of an html page of a flight link, and returns the flights events: [date, time, event]
    :param soup:
    :return: flight_events [date, time, event]
    """

    a = soup.find_all(CFG.FLIGHT_STAT_STR, class_=CFG.FLIGHTS_EVENTS_STR)
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
        elif len(b.string.split(" ")[CFG.SECOND_ITEM]) == MONTH_STRING_LENGTH:  # is date (len 3 is month short name)
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

    if not flight_links[CFG.FIRST_ITEM]:
        return print(CFG.NO_FLIGHTS_MSG)
    flight_details, flight_events = [], []

    for flight_link in flight_links[CFG.FIRST_ITEM]: #[FIRST_ITEM]
        page = requests.get(flight_link)  # HTML request
        soup = BeautifulSoup(page.content, CFG.HTML_PARSER_STR)
        if soup.find(CFG.FLIGHT_NOT_IN_SYSTEM_STR):  # 'THIS FLIGHT COULD NOT BE LOCATED IN OUR SYSTEM'
            continue
        flight_detail_temp = get_flight_details(soup)
        flight_details.append(flight_detail_temp)  # Scrape for regular flight's details (name, destination, gate)

        flight_event_temp = get_flight_events(soup)
        flight_events.append(flight_event_temp)  # Scrape for before and during the flight

    flights_data = list(zip(flight_details, flight_events))  # zip the two data lists together
    # print(flights_data)

    # FEED to DATABASE
    db_feed_flights_data(flights_data)
    print(f"{len(flight_links[CFG.FIRST_ITEM])} flights added to database")

    return flights_data


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

    # scrape_flights('airport-codes.csv', ['large_airport'], 1000, 0, ['DE'], CONTINENTS_2DIGITS)
    # get_flights_data(flight_links)
    #
    # arguments parsing
    parser = argparse.ArgumentParser(description=CFG.PARSER_DESCRIB)
    parser.add_argument("filename", type=str)
    parser.add_argument("-type", type=str,  nargs='+', choices=['heliport', 'small_airport', 'closed', 'seaplane_base',
                                                      'balloonport', 'medium_airport', 'large_airport'])
    parser.add_argument("-country", type=str, nargs='+', choices=CFG.ISO_COUNTRIES_CODES)
    parser.add_argument("-continent", type=str, nargs='+', choices=CFG.CONTINENTS_2DIGITS)
    parser.add_argument("-maxfeet", type=int)
    parser.add_argument("-minfeet", type=int)
    args = parser.parse_args()

    # running the scraper
    flights_data = scrape_flights(args.filename, args.type, args.maxfeet, args.minfeet, args.country, args.continent)
    #
    # return flights_data


if __name__ == '__main__':
    main()
