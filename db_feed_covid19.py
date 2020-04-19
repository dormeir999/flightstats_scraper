"""
This file contains functions to feed in the COVID-19 data scraped

Module: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""

import mysql.connector
from list_airport_codes import get_airports
from datetime import datetime
from db_init import db_create_cursor
import config_db as CFG
import scra


def db_feed_covid19_cities():
    """This function creates a table (airports) in the database flights_departures"""


    db, cur = db_create_cursor()

    query = """INSERT INTO covid19_city (location, confirmed, dead, recovered, updated, longitude, latitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""


    for index, data in airports.iterrows():

        food = tuple(data)[CFG.second_elem]

        # catch error if there are duplicates in the data set
        try:
            cur.execute(query, food)
        except mysql.connector.errors.IntegrityError as err:
            print("Error caught while updating covid19_city table: {}".format(err))
    db.commit()


def db_insert_flights(flight_data):
    """This function takes the a flight data dictionary as an input and feeds it into the database table departures.
    :param flight_data: e.g.
                    {'flight_number': '425',
                    'flight_status': 'On time | Scheduled',
                    'departure_airport': 'TLV',
                    'arrival_airport': 'ETM',
                    'departure_date': '12-Apr-2020',
                    'arrival_date': '12-Apr-2020',
                    'operating_airline': '(6H) Israir Airlines'}"""

    table = 'departures'
    dep_airport = flight_data[CFG.key_dep_airport]
    flight_id = flight_data[CFG.key_flight_id]
    flight_status = flight_data[CFG.key_flight_status]
    arrival_airport = flight_data[CFG.key_arr_airport]
    departure_date = flight_data[CFG.key_dep_date]
    arrival_date = flight_data[CFG.key_arr_date]
    operating_airline = flight_data[CFG.key_airline]
    flight_number = flight_data[CFG.key_flight_number]

    db, cur = db_create_cursor()

    # change type of data from bs4.element.NavigableString to string
    for e in flight_data.keys():
        flight_data[e] = str(flight_data[e])

    # check if there is an entry for this data:
    is_observation = db_select_flight(dep_airport, flight_id)

    if is_observation:
        stmt = f"""UPDATE {table} SET 
               f"{CFG.key_flight_status} = {flight_status}, 
               f"'" {CFG.key_dep_date} = {departure_date}, 
               f"{CFG.key_arr_airport} = {arrival_airport},
               f"{CFG.key_arr_date} = {arrival_date}, 
               f"{CFG.key_airline} = {operating_airline}, 
               f"{CFG.key_flight_number} = {flight_number} 
               f"WHERE 
               f"{CFG.key_dep_airport}={dep_airport} AND {CFG.key_flight_id}={flight_id};"""
        cur.execute(stmt)

    else:
        placeholder = ", ".join(["%s"] * len(flight_data))
        stmt = "INSERT INTO {table} ({columns}) VALUES ({values});".format(table=table,
                                                                           columns=",".join(flight_data.keys()),
                                                                           values=placeholder)
        try:
            cur.execute(stmt, list(flight_data.values()))
        except mysql.connector.errors.IntegrityError as err:
            print(stmt)
            print(list(flight_data.values()))
            print("Error caught while inserting flights table: {}".format(err))
    db.commit()


def db_insert_events(events_data):
    """This function takes the a event data dictionary as an input and feeds it into the database table events.
    :param events_data: (flight_id, event_date, event_time, event_type)"""

    # change type of data from bs4.elemnt.NavigableString to string
    events_data = tuple([str(e) for e in events_data])

    length = len(events_data)
    event_date = events_data[CFG.second_elem]
    flight_id = events_data[CFG.first_elem]

    db, cur = db_create_cursor()
    table = 'events'

    is_observation = db_select_event(flight_id, event_date)

    if is_observation:
        pass
    else:
        placeholder = ", ".join(["%s"] * length)
        smt = "INSERT INTO {table} ({columns}) values ({values});".format(table=table,
                                                                          columns=f'{CFG.key_flight_id},'
                                                                                  f'{CFG.key_event_date},'
                                                                                  f'{CFG.key_event_time},'
                                                                                  f'{CFG.key_even_type}'
                                                                          , values=placeholder)
        try:
            cur.execute(smt, events_data)
        except mysql.connector.errors.IntegrityError as err:
            print("Error while inserting events data: {}".format(err))
    db.commit()


def create_flight_id(flight_data):
    """
    this function creates a unique key: flight_id and adds it to the flight_data that consists of
    flight_number, operating_airline, departure_date
    :param flight_data:
    :return: flight_data with new unique field, flight_id
    """

    flight_data[CFG.key_flight_id] = '_'.join([flight_data[CFG.key_airline], flight_data[CFG.key_flight_number],
                                               flight_data[CFG.key_dep_date]])

    # create date from string:
    flight_data[CFG.key_dep_date] = datetime.strptime(flight_data[CFG.key_dep_date], '%d-%b-%Y')
    flight_data[CFG.key_arr_date] = datetime.strptime(flight_data[CFG.key_arr_date], '%d-%b-%Y')

    return flight_data


def db_feed_flights_data(flights_data):
    """
    This function takes the data scraped per airport and loops over every flight in the data
    :param flights_data:
    :return: no output
    """

    for flight_data in flights_data:
        events_data = flight_data[CFG.second_elem]
        flight_data = flight_data[CFG.first_elem]
        flight_data = create_flight_id(flight_data)

        # prepare events_data:
        for i in range(0, len(events_data), CFG.length_of_events):
            now = datetime.now()
            event_date = datetime.strptime(events_data[i] + '-' + str(now.year) + '-' + events_data[i + 1]
                                           , '%d %b-%Y-%H:%M')

            event_data = (flight_data[CFG.key_flight_id], event_date, events_data[i + CFG.second_elem],
                          events_data[i + CFG.third_elem])

            # inserting event_data
            db_insert_events(event_data)

        # inserting flight data
        db_insert_flights(flight_data)


def db_select_flight(airport, flight_id):
    """
    This function creates a SQL query given a flight_id and an airport date and returns the result.
    :param flight_id: unique id for the specific flight
    :param airport: iata code of the specific airport
    :return: result of the SQL query
    """

    table = 'departures'
    db, cur = db_create_cursor()

    stmt = f"SELECT * " \
           f"FROM {table} " \
           f"WHERE {CFG.key_dep_airport}={airport} AND {CFG.key_flight_id}={flight_id};"
    cur.execute(stmt)
    return cur.fetchall()


def db_select_event(flight_id, event_date):
    """
    This function creates a SQL query given a flight_id and an event date and returns the result.
    :param flight_id: unique id for the specific flight
    :param event_date: date of the event
    :return: result of the SQL query
    """

    table = 'events'
    db, cur = db_create_cursor()

    stmt = f"SELECT * " \
           f"FROM {table} " \
           f"WHERE {CFG.key_event_date}='{event_date}' AND {CFG.key_flight_id}='{flight_id}';"
    cur.execute(stmt)
    return cur.fetchall()


def main():
    # some test data
    flights_data = [({CFG.key_flight_number: '425', CFG.key_flight_status: 'On time | Scheduled',
                      CFG.key_dep_airport: 'TLV', CFG.key_arr_airport: 'ETM', CFG.key_dep_date: '12-Apr-2020',
                      CFG.key_arr_date: '12-Apr-2020', CFG.key_airline: '(6H) Israir Airlines'},
                     ['12 Apr', '05:23', 'Equipment Adjustment', '9 Apr', '20:04', 'Record Created', '9 Apr', '20:04',
                      'Time Adjustment']),
                    ({CFG.key_flight_number: '756', CFG.key_flight_status: 'On time | Scheduled',
                      CFG.key_dep_airport: 'TLV', CFG.key_arr_airport: 'HER', CFG.key_dep_date: '12-Apr-2020',
                      CFG.key_arr_date: '12-Apr-2020', CFG.key_airline: '(BBG) Blue Bird Airways'},
                     ['9 Apr', '20:07', 'Record Created', '9 Apr', '20:07', 'Time Adjustment']),
                    ({CFG.key_flight_number: '754', CFG.key_flight_status: 'On time | Scheduled',
                      CFG.key_dep_date: 'TLV', CFG.key_arr_airport: 'HER', CFG.key_dep_date: '12-Apr-2020',
                      CFG.key_arr_date: '12-Apr-2020', CFG.key_airline: '(BBG) Blue Bird Airways'},
                     ['9 Apr', '20:07', 'Record Created', '9 Apr', '20:07', 'Time Adjustment'])]

    # # feed into airport list:
    db_insert_airports()
    # feed data into
    db_feed_flights_data(flights_data)


if __name__ == '__main__':
    main()
