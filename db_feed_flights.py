"""
This file contains functions to feed in the flight data scraped

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


def db_insert_airports():
    """This function creates a table (airports) in the database flights_departures"""

    airports = get_airports()
    db, cur = db_create_cursor()
    # airports.drop(columns=['name'], inplace=True)

    query = """INSERT INTO airports (airport_type, name, elevation_ft, continent, iso_country, iso_region, 
            municipality, gps_code, iata_code, local_code, longitude, latitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    for index, airport in airports.iterrows():

        # if elevation is empty fill in None value
        if airport[CFG.elevation] == '':
            airport[CFG.elevation] = None
        airport.fillna(0, inplace=True)
        data = tuple(airport)[CFG.second_elem:]
        print(data)
        # catch error if there are duplicates in the data set
        try:
            cur.execute(query, data)
        except mysql.connector.errors.IntegrityError as err:
            print("Error caught while updating airport table: {}".format(err))
        # except mysql.connector.errors.DatabaseError as err:
        #     print("Error caught while updating airport table: {}".format(err))


    db.commit()


def db_insert_conversion_tables():
    """This fills airports and  in the database flights_departures"""

    airports = get_airports()
    db, cur = db_create_cursor()

    # city
    cities = airports['municipality'].dropna().unique()
    query = """INSERT INTO city_airports (municipality) VALUES (%s);"""

    for city in cities:
        # catch error if there are duplicates in the data set
        try:
            cur.execute(query, [city])
        except mysql.connector.errors.IntegrityError as err:
            print("Error caught while updating country_airports table: {}".format(err))


    # region
    regions = airports['iso_region'].dropna().unique()
    query = """INSERT INTO region_airports (iso_region) VALUES (%s);"""

    for region in regions:
        # catch error if there are duplicates in the data set
        try:
            cur.execute(query, [region])
        except mysql.connector.errors.IntegrityError as err:
            print("Error caught while updating region_airports table: {}".format(err))

    # country
    countries = airports['iso_country'].dropna().unique()
    query = """INSERT INTO country_airports (iso_country) VALUES (%s);"""

    for country in countries:
        # catch error if there are duplicates in the data set
        try:
            cur.execute(query, [country])
        except mysql.connector.errors.IntegrityError as err:
            print("Error caught while updating city_airport table: {}".format(err))

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

    dep_airport = flight_data[CFG.KEY_dep_airport]
    flight_id = flight_data[CFG.KEY_flight_id]
    flight_status = flight_data[CFG.KEY_flight_status]
    arrival_airport = flight_data[CFG.KEY_arr_airport]
    departure_date = flight_data[CFG.KEY_dep_date]
    arrival_date = flight_data[CFG.KEY_arr_date]
    operating_airline = flight_data[CFG.KEY_airline]
    flight_number = flight_data[CFG.KEY_flight_number]

    db, cur = db_create_cursor()

    # change airport_type of data from bs4.element.NavigableString to string
    for e in flight_data.keys():
        flight_data[e] = str(flight_data[e])

    # check if there is an entry for this data:
    is_observation = db_select_flight(dep_airport, flight_id)

    if is_observation:
        stmt = f"""UPDATE {table} SET 
               {CFG.KEY_flight_status} = '{flight_status}', 
               {CFG.KEY_dep_date} = '{departure_date}', 
               {CFG.KEY_arr_airport} = '{arrival_airport}',
               {CFG.KEY_arr_date} = '{arrival_date}', 
               {CFG.KEY_airline} = '{operating_airline}', 
               {CFG.KEY_flight_number} = {flight_number}
               WHERE {CFG.KEY_dep_airport}='{dep_airport}' AND {CFG.KEY_flight_id}='{flight_id}';"""
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

    # change airport_type of data from bs4.elemnt.NavigableString to string
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
                                                                          columns=f'{CFG.KEY_flight_id},'
                                                                                  f'{CFG.KEY_event_date},'
                                                                                  f'{CFG.KEY_event_time},'
                                                                                  f'{CFG.KEY_even_type}'
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

    flight_data[CFG.KEY_flight_id] = '_'.join([flight_data[CFG.KEY_airline], flight_data[CFG.KEY_flight_number],
                                               flight_data[CFG.KEY_dep_date]])

    # create date from string:
    flight_data[CFG.KEY_dep_date] = datetime.strptime(flight_data[CFG.KEY_dep_date], '%d-%b-%Y')
    flight_data[CFG.KEY_arr_date] = datetime.strptime(flight_data[CFG.KEY_arr_date], '%d-%b-%Y')

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

        # inserting flight data
        db_insert_flights(flight_data)

        # prepare events_data:
        for i in range(0, len(events_data), CFG.length_of_events):
            now = datetime.now()
            event_date = datetime.strptime(events_data[i] + '-' + str(now.year) + '-' + events_data[i + 1]
                                           , '%d %b-%Y-%H:%M')

            event_data = (flight_data[CFG.KEY_flight_id], event_date, events_data[i + CFG.second_elem],
                          events_data[i + CFG.third_elem])

            # inserting event_data
            db_insert_events(event_data)



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
           f"WHERE {CFG.KEY_dep_airport}='{airport}' AND {CFG.KEY_flight_id}='{flight_id}';"
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
           f"WHERE {CFG.KEY_event_date}='{event_date}' AND {CFG.KEY_flight_id}='{flight_id}';"
    cur.execute(stmt)
    return cur.fetchall()


def main():
    # some test data
    flights_data = [({CFG.KEY_flight_number: '425', CFG.KEY_flight_status: 'On time | Scheduled',
                      CFG.KEY_dep_airport: 'TLV', CFG.KEY_arr_airport: 'ETM', CFG.KEY_dep_date: '12-Apr-2020',
                      CFG.KEY_arr_date: '12-Apr-2020', CFG.KEY_airline: '(6H) Israir Airlines'},
                     ['12 Apr', '05:23', 'Equipment Adjustment', '9 Apr', '20:04', 'Record Created', '9 Apr', '20:04',
                      'Time Adjustment']),
                    ({CFG.KEY_flight_number: '756', CFG.KEY_flight_status: 'On time | Scheduled',
                      CFG.KEY_dep_airport: 'TLV', CFG.KEY_arr_airport: 'HER', CFG.KEY_dep_date: '12-Apr-2020',
                      CFG.KEY_arr_date: '12-Apr-2020', CFG.KEY_airline: '(BBG) Blue Bird Airways'},
                     ['9 Apr', '20:07', 'Record Created', '9 Apr', '20:07', 'Time Adjustment']),
                    ({CFG.KEY_flight_number: '754', CFG.KEY_flight_status: 'On time | Scheduled',
                      CFG.KEY_dep_airport: 'TLV', CFG.KEY_arr_airport: 'HER', CFG.KEY_dep_date: '12-Apr-2020',
                      CFG.KEY_arr_date: '12-Apr-2020', CFG.KEY_airline: '(BBG) Blue Bird Airways'},
                     ['9 Apr', '20:07', 'Record Created', '9 Apr', '20:07', 'Time Adjustment'])]

    # # feed into airport list:
    # # feed data into
    # db_feed_flights_data(flights_data)
    db_insert_conversion_tables()
    db_insert_airports()

if __name__ == '__main__':
    main()
