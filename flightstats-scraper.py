
import requests
from bs4 import BeautifulSoup
<<<<<<<<< Temporary merge branch 1
import re

SPECIFIC_FLIGHT_IDENTIFIER = "flightId"
FLIGHT_INFO_TAG = "flight-details"
FLIGHT_TRACK_TAG = "flight-tracker"
URL_SPLIT_STRING = "/v2"
URL_FLIGHT_DEPT = 'https://www.flightstats.com/v2/flight-tracker/departures/'
list_of_airports = ['zrh','tlv']
HTML_PARSER_STRING = 'html.parser'
FLIGHT_TRACKER_STRING = 'h2'
FLIGHT_NAME_STRING = "h1"
FLIGHT_STAT_STRING = "p"
AIRPORT_DEPT_STRING = "h2"
FLIGHTS_EVENTS_STRING = 'rowData'
FLIGHT_LINK_STRING = 'a'
LINK_STRING = 'href'

url = str(URL_FLIGHT_DEPT) + str(list_of_airports[0])
SITE_BASIC_PATH = url.split(URL_SPLIT_STRING)[0]
=========
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

elm = driver.find_element_by_class_name('cKpakR')
elm.click()

from selenium import webdriver


# options = webdriver.ChromeOptions()
# options.add_argument('--ignore-certificate-errors')
# options.add_argument("--test-type")
# options.binary_location = "/usr/bin/chromium"
driver = webdriver.Chrome(chrome_options=options)
driver.get(url)

html = driver.page_source
print(html)


url = 'https://www.flightstats.com/v2/flight-tracker/departures/zrh'
#url = 'https://www.flightstats.com/v2/flight-tracker/BA/709?year=2020&month=3&date=5&flightId=1033081792'
>>>>>>>>> Temporary merge branch 2
s = requests.session()
r = s.get(url)
page = requests.get(url)
soup = BeautifulSoup(page.content, HTML_PARSER_STRING)
flights = list(soup.children)[1].select(FLIGHT_TRACKER_STRING)

flights_list_Number_Departime_Arrivetime_Dest = []
for flight in flights:
    flights_list_Number_Departime_Arrivetime_Dest.append(flight.get_text())

print("get flights links (and ids):")
links = []
flight_links = []
for link in list(soup.children)[1].find_all(FLIGHT_LINK_STRING):
        links.append(str(link.get(LINK_STRING)))
        print(str(link.get(LINK_STRING)))



for link in links:
    if re.findall(SPECIFIC_FLIGHT_IDENTIFIER, link):
        details_link = re.sub(FLIGHT_TRACK_TAG, FLIGHT_INFO_TAG, link)
        flight_links.append(str(SITE_BASIC_PATH) + str(details_link))
        print(str(SITE_BASIC_PATH) + str(details_link))

for link in flight_links:
    url = link
    s = requests.session()
    r = s.get(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, HTML_PARSER_STRING)
    flight_details_list = []
    flight_name = soup.find(FLIGHT_NAME_STRING).string
    flight_status = soup.find(FLIGHT_STAT_STRING).string
    departure_airport = soup.find_all(AIRPORT_DEPT_STRING)[1].string
    arrival_airport = soup.find_all(AIRPORT_DEPT_STRING)[3].string
    departure_date = soup.find_all(FLIGHT_STAT_STRING)[3].string
    arrival_date = soup.find_all(FLIGHT_STAT_STRING)[26].string
    operating_airline = soup.find_all(FLIGHT_STAT_STRING)[48].string
    flight_details_list.append([flight_name, flight_status, departure_airport, arrival_airport, departure_date, arrival_date, operating_airline])

    flight_events_Date_Time_MSG = []
    a = soup.find_all(FLIGHT_STAT_STRING, class_=FLIGHTS_EVENTS_STRING)
    string_before = ""
    time_iter = -1
    for i, b in enumerate(a):
        if b.string is None:  # empty cell
            continue
        elif ":" in b.string:  # is time
            string_before = b.string
            time_iter += 1
            if time_iter % 3 == 0:  # is UTC time
                flight_events_Date_Time_MSG.append(b.string)
            else:
                continue
        elif ":" in string_before:  # is event message
            string_before = b.string
            flight_events_Date_Time_MSG.append(b.string)
        elif len(b.string.split(" ")[1]) == 3:  # is date (len 3 is month short name)
            string_before = b.string
            flight_events_Date_Time_MSG.append(b.string)

    specific_airport_flights_data = []
    for i, flight in enumerate(flight_details_list):
        specific_airport_flights_data.append([flights_list_Number_Departime_Arrivetime_Dest[i], flight_details_list[i], flight_events_Date_Time_MSG])
        print(specific_airport_flights_data[i])




