"""
CONFIGFILE: parsing
This config-file holds variables and magic numbers used for parsing in scraping scripts -> scrape_*.py

Module: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""

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

# magic numbers
FIRST_ITEM = 0
SECOND_ITEM = 1
THIRD_ITEM = 2
FOURTH_ITEM = 3