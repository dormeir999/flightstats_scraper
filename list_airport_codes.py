"""
Module: Data Mining
Functionality: create list of airports
Author: Dor Meir & Itamar Bergfreund
Date: 11. March 2020

Airport data was taken from :https://ourairports.com/data/"
"""


import csv


def create_list_of_airports(filename):
    """takes a list of all airports and filters it to get only medium and large airports with following information:

    ['ident', 'type', 'name', 'elevation_ft', 'continent', 'iso_country', 'iso_region', 'municipality',
    'gps_code', 'iata_code', 'local_code', 'coordinates']
    """

    with open(filename, 'r', encoding="utf-8") as d:
        data = csv.reader(d)
        airports = [row for row in data]

    return airports
    # return [airport for airport in airports if airport[1] == 'large_airport' or airport[1] == 'medium_airport']


def get_iata_code(airports):
    """creates an array with iata-codes and deletes airports without a code"""

    return [airport[9] for airport in airports if airport[9] != '']


def main():
    filename = 'airport-codes.csv'
    print(len(create_list_of_airports(filename)))
    print(get_iata_code(create_list_of_airports(filename)))

if __name__ == "__main__":
    main()



