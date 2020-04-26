"""
This script initializes a database to fill in the data scraped
DATABASE NAME: flights

Module: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""


import db_init as init
import db_init_flights as fl
import db_init_corona as covid
import db_feed_flights as feed


def start_db():
    """This function need to be run once to initialize the database"""
    init.database_init()
    print('created database flight_data')
    covid.create_conversion_tables()
    print('created conversion tables')
    covid.create_tables_covid19()
    print('created covid19 tables')
    fl.create_tables_flights()
    print('created flights tables')
    feed.db_insert_conversion_tables()
    print('fed conversion tables')
    feed.db_insert_airports()
    print('fed airports table')


def main():
    start_db()


if __name__ == '__main__':
    main()