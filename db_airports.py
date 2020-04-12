"""
This creates a database to fill in the data scraped

Authors: Itamar Bergfreund & Dor Meir
"""

import mysql.connector
from list_airport_codes import create_list_of_airports
from datetime import datetime


# for config file
host = "localhost"
user = "root"
passwd = 'flightscraper'
database='flight_departures'
logfile = 'fs_log.log'
key_dep_date = 'departure_date'
key_arr_date = 'arrival_date'
key_airline = 'operating_airline'
key_flight_number = 'flight_number'
key_flight_id = 'flight_id'
length_of_events = 3
first_elem = 0
second_elem = 1
third_elem = 2
iata_code = 9
coordinates = 11
elevation = 3


def db_create_cursor():
    """creates connection with database and creates a cursor
    :return db, cur
    """

    db = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=database)

    cur = db.cursor()
    return db, cur


def db_insert_airports(filename='airport-codes.csv'):
    """This function creates a table (airports) in the database flights_departures"""

    airports = create_list_of_airports(filename)
    db, cur = db_create_cursor()

    query_create = "INSERT INTO airports (type, name, elevation_ft, continent, iso_country, iso_region, " \
                   "municipality, gps_code, iata_code, local_code, longitude, latitude) " \
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    for x, airport in enumerate(airports[second_elem:]):

        # if elevation is empty fill in None value
        if airport[elevation] == '':
            airport[elevation] = None

        # if iata-code is empty fill skip
        if airport[iata_code] != '' and airport[iata_code] != '0':
            data = (tuple(airport[second_elem:coordinates]) + tuple(airport[coordinates].split(', ')))

            # catch error if there are duplicates in the data set
            try:
                cur.execute(query_create, data)
            except mysql.connector.errors.IntegrityError as err:
                print("Error caught while updating airport table: {}".format(err))

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
    dep_airport = flight_data['departure_airport']
    flight_id = flight_data['flight_id']
    flight_status = flight_data['flight_status']
    arrival_airport = flight_data['arrival_airport']
    departure_date = flight_data['departure_date']
    arrival_date = flight_data['arrival_date']
    operating_airline = flight_data['operating_airline']
    flight_number = flight_data['flight_number']

    db, cur = db_create_cursor()

    # change type of data from bs4.elemnt.NavigableString to string
    for e in flight_data.keys():
        flight_data[e] = str(flight_data[e])

    # check if there is an entry for this data:
    is_observation = db_select_flight(dep_airport, flight_id)

    if is_observation:
        stmt = f"UPDATE {table} SET " \
               f"flight_status = '{flight_status}', " \
               f"departure_date = '{departure_date}', " \
               f"arrival_airport = '{arrival_airport}', " \
               f"arrival_date = '{arrival_date}', " \
               f"operating_airline = '{operating_airline}', " \
               f"flight_number = '{flight_number}' " \
               f"WHERE " \
               f"departure_airport='{dep_airport}' AND flight_id='{flight_id}';"
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

    length = len(events_data)

    # change type of data from bs4.elemnt.NavigableString to string
    events_data = tuple([str(e) for e in events_data])

    db, cur = db_create_cursor()
    table = 'events'
    placeholder = ", ".join(["%s"] * length)
    smt = "INSERT INTO {table} ({columns}) values ({values});".format(table=table,
                                                                      columns='flight_id, event_date, event_time'
                                                                              ', event_type',
                                                                      values=placeholder)

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

    flight_data[key_flight_id] = '_'.join([flight_data[key_airline], flight_data[key_flight_number],
                                           flight_data[key_dep_date]])

    # create date from string:
    flight_data[key_dep_date] = datetime.strptime(flight_data[key_dep_date], '%d-%b-%Y')
    flight_data[key_arr_date] = datetime.strptime(flight_data[key_arr_date], '%d-%b-%Y')

    return flight_data


def db_feed_flights_data(flights_data):
    """This function takes the data scraped per airport and loops over every flight in the data"""

    for flight_data in flights_data:
        events_data = flight_data[second_elem]
        flight_data = flight_data[first_elem]
        flight_data = create_flight_id(flight_data)

        # prepare events_data:
        for i in range(0, len(events_data), length_of_events):
            now = datetime.now()
            event_date = datetime.strptime(events_data[i] + '-' + str(now.year) + '-'+ events_data[i+1] , '%d %b-%Y-%H:%M')

            # todo remove 0 (event time) adjust in db structure
            event_data = (flight_data[key_flight_id] , event_date, 0, events_data[i + third_elem])

            # inserting event_data
            db_insert_events(event_data)

        # inserting flight data
        db_insert_flights(flight_data)


def db_select_flight(airport, flight_id):

    table = 'departures'
    db, cur = db_create_cursor()

    stmt = f"SELECT * " \
           f"FROM {table} " \
           f"WHERE departure_airport='{airport}' AND flight_id='{flight_id}';"
    cur.execute(stmt)
    return cur.fetchall()


def main():

    flights_data = [({'flight_number': '425', 'flight_status': 'On time | Scheduled', 'departure_airport': 'TLV',
                      'arrival_airport': 'ETM', 'departure_date': '12-Apr-2020', 'arrival_date': '12-Apr-2020',
                      'operating_airline': '(6H) Israir Airlines'},
                     ['12 Apr', '05:23', 'Equipment Adjustment', '9 Apr', '20:04', 'Record Created', '9 Apr', '20:04',
                      'Time Adjustment']),

                    ({'flight_number': '756', 'flight_status': 'On time | Scheduled', 'departure_airport': 'TLV',
                      'arrival_airport': 'HER', 'departure_date': '12-Apr-2020', 'arrival_date': '12-Apr-2020',
                      'operating_airline': '(BBG) Blue Bird Airways'},
                     ['9 Apr', '20:07', 'Record Created', '9 Apr', '20:07', 'Time Adjustment']), ({'flight_number': '754', 'flight_status': 'On time | Scheduled', 'departure_airport': 'TLV', 'arrival_airport': 'HER', 'departure_date': '12-Apr-2020', 'arrival_date': '12-Apr-2020', 'operating_airline': '(BBG) Blue Bird Airways'}, ['9 Apr', '20:07', 'Record Created', '9 Apr', '20:07', 'Time Adjustment']), ({'flight_number': '23', 'flight_status': 'Arrived', 'departure_airport': 'TLV', 'arrival_airport': 'DTW', 'departure_date': '12-Apr-2020', 'arrival_date': '12-Apr-2020', 'operating_airline': '(LY) El Al'}, ['12 Apr', '18:15', 'Time Adjustment', '12 Apr', '18:04', 'Time Adjustment', '12 Apr', '18:02', 'Status Landed', '12 Apr', '17:58', 'Time Adjustment', '12 Apr', '17:53', 'Time Adjustment', '12 Apr', '17:51', 'Time Adjustment', '12 Apr', '17:51', 'Time Adjustment', '12 Apr', '17:49', 'Time Adjustment', '12 Apr', '17:48', 'Time Adjustment', '12 Apr', '17:47', 'Time Adjustment', '12 Apr', '17:45', 'Time Adjustment', '12 Apr', '17:44', 'Time Adjustment', '12 Apr', '17:42', 'Time Adjustment', '12 Apr', '17:38', 'Time Adjustment', '12 Apr', '17:35', 'Time Adjustment', '12 Apr', '17:03', 'Time Adjustment', '12 Apr', '16:35', 'Time Adjustment', '12 Apr', '13:32', 'Time Adjustment', '12 Apr', '11:59', 'Time Adjustment', '12 Apr', '06:14', 'Time Adjustment', '12 Apr', '06:14', 'Record Created']), ({'flight_number': '692', 'flight_status': 'On time | Scheduled', 'departure_airport': 'TLV', 'arrival_airport': 'RHO', 'departure_date': '12-Apr-2020', 'arrival_date': '12-Apr-2020', 'operating_airline': '(BBG) Blue Bird Airways'}, ['9 Apr', '20:07', 'Record Created', '9 Apr', '20:07', 'Time Adjustment']), ({'flight_number': '752', 'flight_status': 'On time | Scheduled', 'departure_airport': 'TLV', 'arrival_airport': 'HER', 'departure_date': '12-Apr-2020', 'arrival_date': '12-Apr-2020', 'operating_airline': '(BBG) Blue Bird Airways'}, ['9 Apr', '20:07', 'Record Created', '9 Apr', '20:07', 'Time Adjustment']), ({'flight_number': '697', 'flight_status': 'On time | Scheduled', 'departure_airport': 'TLV', 'arrival_airport': 'BUS', 'departure_date': '12-Apr-2020', 'arrival_date': '12-Apr-2020', 'operating_airline': '(A9) Georgian Airways'}, ['9 Apr', '20:05', 'Record Created', '9 Apr', '20:05', 'Time Adjustment']), ({'flight_number': '322', 'flight_status': 'On time | Scheduled', 'departure_airport': 'TLV', 'arrival_airport': 'GYD', 'departure_date': '12-Apr-2020', 'arrival_date': '12-Apr-2020', 'operating_airline': '(J2) AZAL Azerbaijan Airlines'}, ['9 Apr', '20:11', 'Record Created', '9 Apr', '20:11', 'Time Adjustment']), ({'flight_number': '91', 'flight_status': 'Delayed by 1h 1m | Departed', 'departure_airport': 'TLV', 'arrival_airport': 'EWR', 'departure_date': '12-Apr-2020', 'arrival_date': '12-Apr-2020', 'operating_airline': '(UA) United Airlines'}, ['12 Apr', '18:40', 'Time Adjustment', '12 Apr', '17:21', 'Time Adjustment', '12 Apr', '16:43', 'Time Adjustment', '12 Apr', '16:03', 'Time Adjustment', '12 Apr', '10:38', 'Time Adjustment', '12 Apr', '10:27', 'Time Adjustment', '12 Apr', '10:12', 'Status Active', '12 Apr', '06:03', 'Gate Adjustment', '12 Apr', '01:31', 'Time Adjustment', '11 Apr', '20:26', 'Time Adjustment', '11 Apr', '08:04', 'Gate Adjustment', '10 Apr', '05:15', 'Time Adjustment', '9 Apr', '20:16', 'Time Adjustment', '9 Apr', '20:16', 'Record Created'])]    # # initialize databse:


    # # feed into airport list:
    # db_insert_airports()
    # feed data into
    db_feed_flights_data(flights_data)


if __name__ == '__main__':
    main()
