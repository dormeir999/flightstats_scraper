"""
This config-file holds variables and magic numbers used by all database scripts -> db_*.py

Exercise: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""


# DB specifics:
host = "localhost"
user = "root"
pwd = 'flightscraper'
database = 'flight_departures'
logfile = 'fs_log.log'

# KEYS
key_dep_date = 'departure_date'
key_arr_date = 'arrival_date'
key_arr_airport = 'arrival_airport'
key_dep_airport = 'departure_airport'
key_flight_status = 'flight_status'
key_airline = 'operating_airline'
key_flight_number = 'flight_number'
key_flight_id = 'flight_id'
key_event_date = 'event_date'
key_event_time = 'event_time'
key_even_type = 'event_type'

# MAGIC NUMBERS
length_of_events = 3
first_elem = 0
second_elem = 1
third_elem = 2
iata_code = 9
coordinates = 11
elevation = 3
