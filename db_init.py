"""
This script initializes a database to fill in the data scraped
DATABASE NAME: flights

Module: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""


import mysql.connector
import config_db as CFG


def database_init():
    """This function creates a database on you local host"""
    db = mysql.connector.connect(
        host=CFG.host,
        user=CFG.user,
        password=CFG.pwd
    )

    cur = db.cursor()

    try:
        cur.execute("CREATE DATABASE {}".format(CFG.database))
    except mysql.connector.Error as err:
        print("Failed to create database: {}".format(err))

    db.commit()


def db_create_cursor():
    """creates connection with database and creates a cursor
    :return db, cur
    """

    db = mysql.connector.connect(
        host=CFG.host,
        user=CFG.user,
        password=CFG.pwd,
        database=CFG.database)

    cur = db.cursor()
    return db, cur


def main():

    database_init()
    db_create_cursor()


if __name__ == '__main__':
    main()