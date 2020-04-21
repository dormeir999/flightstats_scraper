"""
This config-file holds variables and magic numbers used by all database scripts -> db_*.py

Module: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""


# DB specifics:
host = "localhost"
user = "root"
pwd = 'flightscraper'
database = 'flights_data'
logfile = 'fs_log.log'

# KEYS
KEY_dep_date = 'departure_date'
KEY_arr_date = 'arrival_date'
KEY_arr_airport = 'arrival_airport'
KEY_dep_airport = 'departure_airport'
KEY_flight_status = 'flight_status'
KEY_airline = 'operating_airline'
KEY_flight_number = 'flight_number'
KEY_flight_id = 'flight_id'
KEY_event_date = 'event_date'
KEY_event_time = 'event_time'
KEY_even_type = 'event_type'
KEY_travel_restrictions = 'travel_restrictions'
KEY_country = 'iso_country'

# MAGIC NUMBERS
updated = 5
length_of_events = 3
first_elem = 0
second_elem = 1
third_elem = 2
iata_code = 9
coordinates = 11
elevation = 3
