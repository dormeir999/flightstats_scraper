"""
Functionality: This file contains functions to feed in the corona data scraped

Module: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""

import mysql.connector
from db_init import db_create_cursor


def create_conversion_tables():
    """this function creates a conversion table that connects the COVID19 tables with the airport table"""

    db, cur = db_create_cursor()

    # add iata code to the table and drop iso_region in the airports table?
    # iata_code
    # VARCHAR(10), FOREIGN
    # KEY(iata_code)
    # REFERENCES
    # airports(iata_code),

    #  country - airports conversion table:
    cur.execute("""CREATE TABLE IF NOT EXISTS country_airports(

                    iso_country VARCHAR(255) PRIMARY KEY
                    )""")
    try:
        cur.execute("CREATE INDEX idx_country ON country_airports(iso_country)")
    except mysql.connector.errors.ProgrammingError as err:
        print(err)


    # add iata code to the table and drop iso_region in the airports table?
    # iata_code
    # VARCHAR(10), FOREIGN
    # KEY(iata_code)
    # REFERENCES
    # airports(iata_code),

    # region - airports conversion table:
    cur.execute("""CREATE TABLE IF NOT EXISTS region_airports(
                    iso_region VARCHAR(255) PRIMARY KEY
                    )""")
    try:
        cur.execute("CREATE INDEX idx_region ON region_airports(iso_region)")
    except mysql.connector.errors.ProgrammingError as err:
        print(err)


    # add iata code to the table and drop municipality in the airports table?
    # iata_code
    # VARCHAR(10), FOREIGN
    # KEY(iata_code)
    # REFERENCES
    # airports(iata_code)

    # city - airports conversion table:
    cur.execute("""CREATE TABLE IF NOT EXISTS city_airports(
                    municipality VARCHAR(255) PRIMARY KEY
                    )""")
    try:
        cur.execute("CREATE INDEX idx_municipality ON city_airports(municipality)")
    except mysql.connector.errors.ProgrammingError as err:
        print(err)


def create_tables_covid19():
    """this function creates the tables containing the numbers of the COVID-19 pandemic"""

    db, cur = db_create_cursor()

    # corona per country table
    cur.execute("""CREATE TABLE IF NOT EXISTS covid19_country(
                id INTEGER PRIMARY KEY AUTO_INCREMENT 
                , iso_country VARCHAR(10), FOREIGN KEY (iso_country) REFERENCES country_airports(iso_country)
                , confirmed INTEGER
                , dead INTEGER
                , recovered INTEGER
                , updated TIMESTAMP
                , longitude FLOAT
                , latitude FLOAT
                , travel_restrictions VARCHAR(2000))""")

    try:
        cur.execute("CREATE INDEX idx_country_ ON covid19_country(iso_country)")
    except mysql.connector.errors.ProgrammingError as err:
        print(err)

    # corona per region table
    cur.execute("""CREATE TABLE IF NOT EXISTS covid19_region(
                id INTEGER PRIMARY KEY AUTO_INCREMENT
                , iso_region VARCHAR(50), FOREIGN KEY (iso_region) REFERENCES region_airports(iso_region)
                , confirmed INTEGER
                , dead INTEGER
                , recovered INTEGER
                , updated INTEGER
                , longitude FLOAT
                , latitude FLOAT)""")

    try:
        cur.execute("CREATE INDEX idx_region_ ON covid19_region(iso_region)")
    except mysql.connector.errors.ProgrammingError as err:
        print(err)

    # corona per city table
    cur.execute("""CREATE TABLE IF NOT EXISTS covid19_city(
                id INTEGER PRIMARY KEY AUTO_INCREMENT
                , location VARCHAR(200), FOREIGN KEY (location) REFERENCES city_airports(municipality)
                , confirmed INTEGER
                , dead INTEGER
                , recovered INTEGER
                , updated INTEGER
                , longitude FLOAT
                , latitude FLOAT)""")

    try:
        cur.execute("CREATE INDEX idx_location_ ON covid19_city(location)")
    except mysql.connector.errors.ProgrammingError as err:
        print(err)

    db.commit()


def main():

    create_conversion_tables()
    # create_conversion_tables()
    create_tables_covid19()


if __name__ == '__main__':
    main()