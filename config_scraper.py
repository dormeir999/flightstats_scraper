"""
CONFIGFILE: scraping

This config-file holds variables and magic numbers used by all database scripts -> db_*.py

Module: ITC - Data Mining
Project: Flight_Scraper
Authors: Itamar Bergfreund & Dor Meir

Last Updated: 19.04.2020
"""

# constant for testing
TESTING_AIRPORT = 'ATL'

# constants used for filtering iata codes
IATA_STR = 'iata_code'
TYPE_STR = 'airport_type'
FEET_STR = 'elevation_ft'
COUNTR_STR = 'iso_country'
CONTIN_STR = 'continent'
EMPTY_AIRPORTS_INT = 0
NO_AIRPORTS_MSG = "No airports were found..."

# constants used for main()
CONTINENTS_2DIGITS = ['OC', 'AF', 'EU', 'AS', 'SA', 'AN']
ISO_COUNTRIES_CODES = ['US', 'PR', 'MH', 'MP', 'GU', 'SO', 'AQ', 'GB', 'PG', 'AD', 'SD',
       'SA', 'AE', 'SS', 'ES', 'CN', 'AF', 'LK', 'SB', 'CO', 'AU', 'MG',
       'TD', 'AL', 'AM', 'MX', 'MZ', 'PW', 'NR', 'AO', 'AR', 'AS', 'AT',
       'GA', 'AZ', 'BA', 'BE', 'DE', 'BF', 'BG', 'GL', 'BH', 'BI', 'IS',
       'BJ', 'OM', 'XK', 'BM', 'KE', 'PH', 'BO', 'BR', 'BS', 'CV', 'BW',
       'FJ', 'BY', 'UA', 'LR', 'BZ', 'CA', 'CD', 'CF', 'CG', 'MR', 'CH',
       'CL', 'CM', 'CR', 'CU', 'CY', 'CZ', 'SK', 'PA', 'DZ', 'ID', 'GH',
       'RU', 'CI', 'DK', 'NG', 'DO', 'NE', 'HR', 'TN', 'TG', 'EC', 'EE',
       'FI', 'EG', 'GG', 'JE', 'IM', 'FK', 'EH', 'NL', 'IE', 'FO', 'LU',
       'NO', 'PL', 'ER', 'MN', 'PT', 'SE', 'ET', 'LV', 'LT', 'ZA', 'SZ',
       'GQ', 'SH', 'MU', 'IO', 'ZM', 'FM', 'KM', 'YT', 'RE', 'TF', 'ST',
       'FR', 'SC', 'ZW', 'MW', 'LS', 'ML', 'GM', 'GE', 'GF', 'SL', 'NF',
       'GW', 'MA', 'GN', 'SN', 'GR', 'GT', 'TZ', 'GY', 'SR', 'DJ', 'HK',
       'LY', 'HN', 'VN', 'KZ', 'RW', 'HT', 'HU', 'UG', 'TL', 'IL', 'IN',
       'IQ', 'IR', 'JP', 'IT', 'JM', 'JO', 'KG', 'BD', 'KI', 'KH', 'KP',
       'KR', 'KW', 'LA', 'MY', 'PM', 'SI', 'PS', 'MT', 'MC', 'RO', 'LI',
       'TR', 'MD', 'MK', 'GI', 'RS', 'ME', 'TC', 'GD', 'MM', 'NI', 'SV',
       'MF', 'MV', 'KY', 'NC', 'CK', 'TO', 'TV', 'NU', 'WF', 'NP', 'WS',
       'PF', 'VU', 'NZ', 'LB', 'PK', 'SY', 'QA', 'YE', 'UM', 'PE', 'TH',
       'PY', 'TW', 'SG', 'VI', 'SM', 'UY', 'VE', 'AG', 'BB', 'DM', 'GP',
       'MQ', 'BL', 'TJ', 'KN', 'LC', 'TM', 'AW', 'BQ', 'CW', 'SX', 'AI',
       'MS', 'TT', 'VG', 'VC', 'UZ', 'VA', 'MO', 'BT', 'BN', 'CC', 'CX']
PARSER_DESCRIB = """Insert the filename of airport details.
                    and other optional filters. If you want to add filters, add the
                    filter flag and than each parameter with space:
                    scrape_flightstats.py airport-codes.csv {-airport_type TYPE -country COUNTRY1 COUNTRY2 "-max-feet NUM -min-feet NUM}"""
AIRPORTS_TYPES = 'heliport', 'small_airport', 'closed', 'seaplane_base','balloonport', 'medium_airport', 'large_airport'
AIRPORTS_FILE_NAME = "airport-codes.csv"

# constants for scraping corona
CITIES_URL = "https://www.trackcorona.live/api/cities"
TRAVEL_URL = "https://www.trackcorona.live/api/travel"
PROVINCE_URL = "https://www.trackcorona.live/api/provinces"
COUNTRIES_URL = "https://www.trackcorona.live/api/countries"
COUNTRIES_NO_AIRPORTS = ['VA', 'SM', 'AX', 'NA', 'LI']
DATA_COLUMN_NAME = 'data'


# KEYS
KEY_iata_code = 'iata_code'
KEY_COORD = 'coordinates'
KEY_longitude = 'longitude'
KEY_latitude = 'latitude'


# constants used for html parsing
HTML_PARSER_STR = 'html.parser'
FLIGHT_TRACKER_STR = 'h2'
FLIGHT_NUMBER_STR = "h1"
FLIGHT_STAT_STR = "p"
AIRPORT_DEPT_STR = "h2"  # In a different context, it's also the flight tracker string (see above)
FLIGHTS_EVENTS_STR = 'rowData'
HTML_LINKS_STR1 = 'a'
HTML_LINKS_STR2 = 'href'
NO_FLIGHTS_MSG = 'No recent flights!'
AIRPORT_CODE_CLASS = "airportCodeTitle"
DATE_CLASS = "date"
FLIGHT_CARRIER_STRING = "h1"
FLIGHT_CARRIER_CLASS = "carrier-text-style"
FLIGHT_CARRIER_SPACE_STR = " "
FIRST_ITEM = 0
SECOND_ITEM = 1
THIRD_ITEM = 2
FOURTH_ITEM = 3
FLIGHT_NOT_IN_SYSTEM_STR = "h6"

# constants for flights web urls
SPECIFIC_FLIGHT_IDENTIFIER = "flightId"
FLIGHT_INFO_TAG = "flight-details"
FLIGHT_TRACK_TAG = "flight-tracker"
URL_SPLIT_STR = "/v2"
URL_FLIGHT_DEPT = 'https://www.flightstats.com/v2/flight-tracker/departures/'
DIVISOR_UTC = 3
MONTH_STRING_LENGTH = 3

