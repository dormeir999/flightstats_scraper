import mysql.connector
from list_airport_codes import get_airports
from datetime import datetime
from db_init import db_create_cursor
import config_db as CFG


def db_insert_airport():
    """This function creates a table (airports) in the database flights_departures"""

    airports = get_airports()
    db, cur = db_create_cursor()

    for index, airport in airports.iterrows():
        # if elevation is empty fill in None value
        if airport[CFG.elevation] == '':
            airport[CFG.elevation] = None
        airport.fillna(0, inplace=True)
        data = tuple(airport)[CFG.second_elem:]
        print(data)
        airport['name'] = airport['name'].replace('\"', '\'')
        query = f"""INSERT INTO airport (airport_type, name, elevation_ft, continent, iso_country, iso_region, 
                    municipality, gps_code, iata_code, local_code, longitude, latitude)
                    VALUES ("{airport['type']}", "{airport['name']}", '{int(airport['elevation_ft'])}', 
                    "{airport['continent']}", '{airport['iso_country']}', '{airport['iso_region']}', 
                    "{airport['municipality']}", '{airport['gps_code']}', '{airport['iata_code']}', 
                    '{airport['local_code']}', '{airport['longitude']}','{airport['latitude']}');"""

        # catch error if there are duplicates in the data set
        try:
            cur.execute(query)
        except mysql.connector.errors.IntegrityError as err:
            print("Error caught while updating airport table: {}".format(err))

    db.commit()


def main():
    db_insert_airport()

if __name__ == '__main__':
    main()
