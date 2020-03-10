
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
flights_list = [flight.get_text() for flight in flights]

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

flights_data = []
flights_all_strings = []
for link in flight_links:
    url = link
    s = requests.session()
    r = s.get(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    html = list(soup.children)[1]
    body = list(html.children)[1]
    flights_data.append(body.get_text())  # one liner of all data on flight, including flight note
    #flights_all_strings.append(list(body._all_strings()))  # just the strings
    #print(body.get_text().split("}"))  # the data splitted into fields (probably can ignore path and name
