"""
Functionality: This file contains functions to feed in the corona data scraped

Module: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""

import mysql.connector
from db_init import db_create_cursor


def create_tables_covid19():
    """this function creates the tables containing the numbers of the COVID-19 pandemic"""

    db, cur = db_create_cursor()

    # corona per country table
    cur.execute("""CREATE TABLE IF NOT EXISTS covid19_country(
                id INTEGER PRIMARY KEY AUTO_INCREMENT
                , iso_country VARCHAR(10)
                , confirmed INTEGER
                , dead INTEGER
                , recovered INTEGER
                , updated TIMESTAMP
                , longitude FLOAT
                , latitude FLOAT
                , travel_restrictions VARCHAR(500))""")

    try:
        cur.execute("CREATE INDEX idx_country ON covid19_country(iso_country)")
    except mysql.connector.errors.ProgrammingError as err:
        print(err)

    # corona per region table
    cur.execute("""CREATE TABLE IF NOT EXISTS covid19_region(
                id INTEGER PRIMARY KEY AUTO_INCREMENT
                , iso_region VARCHAR(50)
                , confirmed INTEGER
                , dead INTEGER
                , recovered INTEGER
                , updated TIMESTAMP
                , longitude FLOAT
                , latitude FLOAT)""")

    try:
        cur.execute("CREATE INDEX idx_region ON covid19_region(iso_region)")
    except mysql.connector.errors.ProgrammingError as err:
        print(err)

    # corona per city table
    cur.execute("""CREATE TABLE IF NOT EXISTS covid19_city(
                id INTEGER PRIMARY KEY AUTO_INCREMENT
                ,location VARCHAR(200) 
                , confirmed INTEGER
                , dead INTEGER
                , recovered INTEGER
                , updated TIMESTAMP
                , longitude FLOAT
                , latitude FLOAT)""")

    try:
        cur.execute("CREATE INDEX idx_location ON covid19_city(location)")
    except mysql.connector.errors.ProgrammingError as err:
        print(err)

    db.commit()


def main():

    create_tables_covid19()


if __name__ == '__main__':
    main()