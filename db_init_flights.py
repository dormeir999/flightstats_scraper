"""
Functionality: This file contains functions to create the tables for the scraped flight data

Module: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""

import mysql.connector
from db_init import db_create_cursor


def create_tables_flights():
    """this function create the tables in the database flight_departures"""

    db, cur = db_create_cursor()

    # airports table
    cur.execute("""CREATE TABLE IF NOT EXISTS airport(
                type VARCHAR(255)
                ,  name VARCHAR(255)
                , elevation_ft INTEGER
                , continent VARCHAR(255)
                , iso_country VARCHAR(5), FOREIGN KEY (iso_country) REFERENCES country_airports(iso_country)
                , iso_region VARCHAR(255), FOREIGN KEY (iso_region) REFERENCES region_airports(iso_region)
                , municipality VARCHAR(255), FOREIGN KEY (municipality) REFERENCES city_airports(municipality)
                , gps_code VARCHAR(255)
                , iata_code VARCHAR(5) PRIMARY KEY
                , local_code VARCHAR(255)
                , longitude FLOAT
                , latitude FLOAT);""")

    try:
        cur.execute("CREATE UNIQUE INDEX idx_iata ON airports(iata_code)")
    except mysql.connector.errors.ProgrammingError as err:
        print(err)

    # departures table
    cur.execute("""CREATE TABLE IF NOT EXISTS departures(
                flight_id VARCHAR(255) PRIMARY KEY
                , departure_airport VARCHAR(10), FOREIGN KEY (departure_airport) REFERENCES airports(iata_code)
                , flight_number INTEGER
                , flight_status VARCHAR(255)
                , arrival_airport VARCHAR(10)
                , departure_date DATE
                , arrival_date DATE
                , operating_airline VARCHAR(255));""")

    try:
        cur.execute("CREATE UNIQUE INDEX idx_flight_id ON departures(flight_id)")
    except mysql.connector.errors.ProgrammingError as err:
        print(err)

    # events table
    cur.execute("""CREATE TABLE IF NOT EXISTS events(
                id INTEGER(255) PRIMARY KEY AUTO_INCREMENT
                , flight_id VARCHAR(255), FOREIGN KEY (flight_id) REFERENCES departures(flight_id)
                , event_time TIME
                , event_date DATE
                , event_type VARCHAR(255));""")

    try:
        cur.execute("CREATE INDEX idx_flight_id_event ON events(flight_id)")
    except mysql.connector.errors.ProgrammingError as err:
        print(err)



    db.commit()


def main():

    create_tables_flights()


if __name__ == '__main__':
    main()