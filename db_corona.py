"""
This file contains functions to feed in the corona data scraped

Exercise: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""

import mysql.connector
from list_airport_codes import create_list_of_airports
from datetime import datetime
from db_init import db_create_cursor
import config_db as CFG


