"""
This script initializes a database to fill in the data scraped
DATABASE NAME: flight_departures

Authors: Itamar Bergfreund & Dor Meir
"""

import mysql.connector
from db_airports import db_create_cursor

# for config file
host="localhost"
user="root"
passwd='flightscraper'
database='flight_departures'
logfile = 'fs_log.log'


def database_init():

    db = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd
        )
    cur = db.cursor()

    try:
        cur.execute("CREATE DATABASE {}".format(database))
    except mysql.connector.Error as err:
        print("Failed to create database: {}".format(err))

    db.commit()


def create_tables():
    """this function create the tables in the database flight_departures"""

    db, cur = db_create_cursor()

    # airports table
    cur.execute("CREATE TABLE IF NOT EXISTS airports("
                "type VARCHAR(255)"
                ",  name VARCHAR(255)"
                ", elevation_ft INTEGER"
                ", continent VARCHAR(255)"
                ", iso_country VARCHAR(5)"
                ", iso_region VARCHAR(255)"
                ", municipality VARCHAR(255)"
                ", gps_code VARCHAR(255)"
                ", iata_code VARCHAR(10) PRIMARY KEY"
                ", local_code VARCHAR(255)"
                ", longitude FLOAT"
                ", latitude FLOAT)")

    # events table
    cur.execute("CREATE TABLE IF NOT EXISTS events("
                "id INTEGER(255) PRIMARY KEY AUTO_INCREMENT"
                ", flight_id VARCHAR(255)"
                ", event_time TIME"
                ", event_date DATE"
                ", event_type VARCHAR(255))")

    try:
        cur.execute("CREATE INDEX idx_flight ON events(flight_id)")
    except mysql.connector.errors.ProgrammingError:
        pass

    # departures table
    cur.execute("CREATE TABLE IF NOT EXISTS departures("
                "id INTEGER PRIMARY KEY AUTO_INCREMENT"
                ", flight_id VARCHAR(255), FOREIGN KEY (flight_id) REFERENCES events(flight_id)"
                ", departure_airport VARCHAR(10), FOREIGN KEY (departure_airport) REFERENCES airports(iata_code)"
                ", airline VARCHAR(50)"
                ", flight_number INTEGER"
                ", flight_status VARCHAR(255)"
                ", arrival_airport VARCHAR(10)"
                ", departure_date DATE"
                ", arrival_date DATE"
                ", operating_airline VARCHAR(255))")

    try:
        cur.execute("CREATE UNIQUE INDEX idx_flight ON departures(flight_id)")
    except mysql.connector.errors.ProgrammingError:
        pass

    # # event_types
    # cur.execute("CREATE TABLE IF NOT EXISTS events_type("
    #             "id int PRIMARY KEY AUTO_INCREMENT"
    #             ", event_date DATE"
    #             ", event_time TIME"
    #             ", event_type VARCHAR(50))")

    db.commit()


def main():
    database_init()
    create_tables()

if __name__ == '__main__':
    main()