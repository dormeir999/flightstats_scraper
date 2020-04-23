"""
This file contains functions to feed in the COVID-19 data scraped

Module: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""

import mysql.connector
from list_airport_codes import get_airports
from db_init import db_create_cursor
import config_db as CFG
import scrape_corona_api as covid
import numpy as np


def db_feed_covid19_cities(df):
    """
    This function feeds the table covid19_city with the data scraped
    :param df: dataframe created with an API request
    :return: None
    """

    db, cur = db_create_cursor()
    query = """INSERT INTO covid19_city (location, latitude, longitude, confirmed, dead, recovered, updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""

    for index, data in df.iterrows():

        # todo: get NAN values into database as for now nan values are represented by 0
        data.fillna(0, inplace=True)
        food = tuple(data)
        # catch error if there are duplicates in the data set
        try:
            cur.execute(query, food)
        except mysql.connector.errors.IntegrityError as err:
            print("Error caught while updating covid19_city table: {}".format(err))

    db.commit()


def db_feed_covid19_countries(df):
    """
    This function feeds the table covid19_country with the data scraped
    :param df: dataframe created with an API request
    :return: None
    """

    db, cur = db_create_cursor()
    query = """INSERT INTO covid19_country (iso_country, latitude, longitude, confirmed, dead, recovered, updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""

    for index, data in df.iterrows():

        # todo: get NAN values into database as for now nan values are represented by 0
        data.fillna(0, inplace=True)
        food = tuple(data)

        # catch error if there are duplicates in the data set
        try:
            cur.execute(query, food)
        except mysql.connector.errors.IntegrityError as err:
            print(food)
            print("Error caught while updating covid19_country table: {}".format(err))

    db.commit()


def db_feed_covid19_region(df):
    """
    This function feeds the table covid19_region with the data scraped
    :param df: dataframe created with an API request
    :return: None
    """

    db, cur = db_create_cursor()
    query = """INSERT INTO covid19_region (iso_region, latitude, longitude, confirmed, dead, recovered, updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""

    for index, data in df.iterrows():

        # todo: get NAN values into database as for now nan values are represented by 0
        data.fillna(0, inplace=True)
        food = tuple(data)
        # catch error if there are duplicates in the data set
        try:
            cur.execute(query, food)
        except mysql.connector.errors.IntegrityError as err:
            print(food)
            print("Error caught while updating covid19_region table: {}".format(err))

    db.commit()


def db_feed_covid19_travel_restrictions(df):
    """
    This function feeds the table covid19_country with the travel restrictions scraped
    :param df: dataframe created with an API request
    :return: None
    """

    db, cur = db_create_cursor()
    table = 'covid19_country'

    for index, country in df.iterrows():

        # check for last entry in covid19_country table:
        is_observation = db_select_country_data(country[CFG.KEY_country])
        data = (country['data'].replace("\'", ''))
        # print(airport_type(is_observation[CFG.first_elem][CFG.updated]))
        if is_observation:
            stmt = f"""UPDATE {table} SET
                   travel_restrictions='{data}'
                   WHERE
                   '{CFG.KEY_country}'='{country[CFG.KEY_country]}' AND
                   updated='{is_observation[CFG.first_elem][CFG.updated]}';"""
            cur.execute(stmt)


def db_select_country_data(country):
    """
    This function creates a SQL query given a country returns the last entry created.
    :param country: iso_country
    :return: result of the SQL query
    """

    table = 'covid19_country'
    db, cur = db_create_cursor()


    stmt = f"SELECT * " \
           f"FROM {table} " \
           f"WHERE iso_country='{country}' ORDER BY updated DESC LIMIT 1;"
    cur.execute(stmt)

    return cur.fetchall()


def main():
    # some test data

    airports = get_airports()

    # df_cities = covid.get_covid_data_cities(airports)
    df_regions = covid.get_covid_data_regions(airports)
    df_countries = covid.get_covid_data_countries(airports)
    df_tr = covid.get_travel_restrictions(airports)

    db_feed_covid19_countries(df_countries)
    print('countries done')
    db_feed_covid19_region(df_regions)
    print('regions done')
    # db_feed_covid19_cities(df_cities)
    print('cities done')
    db_feed_covid19_travel_restrictions(df_tr)
    print('travel restrictions done')

    print('done')


if __name__ == '__main__':
    main()
