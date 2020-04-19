"""
Functionality: This file contains functions to create the tables for the scraped flight data

Module: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""

import mysql.connector
from db_init import db_create_cursor
import config_db as CFG


def create_tables_flights():
    """this function create the tables in the database flight_departures"""

    db, cur = db_create_cursor()

    # airports table
    cur.execute("""CREATE TABLE IF NOT EXISTS airports(
                type VARCHAR(255)
                ,  name VARCHAR(255)
                , elevation_ft INTEGER
                , continent VARCHAR(255)
                , iso_country VARCHAR(5), FOREIGN KEY (iso_country) REFERENCES covid19_country(iso_country)
                , iso_region VARCHAR(255), FOREIGN KEY (iso_region) REFERENCES covid19_region(iso_region)
                , municipality VARCHAR(255), FOREIGN KEY (municipality) REFERENCES covid19_city(location)
                , gps_code VARCHAR(255)
                , iata_code VARCHAR(10) PRIMARY KEY
                , local_code VARCHAR(255)
                , longitude FLOAT
                , latitude FLOAT)""")

    # events table
    cur.execute("""CREATE TABLE IF NOT EXISTS events(
                id INTEGER(255) PRIMARY KEY AUTO_INCREMENT
                , flight_id VARCHAR(255)
                , event_time TIME
                , event_date DATE
                , event_type VARCHAR(255))""")

    try:
        cur.execute("CREATE INDEX idx_flight ON events(flight_id)")
    except mysql.connector.errors.ProgrammingError as err:
        print(err)

    # departures table
    cur.execute("""CREATE TABLE IF NOT EXISTS departures(
                id INTEGER PRIMARY KEY AUTO_INCREMENT
                , flight_id VARCHAR(255), FOREIGN KEY (flight_id) REFERENCES events(flight_id)
                , departure_airport VARCHAR(10), FOREIGN KEY (departure_airport) REFERENCES airports(iata_code)
                , airline VARCHAR(50)
                , flight_number INTEGER
                , flight_status VARCHAR(255)
                , arrival_airport VARCHAR(10)
                , departure_date DATE
                , arrival_date DATE
                , operating_airline VARCHAR(255))""")

    try:
        cur.execute("CREATE UNIQUE INDEX idx_flight ON departures(flight_id)")
    except mysql.connector.errors.ProgrammingError as err:
        print(err)

    # # event_types
    # cur.execute("CREATE TABLE IF NOT EXISTS events_type("
    #             "id int PRIMARY KEY AUTO_INCREMENT"
    #             ", event_date DATE"
    #             ", event_time TIME"
    #             ", event_type VARCHAR(50))")

    db.commit()


def main():

    create_tables_flights()


if __name__ == '__main__':
    main()