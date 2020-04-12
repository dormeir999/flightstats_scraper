"""
This creates a database to fill in the data scraped

Authors: Itamar Bergfreund & Dor Meir
"""

import mysql.connector
from list_airport_codes import create_list_of_airports

# for config file
host="localhost"
user="root"
passwd='flightscraper'
database='flight_departures'
logfile = 'fs_log.log'


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

    for x, airport in enumerate(airports[1:]):

        # if elevation is empty fill in None value
        if airport[3] == '':
            airport[3] = None

        # if iata-code is empty fill skip
        if airport[9] != '' and airport[9] != '0':
            data = (tuple(airport[1:11]) + tuple(airport[11].split(', ')))

            # catch error if there are duplicates in the data set
            try:
                cur.execute(query_create, data)
            except mysql.connector.errors.IntegrityError as err:
                print("Error caught while updating airport table: {}".format(err))

    db.commit()


def db_insert_flights(flight_data):
    """This function takes the a flight data dictionary as an input and feeds it into the database table departures.
    :param flight_data: e.g.
                        {'flight_status': 'On time | Arrived',
                        'departure_airport': 'GVA',
                        'arrival_airport': 'AMS',
                        'departure_date': '10-Apr-2020',
                        'arrival_date': '10-Apr-2020',
                        'operating_airline': 'Operated by KLM 1928',
                        'airline': 'Xiamen Airlines',
                        'flight_number': '9600',
                        'flight_id': 'Xiamen Airlines_9600_10-Apr-2020'}"""

    table = 'departures'
    db, cur = db_create_cursor()

    # change type of data from bs4.elemnt.NavigableString to string
    for e in flight_data.keys():
        flight_data[e] = str(flight_data[e])

    placeholder = ", ".join(["%s"] * len(flight_data))
    stmt = "INSERT INTO {table} ({columns}) VALUES ({values});".format(table=table,
                                                                       columns=",".join(flight_data.keys()),
                                                                       values=placeholder)
    try:
        cur.execute(stmt, list(flight_data.values()))

    except mysql.connector.errors.IntegrityError as err:
        print("Error caught while updating flights table: {}".format(err))
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
                                                                        columns='flight_id, event_date, event_time, '
                                                                                'event_type',
                                                                        values=placeholder)

    try:
        cur.execute(smt, events_data)

    except mysql.connector.errors.IntegrityError as err:
        print("Error while inserting events data: {}".format(err))

    db.commit()


def flight_data_prepare(flight_data):

    key_airline = 'airline'
    key_flight_number = 'flight_number'
    key_flight_name = 'flight_name'
    key_flight_id = 'flight_id'

    # todo: split data while handling data
    temp = list(flight_data.values())[0].split(' ')
    if len(temp) == 5:
        al_min = 1
        al_max = 2
    elif len(temp) == 6:
        al_min = 1
        al_max = 3
    elif len(temp) == 7:
        al_min = 1
        al_max = 4

    flight_data[key_airline] = ' '.join(temp[al_min:al_max])
    flight_data[key_flight_number] = temp[-3]
    flight_data[key_flight_id] = '_'.join([flight_data['airline'], flight_data['flight_number'], flight_data['departure_date']])
    del flight_data[key_flight_name]
    return flight_data


def db_feed_flights_data(flights_data):
    """This function takes the data scraped per airport and loops over every flight in the data"""

    for flight_data in flights_data:
        events_data = flight_data[1]
        flight_data = flight_data[0]
        flight_data = flight_data_prepare(flight_data)

        # prepare events_data:
        for i in range(0, len(events_data), 3):
            event_data = ('_'.join([flight_data['airline'], flight_data['flight_number'],
                                    flight_data['departure_date']]), events_data[i], events_data[i + 1],
                          events_data[i + 2])

        db_insert_events(event_data)
        db_insert_flights(flight_data)


def main():

    flights_data = [({'flight_name': '(5C) C.A.L. Cargo Airlines 971 Flight Details', 'flight_status': 'Arrived', 'departure_airport': 'TLV', 'arrival_airport': 'LGG', 'departure_date': '10-Apr-2020', 'arrival_date': ' ', 'operating_airline': '08:39'}, ['11 Apr', '08:39', 'Status Landed', '11 Apr', '08:32', 'Time Adjustment', '11 Apr', '08:29', 'Time Adjustment', '11 Apr', '07:59', 'Time Adjustment', '11 Apr', '07:14', 'Time Adjustment', '11 Apr', '04:49', 'Time Adjustment', '11 Apr', '04:40', 'Status Active', '7 Apr', '20:04', 'Record Created', '7 Apr', '20:04', 'Time Adjustment']), ({'flight_name': '(UA) United Airlines 2770 Flight Details', 'flight_status': 'Delayed by 14h 39m | Departed', 'departure_airport': 'TLV', 'arrival_airport': 'SFO', 'departure_date': '11-Apr-2020', 'arrival_date': 'San Francisco International Airport, CA, US', 'operating_airline': 'Tail Number'}, ['11 Apr', '13:16', 'Time Adjustment', '11 Apr', '13:16', 'Time Adjustment', '11 Apr', '12:57', 'Time Adjustment', '11 Apr', '12:57', 'Status Active', '11 Apr', '06:07', 'Gate Adjustment', '11 Apr', '06:00', 'Gate Adjustment', '11 Apr', '03:13', 'Time Adjustment', '10 Apr', '03:11', 'Time Adjustment', '9 Apr', '21:56', 'Time Adjustment', '8 Apr', '20:15', 'Time Adjustment', '8 Apr', '20:15', 'Record Created']), ({'flight_name': '(BBG) Blue Bird Airways 754 Flight Details', 'flight_status': 'On time | Scheduled', 'departure_airport': 'TLV', 'arrival_airport': 'HER', 'departure_date': '11-Apr-2020', 'arrival_date': 'Actual', 'operating_airline': 'Record Created'}, ['8 Apr', '20:07', 'Record Created', '8 Apr', '20:07', 'Time Adjustment']), ({'flight_name': '(BBG) Blue Bird Airways 692 Flight Details', 'flight_status': 'On time | Scheduled', 'departure_airport': 'TLV', 'arrival_airport': 'RHO', 'departure_date': '11-Apr-2020', 'arrival_date': 'Actual', 'operating_airline': 'Record Created'}, ['8 Apr', '20:07', 'Record Created', '8 Apr', '20:07', 'Time Adjustment']), ({'flight_name': '(BBG) Blue Bird Airways 752 Flight Details', 'flight_status': 'On time | Scheduled', 'departure_airport': 'TLV', 'arrival_airport': 'HER', 'departure_date': '11-Apr-2020', 'arrival_date': 'Actual', 'operating_airline': 'Record Created'}, ['8 Apr', '20:07', 'Record Created', '8 Apr', '20:07', 'Time Adjustment']), ({'flight_name': '(A9) Georgian Airways 696 Flight Details', 'flight_status': 'On time | Scheduled', 'departure_airport': 'TLV', 'arrival_airport': 'TBS', 'departure_date': '11-Apr-2020', 'arrival_date': 'Actual', 'operating_airline': 'Record Created'}, ['8 Apr', '20:04', 'Record Created', '8 Apr', '20:04', 'Time Adjustment']), ({'flight_name': '(UA) United Airlines 91 Flight Details', 'flight_status': 'Delayed by 37m | Departed', 'departure_airport': 'TLV', 'arrival_airport': 'EWR', 'departure_date': '11-Apr-2020', 'arrival_date': 'Newark Liberty International Airport, NJ, US', 'operating_airline': 'Tail Number'}, ['11 Apr', '20:23', 'Time Adjustment', '11 Apr', '19:46', 'Time Adjustment', '11 Apr', '19:29', 'Time Adjustment', '11 Apr', '19:08', 'Time Adjustment', '11 Apr', '18:17', 'Time Adjustment', '11 Apr', '15:35', 'Time Adjustment', '11 Apr', '13:22', 'Time Adjustment', '11 Apr', '09:56', 'Time Adjustment', '11 Apr', '09:46', 'Time Adjustment', '11 Apr', '08:44', 'Status Active', '10 Apr', '22:06', 'Gate Adjustment', '10 Apr', '20:51', 'Gate Adjustment', '10 Apr', '20:26', 'Time Adjustment', '9 Apr', '12:04', 'Equipment Adjustment', '9 Apr', '05:15', 'Time Adjustment', '8 Apr', '20:15', 'Time Adjustment', '8 Apr', '20:15', 'Record Created'])]
    # # initialize databse:
    create_database()

    # # create Tables:
    create_tables()

    # # feed into airport list:
    # db_airports()
    # feed data into
    db_feed_flights_data(flights_data)


if __name__ == '__main__':
    main()
