
import requests
from bs4 import BeautifulSoup
import re


SPECIFIC_FLIGHT_IDENTIFIER = "flightId"
FLIGHT_INFO_TAG = "flight-details"
FLIGHT_TRACK_TAG = "flight-tracker"

url = 'https://www.flightstats.com/v2/flight-tracker/departures/zrh'
SITE_BASIC_PATH = url.split("/v2")[0]

#url = 'https://www.flightstats.com/v2/flight-tracker/BA/709?year=2020&month=3&date=5&flightId=1033081792'
s = requests.session()
r = s.get(url)#, proxies = myProxy, headers = headers)
#print(r.content)

# Command from: https://www.dataquest.io/blog/web-scraping-tutorial-python/

page = requests.get(url)
#print(page)
#print(page.content)

soup = BeautifulSoup(page.content, 'html.parser')
#print(soup.prettify())


# select all the elements at the top level of the page
list(soup.children)

# Let’s see what the type of each element in the list is:
#[type(item) for item in list(soup.children)]

#We can now select the html tag and its children by taking the third item in the list:
html = list(soup.children)[1]

# Now, we can find the children inside the html tag:
# print(list(html.children))

# we want to extract the text of flights, so we’ll dive into the body, which is the second (out of 2) tags:
body = list(html.children)[1]

# Now, we can get the children of the body tag:
# list(body.children)

# There are 8 children:
#print(len(list(body.children)))

# This child contains the actual data:
#print(list(body.children)[3])

# This child contains the next page:
#print(list(body.children)[4])

# This child contains the error page:
#print(list(body.children)[6])

# We can now isolate the actual data page:
flights_data = list(body.children)[3]

#flights_data.children)

# The closes I got to flights data
#print(list(list(soup.children)[1].children)[1])

#print(list(list(soup.children)[1].children)[1].find_all('span', class_="table__SubText-s1x7nv9w-16 fRijCQ"))

# The table of flights:
list(list(soup.children)[1].children)[1].find_all('div', class_="table__TableContainer-s1x7nv9w-5 jfmExz")

list(list(soup.children)[1].children)[1].find_all('div', class_="table__Table-s1x7nv9w-6 iiiADv")



list(list(soup.children)[1].children)[1].find_all('h2')


# The number of pages!
list(soup.children)[1].find_all('span')

# header
list(soup.children)[1].find_all('h1')

# The flights!
list(soup.children)[1].find_all('h2')
list(soup.children)[1].select('h2')
flights = list(soup.children)[1].select('h2')
flights_list_Number_Departime_Arrivetime_Dest = [flight.get_text() for flight in flights]

# The actual flights!
flights_list = [flight.get_text() for flight in flights]

#print(flights_list)

# order the flights_list in 4 memebers unit list

#todo: 1. format as nested list, each list member contains all data on one flight
#todo: 2. implement the list of airports to the script, and an option to choose airports specifically
#todo: 3. adhere to the convesion, docstring
#todo: 4. use selenium package to autuomate pagniation
#todo: 5. get extra data from specific flight page
print("########################")
print("all the links of the page")
for link in soup.find_all('a'):
    print(link.get('href'))

print("########################")
print("get flights links (and ids)")
links = []
for link in list(soup.children)[1].find_all('a'):
        links.append(str(link.get('href')))
        print(str(link.get('href')))

print("########################")
print("flights links")

flight_links = []
for link in links:
    if re.findall(SPECIFIC_FLIGHT_IDENTIFIER, link):
        details_link = re.sub(FLIGHT_TRACK_TAG, FLIGHT_INFO_TAG, link)
        flight_links.append(str(SITE_BASIC_PATH) + str(details_link))
        print(str(SITE_BASIC_PATH) + str(details_link))

flights_html = []
flights_body = []
flights_body_detail_h4 = []
flight_historical_time_hours = []
flights_data = []
flights_data_lower_level = []
flights_data_even_lower_level = []
flights_all_strings = []
for link in flight_links:
    url = link
    s = requests.session()
    r = s.get(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    html = list(soup.children)[1]
    flights_html.append(html)
    body = list(html.children)[1]
    flights_body.append(body)
#    flights_body_detail_h4.append(list(flights_body[0]`.find_all('h4', class_="detail"))
#    flight_historical_time_hours.append(list(flights_body[0].find_all('span', class_="historical-flight-time-hours")))
    flights_data.append(body.get_text())  # one liner of all data on flight, including flight note
    flights_data_lower_level.append(list(body.children)[1].get_text())
    flights_data_even_lower_level.append(list(list(body.children)[1].children)[0])
    #flights_all_strings.append(list(body._all_strings()))  # just the strings
    #print(body.get_text().split("}"))  # the data splitted into fields (probably can ignore path and name

#todo:
airport_all_flights_data = []


#todo:
flight_details_list = []
flight_name = soup.find("h1").string
flight_status = soup.find("p").string
departure_airport = soup.find_all("h2")[1].string
arrival_airport = soup.find_all("h2")[3].string
departure_date = soup.find_all("p")[3].string
arrival_date = soup.find_all("p")[26].string
operating_airline = soup.find_all("p")[48].string
flight_details_list.append([flight_name, flight_status, departure_airport, arrival_airport, departure_date, arrival_date, operating_airline])

#todo:
flight_events_Date_Time_MSG = []
a = soup.find_all('p', class_='rowData')
string_before=""
time_iter = -1
for i, b in enumerate(a):
    if b.string is None:  # empty cell
        continue
    elif ":" in b.string:  # is time
        string_before = b.string
        time_iter += 1
        if time_iter % 3 == 0:  # is UTC time
            counter += 1
            flight_events_Date_Time_MSG.append(b.string)
        else:
            continue
    elif ":" in string_before:  # is event message
        string_before = b.string
        flight_events_Date_Time_MSG.append(b.string)
    elif len(b.string.split(" ")[1]) == 3:  # is date (len 3 is month short name)
        string_before = b.string
        flight_events_Date_Time_MSG.append(b.string)

# for flight in flights:
specific_airport_flights_data.append([flights_list_Number_Departime_Arrivetime_Dest[1:5], flight_details_list, flight_events_Date_Time_MSG])
